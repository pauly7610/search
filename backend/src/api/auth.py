"""
Authentication API Router for AgentAuth Integration

Compatible with FastAPI 0.115.0 and python-multipart==0.0.12
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from src.middleware.auth_middleware import auth_middleware, get_current_user, get_current_user_optional
from src.config.agent_auth import agent_auth_manager, agent_auth_settings
from src.models.auth_models import UserCreate, UserLogin, ConnectionRequest

logger = logging.getLogger(__name__)

# FastAPI 0.115.0 compatible router
router = APIRouter()

class AuthResponse(BaseModel):
    """Response model for authentication operations compatible with Pydantic 2.10.2."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    
    class Config:
        from_attributes = True

class ConnectionResponse(BaseModel):
    """Response model for AgentAuth connection operations compatible with Pydantic 2.10.2."""
    connection_id: str
    auth_url: str
    app: str
    status: str
    
    class Config:
        from_attributes = True

# In-memory user store for demo (replace with database in production)
DEMO_USERS = {
    "demo@xfinity.com": {
        "id": "demo-user-1",
        "email": "demo@xfinity.com",
        "name": "Demo User",
        "hashed_password": auth_middleware.hash_password("demo123"),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate):
    """
    Register a new user account compatible with FastAPI 0.115.0.
    
    Creates a new user account with email and password, then generates
    an access token for immediate authentication.
    """
    try:
        # Check if user already exists
        if user_data.email in DEMO_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = auth_middleware.hash_password(user_data.password)
        
        DEMO_USERS[user_data.email] = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Generate access token
        access_token = auth_middleware.create_access_token(
            data={
                "user_id": user_id,
                "email": user_data.email,
                "name": user_data.name
            }
        )
        
        logger.info(f"New user registered: {user_data.email}")
        
        return AuthResponse(
            access_token=access_token,
            expires_in=agent_auth_settings.jwt_access_token_expire_minutes * 60,
            user={
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name,
                "connections": []
            }
        )
        
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(user_credentials: UserLogin):
    """
    Authenticate user and return access token compatible with FastAPI 0.115.0.
    
    Validates user credentials and returns JWT token for API access
    along with user's AgentAuth connections.
    """
    try:
        # Find user
        user = DEMO_USERS.get(user_credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_middleware.verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user's AgentAuth connections
        connections = await agent_auth_manager.get_user_connections(user["id"])
        
        # Generate access token
        access_token = auth_middleware.create_access_token(
            data={
                "user_id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        )
        
        logger.info(f"User logged in: {user_credentials.email}")
        
        return AuthResponse(
            access_token=access_token,
            expires_in=agent_auth_settings.jwt_access_token_expire_minutes * 60,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "connections": connections
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {user_credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information compatible with FastAPI 0.115.0.
    
    Returns user details and their current AgentAuth connections.
    """
    return {
        "user": current_user,
        "authenticated": True,
        "agent_auth_enabled": agent_auth_settings.agent_auth_enabled
    }

@router.post("/connect/{app_name}", response_model=ConnectionResponse)
async def initiate_app_connection(
    app_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Initiate OAuth2 connection to external app compatible with FastAPI 0.115.0.
    
    Generates authorization URL for connecting user's account to
    external services like GitHub, Gmail, Slack, etc.
    """
    try:
        if app_name not in agent_auth_settings.supported_apps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"App '{app_name}' is not supported"
            )
        
        # Generate auth URL through AgentAuth
        auth_data = await agent_auth_manager.get_auth_url(app_name, current_user["user_id"])
        
        logger.info(f"Auth URL generated for {current_user['email']} -> {app_name}")
        
        return ConnectionResponse(
            connection_id=auth_data["connection_id"],
            auth_url=auth_data["auth_url"],
            app=app_name,
            status="pending"
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate connection for {app_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate connection to {app_name}"
        )

@router.get("/auth/callback")
async def oauth_callback(
    request: Request,
    connection_id: Optional[str] = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Handle OAuth2 callback from external services compatible with FastAPI 0.115.0.
    
    Processes the callback from OAuth2 providers and completes
    the connection setup in AgentAuth.
    """
    try:
        if not connection_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing connection_id parameter"
            )
        
        if not current_user:
            # Redirect to login if no current user
            return RedirectResponse(
                url=f"/login?redirect=/auth/callback?connection_id={connection_id}",
                status_code=status.HTTP_302_FOUND
            )
        
        # Verify connection completion
        connection_status = await agent_auth_manager.verify_connection(
            connection_id, current_user["user_id"]
        )
        
        if connection_status["status"] == "connected":
            logger.info(f"Connection completed for {current_user['email']} -> {connection_status['app']}")
            return RedirectResponse(
                url=f"/dashboard?connected={connection_status['app']}",
                status_code=status.HTTP_302_FOUND
            )
        else:
            logger.warning(f"Connection failed for {current_user['email']}: {connection_status}")
            return RedirectResponse(
                url=f"/dashboard?error=connection_failed",
                status_code=status.HTTP_302_FOUND
            )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url="/dashboard?error=callback_failed",
            status_code=status.HTTP_302_FOUND
        )

@router.get("/connections")
async def get_user_connections(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get all connected apps for the current user compatible with FastAPI 0.115.0.
    
    Returns list of all active AgentAuth connections.
    """
    try:
        connections = await agent_auth_manager.get_user_connections(current_user["user_id"])
        
        return {
            "connections": connections,
            "total": len(connections),
            "supported_apps": agent_auth_settings.supported_apps
        }
        
    except Exception as e:
        logger.error(f"Failed to get connections for {current_user['email']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve connections"
        )

@router.post("/execute/{app_name}/{action}")
async def execute_agent_action(
    app_name: str,
    action: str,
    parameters: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Execute authenticated action through connected app compatible with FastAPI 0.115.0.
    
    Performs actions on external services using the user's
    authenticated AgentAuth connections.
    """
    try:
        # Check if user has connection to the app
        connections = await agent_auth_manager.get_user_connections(current_user["user_id"])
        app_connected = any(conn["app"] == app_name and conn["status"] == "connected" for conn in connections)
        
        if not app_connected:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User not connected to {app_name}"
            )
        
        # Execute action through AgentAuth
        result = await agent_auth_manager.execute_agent_action(
            current_user["user_id"], app_name, action, parameters
        )
        
        logger.info(f"Action executed: {action} on {app_name} for {current_user['email']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute action {action} on {app_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute action on {app_name}"
        )

@router.get("/supported-apps")
async def get_supported_apps():
    """
    Get list of supported apps for AgentAuth connections compatible with FastAPI 0.115.0.
    
    Returns all available apps that users can connect to.
    """
    return {
        "supported_apps": agent_auth_settings.supported_apps,
        "total": len(agent_auth_settings.supported_apps),
        "agent_auth_enabled": agent_auth_settings.agent_auth_enabled
    } 