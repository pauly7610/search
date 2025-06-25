"""
Authentication Middleware for AgentAuth Integration

Compatible with FastAPI 0.115.0 and Pydantic 2.10.2
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from src.config.agent_auth import agent_auth_settings, agent_auth_manager
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing compatible with passlib[bcrypt]==1.7.4
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme compatible with FastAPI 0.115.0
token_scheme = HTTPBearer()

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class AgentAuthMiddleware:
    """
    Middleware for handling AgentAuth authentication and authorization.
    Compatible with FastAPI 0.115.0 and pydantic 2.10.2.
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY  # Use existing SECRET_KEY from main settings
        self.algorithm = agent_auth_settings.jwt_algorithm
        self.access_token_expire_minutes = agent_auth_settings.jwt_access_token_expire_minutes
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token for user authentication.
        Compatible with python-jose[cryptography]==3.3.0.
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise AuthenticationError("Failed to create access token")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        Compatible with python-jose[cryptography]==3.3.0.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationError("Token has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise AuthenticationError("Token verification failed")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """
        Get current user from JWT token.
        Compatible with FastAPI 0.115.0 dependency injection.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            User information from token payload
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            payload = self.verify_token(credentials.credentials)
            user_id = payload.get("user_id")
            
            if not user_id:
                raise AuthenticationError("Invalid token payload")
            
            # Get user's AgentAuth connections
            connections = await agent_auth_manager.get_user_connections(user_id)
            
            return {
                "user_id": user_id,
                "email": payload.get("email"),
                "name": payload.get("name"),
                "connections": connections,
                "is_authenticated": True
            }
            
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password for storage using passlib[bcrypt]==1.7.4."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using passlib[bcrypt]==1.7.4."""
        return pwd_context.verify(plain_password, hashed_password)

# Global middleware instance
auth_middleware = AgentAuthMiddleware()

# FastAPI 0.115.0 compatible dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = token_scheme) -> Dict[str, Any]:
    """FastAPI dependency for getting current authenticated user."""
    return await auth_middleware.get_current_user(credentials)

# Optional dependency for routes that don't require authentication
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """FastAPI dependency for optional authentication compatible with FastAPI 0.115.0."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return await auth_middleware.get_current_user(credentials)
    except HTTPException:
        return None 