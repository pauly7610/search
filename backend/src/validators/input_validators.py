from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import re
import html
from src.config.settings import settings

class MessageRequest(BaseModel):
    """Validation model for chat messages."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('message')
    def validate_message(cls, v):
        """Validate and sanitize message content."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        
        # Remove potentially dangerous HTML/script tags
        v = html.escape(v)
        
        # Check for suspicious patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'document\.cookie',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Message contains potentially dangerous content")
        
        return v.strip()
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """Validate conversation ID format."""
        if not v or not v.strip():
            raise ValueError("Conversation ID cannot be empty")
        
        # Allow alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid conversation ID format")
        
        return v.strip()

class FeedbackRequest(BaseModel):
    """Validation model for feedback submissions."""
    conversation_id: str = Field(..., min_length=1, max_length=100)
    message_id: Optional[str] = Field(None, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = Field(None, max_length=1000)
    
    @validator('feedback_text')
    def validate_feedback_text(cls, v):
        """Validate and sanitize feedback text."""
        if v:
            v = html.escape(v.strip())
            # Basic content filtering
            if len(v) > 1000:
                raise ValueError("Feedback text too long")
        return v

class SearchRequest(BaseModel):
    """Validation model for knowledge base searches."""
    query: str = Field(..., min_length=1, max_length=500)
    limit: Optional[int] = Field(default=10, ge=1, le=50)
    
    @validator('query')
    def validate_query(cls, v):
        """Validate and sanitize search query."""
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        
        # Basic sanitization
        v = html.escape(v.strip())
        
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v)
        
        return v

class UserProfileRequest(BaseModel):
    """Validation model for user profile updates."""
    user_id: Optional[str] = Field(None, max_length=100)
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if v:
            if not re.match(r'^[a-zA-Z0-9_@.-]+$', v):
                raise ValueError("Invalid user ID format")
        return v
    
    @validator('preferences')
    def validate_preferences(cls, v):
        """Validate preferences dictionary."""
        if v:
            # Limit the size of preferences object
            if len(str(v)) > 5000:
                raise ValueError("Preferences object too large")
            
            # Basic validation for common preference keys
            allowed_keys = {
                'theme', 'language', 'notifications', 'timezone',
                'chat_history', 'auto_save', 'sound_enabled'
            }
            
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"Invalid preference key: {key}")
        
        return v

# Rate limiting validation
class RateLimitValidator:
    """Rate limiting validation for API endpoints."""
    
    @staticmethod
    def validate_rate_limit(user_id: str, endpoint: str) -> bool:
        """
        Validate if user has exceeded rate limits.
        This would typically use Redis for production.
        """
        # For now, just return True - implement with Redis in production
        return True

# Content filtering utilities
class ContentFilter:
    """Content filtering utilities for user input."""
    
    PROFANITY_PATTERNS = [
        # Add profanity patterns as needed
    ]
    
    SPAM_PATTERNS = [
        r'(.)\1{10,}',  # Repeated characters
        r'(https?://[^\s]+){3,}',  # Multiple URLs
        r'[A-Z]{20,}',  # Excessive caps
    ]
    
    @classmethod
    def is_spam(cls, text: str) -> bool:
        """Check if text appears to be spam."""
        for pattern in cls.SPAM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def contains_profanity(cls, text: str) -> bool:
        """Check if text contains profanity."""
        for pattern in cls.PROFANITY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Remove HTML tags and encode entities."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Encode HTML entities
        text = html.escape(text)
        return text
    
    @classmethod
    def validate_file_upload(cls, filename: str, content_type: str) -> bool:
        """Validate file upload safety."""
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.gif'}
        allowed_types = {
            'text/plain', 'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png', 'image/gif'
        }
        
        # Check file extension
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{ext}' not in allowed_extensions:
            return False
        
        # Check content type
        if content_type not in allowed_types:
            return False
        
        return True

# SQL injection prevention utilities
class SQLInjectionPrevention:
    """Utilities to prevent SQL injection attacks."""
    
    SQL_INJECTION_PATTERNS = [
        r'(union|select|insert|update|delete|drop|create|alter)\s',
        r'--',
        r'/\*.*\*/',
        r'\'.*\'',
        r'\".*\"',
        r';\s*(drop|delete|update|insert)',
    ]
    
    @classmethod
    def is_sql_injection_attempt(cls, text: str) -> bool:
        """Check if text contains SQL injection patterns."""
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def sanitize_search_term(cls, term: str) -> str:
        """Sanitize search terms to prevent SQL injection."""
        # Remove SQL injection patterns
        term = re.sub(r'[\'\";\-\-]', '', term)
        # Limit length
        term = term[:500]
        # Remove excessive whitespace
        term = re.sub(r'\s+', ' ', term.strip())
        return term 