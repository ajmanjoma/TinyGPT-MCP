"""
TinyGPT-MCP: Production-Grade AI Assistant
FastAPI backend with authentication, rate limiting, and plugin architecture
"""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from contextlib import asynccontextmanager

from core.tinygpt_model import TinyGPTModel
from core.mcp_engine import MCPEngine
from core.tool_manager import ToolManager
from core.auth import AuthManager
from core.database import DatabaseManager
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Initialize Redis for rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
except:
    logger.warning("Redis not available, using in-memory rate limiting")
    redis_client = None

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379" if redis_client else "memory://",
    default_limits=["100/hour"]
)

# Global components
tinygpt_model = None
mcp_engine = None
tool_manager = None
auth_manager = None
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global tinygpt_model, mcp_engine, tool_manager, auth_manager, db_manager
    
    logger.info("Starting TinyGPT-MCP application...")
    
    # Initialize components
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    auth_manager = AuthManager(db_manager)
    tool_manager = ToolManager()
    await tool_manager.initialize()
    
    tinygpt_model = TinyGPTModel()
    await tinygpt_model.initialize()
    
    mcp_engine = MCPEngine(tool_manager)
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down application...")
    if db_manager:
        await db_manager.close()

# Initialize FastAPI app
app = FastAPI(
    title="TinyGPT-MCP API",
    description="Production-grade AI assistant with Model Context Protocol",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Request/Response Models
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(500, ge=1, le=2000)
    tools: Optional[List[str]] = None
    stream: bool = False

class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]
    result: Any
    success: bool
    execution_time: float
    error: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    thought: str
    tool_calls: List[ToolCall]
    final_answer: str
    model_info: Dict[str, Any]
    processing_time: float
    tokens_used: int
    timestamp: datetime

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str
    enabled: bool

class SystemStatus(BaseModel):
    status: str
    version: str
    uptime: float
    model_loaded: bool
    tools_available: int
    active_users: int
    requests_today: int

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        return None
    
    try:
        user = await auth_manager.verify_token(credentials.credentials)
        return user
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None

async def require_auth(user = Depends(get_current_user)):
    """Require authentication"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Routes
@app.get("/", response_model=SystemStatus)
async def root():
    """System status and health check"""
    uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    
    return SystemStatus(
        status="healthy",
        version="2.0.0",
        uptime=uptime,
        model_loaded=tinygpt_model.is_loaded if tinygpt_model else False,
        tools_available=len(tool_manager.get_available_tools()) if tool_manager else 0,
        active_users=await auth_manager.get_active_users_count() if auth_manager else 0,
        requests_today=await db_manager.get_requests_today() if db_manager else 0
    )

@app.post("/auth/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(request: Request, auth_request: AuthRequest):
    """User authentication"""
    try:
        token_data = await auth_manager.authenticate_user(
            auth_request.username, 
            auth_request.password
        )
        
        return AuthResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=3600,
            user_id=token_data["user_id"]
        )
    
    except Exception as e:
        logger.warning(f"Login failed for {auth_request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post("/auth/register", response_model=AuthResponse)
@limiter.limit("3/minute")
async def register(request: Request, auth_request: AuthRequest):
    """User registration"""
    try:
        token_data = await auth_manager.create_user(
            auth_request.username,
            auth_request.password
        )
        
        return AuthResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=3600,
            user_id=token_data["user_id"]
        )
    
    except Exception as e:
        logger.error(f"Registration failed for {auth_request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

@app.get("/tools", response_model=List[ToolInfo])
async def get_tools(user = Depends(get_current_user)):
    """Get available tools"""
    tools = tool_manager.get_available_tools()
    
    return [
        ToolInfo(
            name=tool.name,
            description=tool.description,
            parameters=tool.get_parameters(),
            category=tool.category,
            enabled=tool.enabled
        )
        for tool in tools
    ]

@app.post("/ask", response_model=ChatResponse)
@limiter.limit("30/minute")
async def ask(
    request: Request,
    chat_request: ChatRequest,
    user = Depends(require_auth)
):
    """Main chat endpoint with MCP tool calling"""
    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000)}"
    
    try:
        logger.info(f"Processing request {request_id} from user {user['id']}")
        
        # Log request
        await db_manager.log_request(
            user_id=user["id"],
            request_id=request_id,
            prompt=chat_request.prompt,
            timestamp=datetime.utcnow()
        )
        
        # Generate response with TinyGPT
        model_response = await tinygpt_model.generate(
            prompt=chat_request.prompt,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )
        
        # Parse and execute tool calls
        tool_calls = await mcp_engine.process_response(
            model_response["text"],
            available_tools=chat_request.tools
        )
        
        # Format final response
        final_response = await mcp_engine.format_final_response(
            original_response=model_response["text"],
            tool_calls=tool_calls
        )
        
        processing_time = time.time() - start_time
        
        response = ChatResponse(
            id=request_id,
            thought=final_response["thought"],
            tool_calls=[
                ToolCall(
                    tool=call["tool"],
                    params=call["params"],
                    result=call["result"],
                    success=call["success"],
                    execution_time=call["execution_time"],
                    error=call.get("error")
                )
                for call in tool_calls
            ],
            final_answer=final_response["final_answer"],
            model_info=model_response["model_info"],
            processing_time=processing_time,
            tokens_used=model_response["tokens_used"],
            timestamp=datetime.utcnow()
        )
        
        # Log response
        await db_manager.log_response(
            request_id=request_id,
            response=response.dict(),
            processing_time=processing_time
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}"
        )

@app.get("/status")
async def detailed_status():
    """Detailed system status"""
    try:
        model_status = await tinygpt_model.get_status() if tinygpt_model else {}
        tool_status = tool_manager.get_status() if tool_manager else {}
        
        return {
            "system": {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": time.time() - getattr(app.state, 'start_time', time.time())
            },
            "model": model_status,
            "tools": tool_status,
            "database": await db_manager.get_status() if db_manager else {},
            "auth": await auth_manager.get_status() if auth_manager else {}
        }
    
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/tools/{tool_name}/toggle")
async def toggle_tool(tool_name: str, user = Depends(require_auth)):
    """Enable/disable a specific tool"""
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        result = await tool_manager.toggle_tool(tool_name)
        return {"tool": tool_name, "enabled": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/history")
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    user = Depends(require_auth)
):
    """Get user's chat history"""
    try:
        history = await db_manager.get_user_history(
            user_id=user["id"],
            limit=limit,
            offset=offset
        )
        return {"history": history, "total": len(history)}
    
    except Exception as e:
        logger.error(f"Error fetching history for user {user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch history"
        )

# Initialize app state
@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()
    logger.info("TinyGPT-MCP API server started successfully")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting TinyGPT-MCP server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )