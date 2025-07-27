"""
Database Manager with SQLite for development
"""
import sqlite3
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    SQLite database manager for development
    """
    
    def __init__(self, db_path: str = "tinygpt_mcp.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Requests table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Responses table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    processing_time REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES requests (id)
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def create_user(self, username: str, password_hash: str) -> str:
        """Create a new user"""
        import uuid
        user_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, password_hash)
            )
            await db.commit()
        
        logger.info(f"Created user: {username}")
        return user_id
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    async def log_request(self, user_id: str, request_id: str, prompt: str, timestamp: datetime):
        """Log a user request"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO requests (id, user_id, prompt, timestamp) VALUES (?, ?, ?, ?)",
                (request_id, user_id, prompt, timestamp)
            )
            await db.commit()
    
    async def log_response(self, request_id: str, response: Dict[str, Any], processing_time: float):
        """Log a response"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO responses (request_id, response_data, processing_time) VALUES (?, ?, ?)",
                (request_id, json.dumps(response, default=str), processing_time)
            )
            await db.commit()
    
    async def get_user_history(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's chat history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT r.id, r.prompt, r.timestamp, res.response_data, res.processing_time
                FROM requests r
                LEFT JOIN responses res ON r.id = res.request_id
                WHERE r.user_id = ?
                ORDER BY r.timestamp DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            rows = await cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "prompt": row["prompt"],
                    "timestamp": row["timestamp"],
                    "response": json.loads(row["response_data"]) if row["response_data"] else None,
                    "processing_time": row["processing_time"]
                })
            
            return history
    
    async def get_requests_today(self) -> int:
        """Get number of requests today"""
        today = datetime.now().date()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM requests WHERE DATE(timestamp) = ?",
                (today,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_active_users_count(self) -> int:
        """Get count of users active in last 24 hours"""
        yesterday = datetime.now() - timedelta(days=1)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(DISTINCT user_id) FROM requests WHERE timestamp > ?",
                (yesterday,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        return {
            "total_users": await self.get_total_users(),
            "requests_today": await self.get_requests_today(),
            "active_users": await self.get_active_users_count(),
            "database_path": self.db_path
        }
    
    async def close(self):
        """Close database connections"""
        logger.info("Database connections closed")