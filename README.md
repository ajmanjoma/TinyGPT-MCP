# TinyGPT-MCP: Production-Grade AI Assistant

A comprehensive full-stack AI assistant featuring a lightweight GPT model with Model Context Protocol (MCP) for intelligent tool calling. Built with React frontend, FastAPI backend, authentication, rate limiting, and plugin-ready architecture.

## 🚀 Features

### Backend (FastAPI + Python)
- **TinyGPT Model**: Lightweight GPT with DistilGPT-2 and intelligent intent detection
- **Model Context Protocol**: Structured tool calling with `<tool>function_name</tool>` format
- **6 Built-in Tools**: Weather, Crypto, Wikipedia, Search, Jokes, News
- **Authentication**: JWT-based auth with user registration/login
- **Rate Limiting**: Per-IP rate limiting with Redis support
- **Database**: SQLite for development with async support
- **Plugin Architecture**: Dynamic tool loading and management
- **Docker Support**: Complete containerization with docker-compose
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

### Frontend (React + TypeScript)
- **Modern UI**: Beautiful, responsive design with Framer Motion animations
- **Dark/Light Theme**: Persistent theme switching
- **Real-time Status**: Live system status and tool monitoring
- **Tool Visualization**: Interactive tool grid with execution tracking
- **Authentication UI**: Smooth login/register modals
- **Mobile-First**: Fully responsive across all devices
- **Toast Notifications**: User feedback with react-hot-toast

### Production Features
- **Rate Limiting**: 30 requests/minute per user, 5 login attempts/minute
- **Error Handling**: Comprehensive error handling and logging
- **Security**: JWT tokens, password hashing, CORS protection
- **Monitoring**: Request logging, user analytics, system health checks
- **Scalability**: Plugin system for adding new tools dynamically
- **Docker**: Production-ready containerization

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional):
   ```bash
   export JWT_SECRET_KEY="your-secret-key"
   export OPENWEATHER_API_KEY="your-api-key"
   export NEWS_API_KEY="your-news-api-key"
   ```

4. **Start the server**:
   ```bash
   python app.py
   ```

The backend will be available at:
- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

### Docker Setup (Recommended for Production)

1. **Start with docker-compose**:
   ```bash
   cd backend
   docker-compose up -d
   ```

This starts both the API server and Redis for rate limiting.

## 📖 Usage

### Authentication
1. Click "Login" in the header
2. Register a new account or use existing credentials
3. Start chatting with the AI assistant

### Example Prompts
- "What's the weather in Paris and the price of Bitcoin?"
- "Tell me a joke and show Wikipedia info about AI"
- "Search who won the last World Cup and get ETH price"
- "Give me tech news and explain machine learning"

### API Usage

**Authentication**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

**Chat Request**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the weather in London?", "temperature": 0.7}'
```

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app.py                 # FastAPI main application
├── core/
│   ├── tinygpt_model.py   # TinyGPT implementation
│   ├── mcp_engine.py      # MCP tool orchestration
│   ├── tool_manager.py    # Plugin-ready tool manager
│   ├── auth.py            # JWT authentication
│   └── database.py        # SQLite database manager
├── tools/                 # Built-in tool implementations
├── utils/                 # Utility functions
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Multi-service setup
```

### Frontend Structure
```
src/
├── components/            # React components
├── contexts/              # React contexts (Auth, Theme)
├── services/              # API service layer
└── App.tsx               # Main application
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Core Features
- `GET /` - System status
- `POST /ask` - Main chat endpoint
- `GET /tools` - Available tools
- `GET /history` - Chat history

### Admin
- `POST /tools/{tool_name}/toggle` - Enable/disable tools
- `GET /status` - Detailed system status

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Prevents abuse with configurable limits
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Parameterized queries

## 🔌 Adding Custom Tools

1. **Create tool class**:
```python
from core.tool_manager import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.category = "custom"
    
    async def execute(self, params):
        return {"result": "Custom tool result"}
    
    def get_description(self):
        return "My custom tool"
    
    def get_parameters(self):
        return {"param1": {"type": "string", "required": True}}
```

2. **Register in tool manager**:
```python
# In tool_manager.py
self.tools["my_tool"] = MyTool()
```

## 📊 Monitoring & Analytics

- **Request Logging**: All requests logged to database
- **User Analytics**: Active users, request counts
- **System Health**: Model status, tool availability
- **Performance Metrics**: Response times, success rates

## 🚀 Deployment

### Production Environment Variables
```bash
JWT_SECRET_KEY=your-super-secret-key
OPENWEATHER_API_KEY=your-api-key
NEWS_API_KEY=your-news-api-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
- **Backend**: Deploy to Railway, Fly.io, or AWS
- **Frontend**: Deploy to Vercel, Netlify, or Cloudflare Pages
- **Database**: Use PostgreSQL for production
- **Redis**: Use managed Redis service

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
npm run test
```

### API Testing
Use the interactive docs at `http://localhost:8000/docs` to test all endpoints.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Transformers**: Hugging Face transformers library
- **FastAPI**: High-performance Python web framework
- **React**: Frontend framework
- **Framer Motion**: Animation library
- **Tailwind CSS**: Utility-first CSS framework

---

**TinyGPT-MCP v2.0** - Production-ready AI assistant with intelligent tool calling capabilities.