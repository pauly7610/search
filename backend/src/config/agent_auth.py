"""
AgentAuth Configuration Module

This module provides configuration and integration with Composio's AgentAuth
system for AI agent authentication and authorization.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings
from composio import ComposioToolSet, App
import logging

logger = logging.getLogger(__name__)


class AgentAuthSettings(BaseSettings):
    """Configuration settings for AgentAuth integration compatible with pydantic-settings 2.6.1."""

    # Composio API Configuration
    composio_api_key: Optional[str] = Field(
        default=None, description="Composio API key"
    )
    composio_api_url: str = Field(
        default="https://api.composio.dev/v1/", description="Composio API URL"
    )

    # Authentication Configuration
    agent_auth_enabled: bool = Field(
        default=True, description="Enable AgentAuth features"
    )
    oauth2_redirect_uri: str = Field(
        default="http://localhost:3000/auth/callback", description="OAuth2 redirect URI"
    )

    # Supported Apps for Authentication
    supported_apps: List[str] = Field(
        default=["github", "gmail", "slack", "notion", "hubspot", "salesforce"],
        description="List of supported authentication apps",
    )

    # JWT Configuration for internal auth (uses existing SECRET_KEY from main settings)
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT token expiration in minutes"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment


# Global settings instance compatible with pydantic-settings 2.6.1
agent_auth_settings = AgentAuthSettings()


class AgentAuthManager:
    """
    Manages AgentAuth operations including OAuth flows, token management,
    and agent authentication for external service integrations.
    """

    def __init__(self):
        if agent_auth_settings.composio_api_key:
            self.toolset = ComposioToolSet(api_key=agent_auth_settings.composio_api_key)
        else:
            self.toolset = None
            logger.warning(
                "Composio API key not provided. AgentAuth features will be limited."
            )
        self.entity_id = "default"

    async def get_auth_url(self, app_name: str, user_id: str) -> Dict[str, Any]:
        """
        Generate OAuth2 authorization URL for connecting user accounts to apps.

        Args:
            app_name: Name of the app to connect (e.g., 'github', 'gmail')
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing auth URL and connection details
        """
        if not self.toolset:
            raise Exception(
                "Composio API key not configured. Please set COMPOSIO_API_KEY environment variable."
            )

        try:
            entity = self.toolset.get_entity(id=f"user_{user_id}")

            # Get connection request for the specified app
            connection_request = entity.initiate_connection(app=app_name)

            return {
                "auth_url": connection_request.redirectUrl,
                "connection_id": connection_request.connectionId,
                "app": app_name,
                "user_id": user_id,
                "status": "pending",
            }
        except Exception as e:
            logger.error(f"Failed to generate auth URL for {app_name}: {str(e)}")
            raise

    async def verify_connection(
        self, connection_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Verify and complete OAuth2 connection after user authorization.

        Args:
            connection_id: Connection ID from the auth URL generation
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing connection status and details
        """
        if not self.toolset:
            raise Exception(
                "Composio API key not configured. Please set COMPOSIO_API_KEY environment variable."
            )

        try:
            entity = self.toolset.get_entity(id=f"user_{user_id}")
            connections = entity.get_connections()

            for connection in connections:
                if connection.id == connection_id:
                    return {
                        "connection_id": connection_id,
                        "app": connection.appName,
                        "status": "connected" if connection.isActive else "failed",
                        "user_id": user_id,
                        "connected_account": connection.connectedAccountId,
                    }

            return {
                "connection_id": connection_id,
                "status": "not_found",
                "user_id": user_id,
            }

        except Exception as e:
            logger.error(f"Failed to verify connection {connection_id}: {str(e)}")
            raise

    async def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active connections for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of connected apps and their details
        """
        if not self.toolset:
            logger.warning(
                "Composio API key not configured. Returning empty connections list."
            )
            return []

        try:
            entity = self.toolset.get_entity(id=f"user_{user_id}")
            connections = entity.get_connections()

            return [
                {
                    "connection_id": conn.id,
                    "app": conn.appName,
                    "status": "connected" if conn.isActive else "disconnected",
                    "connected_account": conn.connectedAccountId,
                    "created_at": conn.createdAt,
                }
                for conn in connections
            ]
        except Exception as e:
            logger.error(f"Failed to get connections for user {user_id}: {str(e)}")
            return []


# Global agent auth manager instance
agent_auth_manager = AgentAuthManager()
