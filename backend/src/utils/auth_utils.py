"""
Authentication utilities for GraphQL resolvers
"""
from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import User
from src.services.auth_service import verify_token


def get_current_user(token: str, db: Session) -> Optional[User]:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token string
        db: Database session
    
    Returns:
        User object or None if invalid token
    """
    payload = verify_token(token)
    if not payload:
        return None

    username = payload.get("sub")
    if not username:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def require_auth(token: str, db: Session) -> User:
    """
    Require authentication, raise exception if not authenticated
    
    Args:
        token: JWT token string
        db: Database session
    
    Returns:
        User object
    
    Raises:
        Exception if not authenticated
    """
    user = get_current_user(token, db)
    if not user:
        raise Exception("Authentication required. Please provide a valid token.")
    return user
