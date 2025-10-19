# Quick Start Guide 🚀

Get the Educational Content Assistant running in 5 minutes!

## Prerequisites

- Python 3.11+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Git

## Installation Steps

### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd educational-content-assistant/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

**✅ Done!** API is now running at http://localhost:8000

## First Steps

### 1. Open API Documentation
Visit: http://localhost:8000/docs

### 2. Upload a Document
- Click on **POST /api/v1/documents/upload**
- Click **"Try it out"**
- Upload a PDF file
- Click **"Execute"**

### 3. Generate a Lesson Plan
- Click on **POST /api/v1/lessons/generate**
- Click **"Try it out"**
- Use this example:

```json
{
  "topic": "Introduction to Python",
  "duration_minutes": 45,
  "learner_profile": {
    "age_group": "18-25",
    "difficulty_level": "beginner",
    "prior_knowledge": "Basic computer skills"
  }
}
```

- Click **"Execute"**
- Watch the agent work! ✨

### 4. View the Lesson
- Copy the `lesson_id` from the response
- Click on **GET /api/v1/lessons/{lesson_id}**
- Paste the ID and execute

## Docker Quick Start

If you prefer Docker:

```bash
# Make sure .env exists with your API key
docker-compose up --build
```

Access at http://localhost:8000/docs

## Troubleshooting

**Issue: Module not found**
```bash
pip install -r requirements.txt
```

**Issue: OPENAI_API_KEY not set**
- Check your `.env` file exists
- Verify the key starts with `sk-`

**Issue: Port 8000 already in use**
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

## Next Steps

- Read the full [README.md](README.md)
- Import the [Postman Collection](Educational_Assistant.postman_collection.json)
- Watch the demo video

## Support

Questions? Email: shifaurrahmanroyalist@gmail.com

---

**Happy Teaching! 🎓**