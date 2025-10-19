# Educational Content Assistant 🎓

An AI-powered FastAPI application that generates personalized lesson plans from educational documents using an intelligent agent with multi-step reasoning capabilities.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.6-green.svg)](https://python.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Design Decisions](#-design-decisions)
- [Evaluation & Monitoring](#-evaluation--monitoring)
- [Docker Deployment](#-docker-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Capabilities

- **📚 Document Processing**: Upload educational PDFs, automatically chunk, embed, and store in FAISS vector database
- **🤖 Intelligent Agent**: Multi-step reasoning agent that orchestrates lesson plan generation
- **🔍 RAG Implementation**: Retrieval-Augmented Generation for context-aware lesson plans
- **🎯 Personalization**: Adjusts content difficulty based on learner profiles
- **📊 Structured Output**: Generates comprehensive lesson plans with objectives, activities, and assessments
- **🔄 Async Processing**: Non-blocking endpoints for long-running tasks
- **📝 Complete Logging**: Tracks all agent decisions and tool usage

### Agent Tools

1. **Knowledge Base Search**: Retrieves relevant content from uploaded educational materials
2. **Lesson Plan Generator**: Creates structured lesson templates
3. **Difficulty Adjuster**: Tailors content to learner age group and proficiency level

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   API       │    │   Service    │    │    Agent      │  │
│  │  Endpoints  │───▶│    Layer     │───▶│   System      │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                   │                     │          │
│         │                   │                     ▼          │
│         │                   │            ┌──────────────┐   │
│         │                   │            │  Tool Layer  │   │
│         │                   │            ├──────────────┤   │
│         │                   │            │  • Search    │   │
│         │                   │            │  • Generate  │   │
│         │                   │            │  • Adjust    │   │
│         │                   │            └──────────────┘   │
│         │                   ▼                     │          │
│         │          ┌──────────────┐              │          │
│         │          │  Document    │              │          │
│         │          │  Processing  │              │          │
│         │          └──────────────┘              │          │
│         ▼                   │                     │          │
│  ┌─────────────┐            ▼                     ▼          │
│  │  Pydantic   │   ┌──────────────┐    ┌──────────────┐   │
│  │  Models     │   │    FAISS     │    │   OpenAI     │   │
│  └─────────────┘   │   Vector DB  │    │   GPT-4o     │   │
│                     └──────────────┘    └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Agent Workflow

```
User Request
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  STEP 1: Analyze Request                             │
│  Parse topic, duration, difficulty, learner profile  │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  STEP 2: Search Knowledge Base                       │
│  Tool: search_knowledge_base(query)                  │
│  Retrieve relevant educational content from FAISS    │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  STEP 3: Generate Lesson Structure                   │
│  Tool: generate_lesson_structure(topic, duration)    │
│  Create template with timing and sections            │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  STEP 4: Adjust Difficulty                           │
│  Tool: adjust_difficulty(content, level, age_group)  │
│  Tailor vocabulary and complexity                    │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  STEP 5: Synthesize Final Lesson Plan                │
│  Combine all information into structured output      │
│  Save to disk with unique lesson_id                  │
└──────────────────────────────────────────────────────┘
     │
     ▼
  Return Result
```

---

## 📦 Prerequisites

- **Python**: 3.11 or higher
- **OpenAI API Key**: Required for embeddings and LLM
- **Docker** (optional): For containerized deployment
- **Git**: For version control

---

## 🚀 Installation

### Option 1: Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd educational-content-assistant/backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy example .env
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-api-key-here
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

6. **Access the API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option 2: Docker Setup

1. **Build and run with Docker Compose**
```bash
# Make sure .env file exists with your API key
docker-compose up --build
```

2. **Access the containerized API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

---

## 💻 Usage

### Quick Start Example

1. **Upload an educational document**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@your-textbook.pdf"
```

2. **Generate a lesson plan**
```bash
curl -X POST "http://localhost:8000/api/v1/lessons/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Photosynthesis",
    "duration_minutes": 60,
    "learner_profile": {
      "age_group": "13-15",
      "difficulty_level": "intermediate",
      "prior_knowledge": "Basic biology concepts"
    },
    "additional_context": "Focus on practical experiments"
  }'
```

3. **Retrieve the lesson plan**
```bash
curl -X GET "http://localhost:8000/api/v1/lessons/{lesson_id}"
```

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI with:
- Interactive API testing
- Request/response schemas
- Authentication flows
- Example values

---

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload and process PDF documents |
| `GET` | `/api/v1/documents/stats` | Get vector database statistics |
| `POST` | `/api/v1/lessons/generate` | Generate personalized lesson plan |
| `GET` | `/api/v1/lessons/{lesson_id}` | Retrieve specific lesson |
| `GET` | `/api/v1/lessons/` | List all lessons |
| `GET` | `/api/v1/agent/status` | Get agent status and steps |
| `POST` | `/api/v1/agent/feedback` | Submit feedback on lesson |

### Sample Request/Response

**POST /api/v1/lessons/generate**

Request:
```json
{
  "topic": "Introduction to PySpark",
  "duration_minutes": 60,
  "learner_profile": {
    "age_group": "adults",
    "difficulty_level": "intermediate",
    "prior_knowledge": "Basic Python and data processing concepts",
    "learning_objectives": [
      "Understand PySpark vs Pandas differences",
      "Create and manipulate DataFrames"
    ]
  },
  "additional_context": "Focus on practical DataFrame examples"
}
```

Response:
```json
{
  "lesson_id": "uuid-here",
  "status": "completed",
  "message": "Lesson plan generated successfully",
  "lesson_plan": {
    "topic": "Introduction to PySpark",
    "difficulty_level": "intermediate",
    "duration_minutes": 60,
    "objectives": [
      "Differentiate between PySpark and Pandas DataFrames",
      "Create and manipulate DataFrames in PySpark",
      "Perform filtering and grouping operations"
    ],
    "prerequisites": [
      "Basic Python programming",
      "Familiarity with data structures"
    ],
    "content_outline": [
      {
        "title": "Introduction",
        "content": "Overview of big data and PySpark",
        "duration_minutes": 6
      }
    ],
    "activities": [
      "Hands-on coding exercises",
      "Pair programming tasks"
    ],
    "assessments": [
      "Quiz on PySpark concepts",
      "Practical DataFrame manipulation"
    ],
    "resources": [
      "Sample CSV datasets",
      "Jupyter notebooks"
    ]
  }
}
```

---

## 🎯 Design Decisions

### 1. **RAG Implementation**

**Chunking Strategy:**
- **Method**: RecursiveCharacterTextSplitter
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Rationale**: Balances context preservation with retrieval precision

**Embeddings:**
- **Model**: text-embedding-3-small
- **Dimension**: 1536
- **Rationale**: Cost-effective with high accuracy

**Vector Store:**
- **Choice**: FAISS
- **Rationale**: Fast in-memory search, no external dependencies

### 2. **Agent Architecture**

**Framework**: LangChain with OpenAI Functions
- Structured tool calling
- Built-in error handling
- Observable execution traces

**Tools Design:**
- Specialized, single-purpose tools
- JSON input/output for structured data
- Graceful fallbacks for edge cases

### 3. **API Design**

**RESTful Principles:**
- Resource-based URLs (`/lessons`, `/documents`)
- Proper HTTP methods and status codes
- Stateless operations

**Async Processing:**
- Non-blocking I/O for file uploads
- Background tasks for indexing
- Streaming responses (future enhancement)

### 4. **Trade-offs**

| Decision | Pros | Cons | Mitigation |
|----------|------|------|------------|
| FAISS (in-memory) | Fast, simple | Not persistent by default | Save/load on disk |
| OpenAI embeddings | High quality | API costs | Batch processing |
| Synchronous generation | Simpler code | Blocks during LLM calls | Use async endpoints |
| Single agent instance | Stateful debugging | Not scalable | Future: multi-instance |

---

## 📊 Evaluation & Monitoring

### Logging

All agent decisions are logged:
```python
2025-10-19 12:08:44 - Agent starting lesson generation
2025-10-19 12:08:46 - Tool used: search_knowledge_base
2025-10-19 12:08:48 - Tool used: generate_lesson_structure
2025-10-19 12:08:50 - Tool used: adjust_difficulty
2025-10-19 12:09:01 - Agent completed lesson generation
```

### Metrics (Future Enhancement)

**Planned metrics:**
- Retrieval relevance scoring (cosine similarity threshold)
- Citation accuracy (source attribution validation)
- Generation latency tracking
- Token usage monitoring

### Rate Limits & Costs

**Current Approach:**
- No explicit rate limiting implemented
- OpenAI tier limits apply (100 requests/min for embeddings)
- Cost per lesson: ~$0.02-0.05 (depending on content length)

**Recommendations:**
- Implement request throttling for production
- Cache frequently accessed embeddings
- Use batch processing for bulk uploads
- Monitor token usage via OpenAI dashboard

---

## 🐳 Docker Deployment

### Build

```bash
docker build -t educational-assistant .
```

### Run

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -v $(pwd)/data:/app/data \
  educational-assistant
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

---

## 🧪 Testing

### Manual Testing

Use the Swagger UI at http://localhost:8000/docs

### Postman Collection

Import the provided `Educational_Assistant.postman_collection.json` for:
- Pre-configured requests
- Environment variables
- Example payloads

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Authors

- Shifaur Rahman - Initial work

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- LangChain for agent orchestration
- OpenAI for powerful LLM capabilities
- FAISS for efficient vector search

---

## 📧 Contact

For questions or support, please contact: shifaurrahmanroyalist@gmail.com

---

**Built with ❤️ for better education**