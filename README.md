# ai-safety-eval-dash

> 🤖 **Modern AI Agent Application** built with **FastAPI** + **Next.js** + **Agno** + **OpenRouter**

A production-ready AI agent application featuring unified access to 500+ language models, vector memory, and powerful agent capabilities through the Agno framework.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org)
[![Agno](https://img.shields.io/badge/Agno-2.0+-blue?style=flat)](https://docs.agno.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-500%2B%20models-green?style=flat)](https://openrouter.ai)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178c6?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed?style=flat&logo=docker)](https://www.docker.com)

---

## 🌟 **Features**

### 🧠 **AI Agent Capabilities**
- **500+ Models** via [OpenRouter](https://openrouter.ai) (GPT-5, Claude 3.7, Gemini 2.5 Pro, Llama 3.3, etc.)
- **[Agno Framework](https://docs.agno.com)** for advanced AI agents with memory, tools, and workflows
- **Multi-Agent Systems** and **Workflow Management**
- **Built-in Agent Memory** with conversation context
- **Tool Integration** and **Function Calling**

### 💾 **Advanced Memory Systems**

- **Vector Database**: Pinecone for semantic search and long-term memory

- **Redis** for fast session storage and caching
- **Hybrid Memory** combining vector search with Redis performance
- **Semantic Search** across conversation history

### 🚀 **Production-Ready Architecture**
- **FastAPI Backend** with async/await support
- **Next.js Frontend** with App Router and TypeScript
- **WebSocket Support** for real-time communication
- **Background Task Processing** with Celery workers and Redis
- **Docker Compose** setup for development and production
- **Microservices Ready** with Redis, Kafka, RabbitMQ support

### 🔧 **Developer Experience**
- **`uv`** for ultra-fast Python dependency management
- **Hot Reload** in development
- **Comprehensive Logging** with Loguru
- **Health Checks** and monitoring endpoints
- **Type Safety** with Pydantic and TypeScript

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │────│   FastAPI       │────│   Agno Agent    │
│   Frontend      │    │   Backend       │    │   Framework     │
│                 │    │                 │    │                 │
│ • TypeScript    │    │ • Python 3.11+ │    │ • OpenRouter    │
│ • Tailwind CSS  │    │ • Async/Await   │    │ • 500+ Models   │
│ • WebSocket     │    │ • Pydantic      │    │ • Memory        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌────────────────────────────┴────────────────────────────┐
    │                                                         │
┌───▼────┐ ┌────────┐ ┌────────┐ ┌─────────────┐ ┌──────────┐
│ Redis  │ │ Kafka  │ │RabbitMQ│ │Pinecone Vector│ │PostgreSQL│
│ Cache  │ │Streams │ │ Queue  │ │  Database   │ │ Database │
└────────┘ └────────┘ └────────┘ └─────────────┘ └──────────┘
```

---

## 🚀 **Quick Start**

### 1. **Prerequisites**
```bash
# Install uv (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Node.js 18+
# https://nodejs.org/

# Install Docker & Docker Compose
# https://docs.docker.com/get-docker/
```

### 2. **Environment Setup**
```bash
# Copy environment files
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env

# Set your API keys in backend/.env
OPENROUTER_API_KEY=your_openrouter_key_here

PINECONE_API_KEY=your_pinecone_key_here

```

### 3. **Start with Docker Compose** ⚡
```bash
# Start all services (recommended for first run)
docker-compose up -d

# Or use the development setup
docker-compose -f docker-compose.dev.yml up -d
```

### 4. **Manual Development Setup** 🛠️
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e .
uv pip list
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 5. **Access Your AI Agent App** 🎉
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤖 **AI Agent Configuration**

### **Model Selection**
Choose from 500+ models available through OpenRouter:

```python
# Latest and greatest models
"gpt-5"                          # OpenAI's latest
"anthropic/claude-3.7-sonnet"    # Anthropic's most capable
"google/gemini-2.5-pro"          # Google's flagship

# Production workhorses
"openai/gpt-4o"                  # Reliable and fast
"anthropic/claude-3.5-sonnet"    # Great for reasoning
"google/gemini-1.5-pro"          # Excellent context window

# Fast and efficient
"openai/gpt-4o-mini"             # Quick responses
"anthropic/claude-3-haiku"       # Speed optimized
"google/gemini-1.5-flash"        # Ultra fast
```

### **Agent Types**

**Current Setup**: single


- **Single Agent**: One AI agent handling all conversations
- **Multi-Agent**: Multiple specialized agents working together
- **Workflow**: Step-by-step agent workflows for complex tasks

### **Memory Configuration**

**Current Setup**: vector with pinecone


- **Vector Memory**: Semantic search across conversation history
- **Redis**: Fast session-based memory
- **Hybrid**: Best of both vector search and Redis speed
- **In-Memory**: Development and testing

---

## 📚 **API Endpoints**

### **Chat & Agents**
```bash
# Start a conversation with an AI agent
POST /api/v1/chat
{
  "message": "Help me plan a web application",
  "session_id": "uuid-here",
  "model": "gpt-5"  # optional
}

# Stream agent responses
POST /api/v1/chat/stream

# Get conversation history
GET /api/v1/chat/sessions/{session_id}

# List all sessions
GET /api/v1/chat/sessions
```

### **Agent Management**
```bash
# Get available models
GET /api/v1/models

# Switch agent model
POST /api/v1/agent/model
{
  "model": "anthropic/claude-3.7-sonnet"
}

# Update agent instructions
POST /api/v1/agent/instructions
{
  "instructions": "You are a helpful coding assistant..."
}
```

### **Memory & Search**
```bash
# Semantic search across conversations
POST /api/v1/search
{
  "query": "database optimization tips",
  "session_id": "uuid-here"  # optional
}

# Clear conversation memory
DELETE /api/v1/chat/sessions/{session_id}
```

### **Background Tasks**
```bash
# Trigger asynchronous LLM completion
POST /api/v1/tasks/llm/completion
{
  "prompt": "Explain quantum computing",
  "model": "gpt-4",
  "delay_seconds": 10
}

# Process chat message asynchronously
POST /api/v1/tasks/chat/process
{
  "message": "Hello",
  "session_id": "uuid-here"
}

# Get task status
GET /api/v1/tasks/{task_id}

# List all active tasks
GET /api/v1/tasks

# Trigger system health check
POST /api/v1/tasks/system/health-check

# Send notification
POST /api/v1/tasks/notifications
{
  "recipient": "user@example.com",
  "message": "Task completed",
  "notification_type": "success"
}
```

---

## 🔧 **Configuration**

### **Backend Settings** (`backend/.env`)
```bash
# Agno + OpenRouter
OPENROUTER_API_KEY=your_key_here
DEFAULT_MODEL=claude-4-sonnet
USE_AGNO_AGENTS=yes
AGENT_TYPE=single

# Vector Database
VECTOR_DATABASE=pinecone

PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=gcp-starter


# Infrastructure
REDIS_URL=redis://localhost:6379/0

DATABASE_URL=postgresql://...


# WebSockets

WEBSOCKET_ENABLED=false


# Celery Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_ALWAYS_EAGER=false  # Set to true for testing
```

### **Frontend Settings** (`frontend/.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000

```

---

## 🚢 **Deployment**

### **Using Docker** (Recommended)
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment script
./backend/scripts/deploy.sh
```

### **Manual Deployment**
```bash
# Backend
cd backend
uv pip install -e .
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Start Celery workers (in separate terminals)
celery -A app.core.celery_app:celery_app worker --queues=general --concurrency=2
celery -A app.core.celery_app:celery_app worker --queues=chat --concurrency=3
celery -A app.core.celery_app:celery_app worker --queues=llm --concurrency=2

# Optional: Start Celery Flower for monitoring
celery -A app.core.celery_app:celery_app flower --port=5555

# Frontend
cd frontend
npm run build
npm start
```

### **Environment Variables for Production**
- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY`
- Configure proper `CORS_ORIGINS`
- Set up SSL/TLS certificates
- Use managed database services

- Configure pinecone production instance


---

## 📁 **Project Structure**

```
ai-safety-eval-dash/
├── 📁 backend/                 # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/v1/         # API routes
│   │   ├── 📁 core/           # Core business logic
│   │   │   ├── 📁 llm/        # Agno + OpenRouter integration
│   │   │   ├── 📁 memory/     # Vector & Redis memory
│   │   │   └── 📁 security/   # Auth & rate limiting
│   │   ├── 📁 models/         # Pydantic models
│   │   ├── 📁 services/       # Business services
│   │   ├── 📁 tasks/          # Celery background tasks
│   │   └── 📁 utils/          # Utilities
│   ├── 📁 docker/             # Docker configurations
│   ├── 📁 scripts/            # Deployment scripts
│   └── 📄 pyproject.toml      # Python dependencies (uv)
│
├── 📁 frontend/               # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/            # Next.js App Router
│   │   ├── 📁 components/     # React components
│   │   │   ├── 📁 ui/         # Base UI components
│   │   │   └── 📁 chat/       # Chat interface
│   │   ├── 📁 hooks/          # Custom React hooks
│   │   ├── 📁 lib/            # Utilities & API client
│   │   └── 📁 types/          # TypeScript definitions
│   └── 📄 package.json       # Node.js dependencies
│
├── 📄 docker-compose.yml     # Development services
├── 📄 docker-compose.prod.yml # Production setup
└── 📄 README.md              # This file
```

---

## 🧪 **Development**

### **Running Tests**
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

### **Code Quality**
```bash
# Backend linting & formatting
cd backend
uv run black .
uv run isort .
uv run ruff check .
uv run mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### **Database Migrations**

```bash
cd backend
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

#### Local tunnel
```bash
ssh -R ai-safety-eval:80:localhost:8000 serveo.net
-> it keeps the same url over and over
```

---

## 🔍 **Monitoring & Health Checks**

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics` (Prometheus format)
- **Agent Status**: `GET /api/v1/agent/status`

- **Vector DB Health**: `GET /api/v1/memory/health`


---

## 🤝 **Contributing**

### 🔧 **Setup Pre-commit Hooks**

We use pre-commit hooks to ensure code quality. Set them up before making changes:

```bash
# Install and setup pre-commit hooks
./scripts/setup-pre-commit.sh

# Or manually:
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

The hooks will automatically check:
- **Python**: Black formatting, autoflake unused import removal, isort import sorting, flake8 linting, mypy type checking
- **Frontend**: Prettier formatting, ESLint linting
- **Security**: Secret detection, private key scanning
- **General**: Trailing whitespace, file endings, YAML/JSON validation

### 🚀 **Contribution Steps**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. **Setup pre-commit hooks**: `./scripts/setup-pre-commit.sh`
4. Make your changes
5. Run tests: `uv run pytest && npm test`
6. Commit: `git commit -m 'Add amazing feature'` (pre-commit hooks will run automatically)
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **[Agno](https://docs.agno.com)** - Powerful AI agent framework
- **[OpenRouter](https://openrouter.ai)** - Unified access to 500+ AI models
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Next.js](https://nextjs.org)** - React framework for production
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package manager

- **[Pinecone](https://pinecone.io)** - Vector database for AI memory


---

## 📞 **Support**

- 📧 **Email**: julien.wut@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Julien W./ai-safety-eval-dash/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/Julien W./ai-safety-eval-dash/wiki)

---

<div align="center">

**Built with ❤️ using the latest AI technologies**

[🤖 Agno](https://docs.agno.com) • [🔀 OpenRouter](https://openrouter.ai) • [⚡ FastAPI](https://fastapi.tiangolo.com) • [⚛️ Next.js](https://nextjs.org)

</div>
