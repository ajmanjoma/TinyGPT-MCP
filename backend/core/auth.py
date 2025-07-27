"""
Authentication Manager with JWT tokens
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """
    JWT-based authentication manager
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
    
    async def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user in database
        user_id = await self.db_manager.create_user(username, password_hash.decode('utf-8'))
        
        # Generate token
        token = self._create_access_token({"sub": user_id, "username": username})
        
        return {
            "access_token": token,
            "user_id": user_id
        }
    
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return token"""
        user = await self.db_manager.get_user_by_username(username)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            raise ValueError("Invalid password")
        
        # Generate token
        token = self._create_access_token({"sub": user["id"], "username": username})
        
        return {
            "access_token": token,
            "user_id": user["id"]
        }
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            username = payload.get("username")
            
            if not user_id:
                raise ValueError("Invalid token")
            
            return {
                "id": user_id,
                "username": username
            }
        
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        return await self.db_manager.get_active_users_count()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get authentication system status"""
        return {
            "total_users": await self.db_manager.get_total_users(),
            "active_users": await self.get_active_users_count(),
            "token_expiry_minutes": self.access_token_expire_minutes
        }