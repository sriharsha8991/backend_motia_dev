# Job Description Generator - API Documentation

## 🚀 Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://ai.google.dev/gemini-api/docs/api-key
```

### 3. Start the Server
```bash
npm run dev
```

Server starts at `http://localhost:3000`  
Workbench available at the same URL

---

## 📋 API Endpoints

### **1. Create Job**
```bash
POST /jobs
Content-Type: application/json

{
  "role": "Senior Software Engineer",
  "description": "Looking for an experienced backend developer to build scalable microservices using Node.js and TypeScript with AWS.",
  "yoe": 5,
  "comp": "$120k - $150k + equity"
}
```

**Response (201 Created):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "Senior Software Engineer",
  "description": "Looking for an experienced backend...",
  "yoe": 5,
  "comp": "$120k - $150k + equity",
  "status": "pending",
  "message": "Job created successfully. Description generation in progress.",
  "created_at": "2025-12-16T10:30:00Z"
}
```

### **2. Get Job Status & Content**
```bash
GET /jobs/{job_id}
```

**Response (200 OK) - Pending:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "Senior Software Engineer",
  "status": "pending",
  "created_at": "2025-12-16T10:30:00Z",
  "content": null
}
```

**Response (200 OK) - Completed:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "Senior Software Engineer",
  "status": "completed",
  "file_path": "Job descriptions/550e8400-e29b-41d4-a716-446655440000.txt",
  "content": "Role Overview:\n\nWe are seeking a highly skilled Senior Software Engineer...\n\nKey Responsibilities:\n• Design and develop scalable backend services...",
  "created_at": "2025-12-16T10:30:00Z",
  "updated_at": "2025-12-16T10:30:15Z"
}
```

### **3. List All Jobs**
```bash
GET /jobs
```

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-...",
      "role": "Senior Software Engineer",
      "status": "completed",
      "created_at": "2025-12-16T10:30:00Z",
      "updated_at": "2025-12-16T10:30:15Z"
    }
  ],
  "count": 1,
  "summary": {
    "pending": 0,
    "processing": 0,
    "completed": 1,
    "failed": 0
  }
}
```

---

## 🎯 Example Workflow

```bash
# 1. Create a job
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Senior Software Engineer",
    "description": "Looking for an experienced backend developer to build scalable microservices using Node.js and TypeScript with AWS.",
    "yoe": 5,
    "comp": "$120k - $150k"
  }'

# Save the job_id from response

# 2. Check status (repeat until completed)
curl http://localhost:3000/jobs/{job_id}

# 3. List all jobs
curl http://localhost:3000/jobs
```

---

## 📁 File Structure

```
src/
├── jobs/                          # Job domain steps
│   ├── create_job_step.py         # POST /jobs
│   ├── generate_description_step.py # Event handler
│   ├── get_job_step.py            # GET /jobs/:id
│   └── list_jobs_step.py          # GET /jobs
│
└── services/                       # Reusable services
    ├── gemini_service.py          # AI generation
    └── file_service.py            # File operations

Job descriptions/                   # Generated files
└── {job-id}.txt
```

---

## 🔄 How It Works

1. **User submits job details** via `POST /jobs`
2. **API validates input** (100-150 char description, valid YOE)
3. **Job stored in state** with status "pending"
4. **Event emitted** to `generate-job-description` topic
5. **Background worker** picks up event
6. **Gemini AI generates** comprehensive job description
7. **File saved** to `Job descriptions/` directory
8. **Status updated** to "completed" in state
9. **User can retrieve** via `GET /jobs/:id`

---

## ✨ Features

✅ **Event-Driven Architecture** - Long-running AI tasks don't block HTTP requests  
✅ **State Management** - Track job status across steps  
✅ **Reusable Services** - Gemini & File services can be used anywhere  
✅ **Input Validation** - Pydantic schemas with proper error messages  
✅ **Structured Logging** - Trace every operation in Workbench  
✅ **Error Handling** - Failed jobs marked with error details  
✅ **Domain-Driven Design** - Clean separation of concerns  

---

## 🛠️ Development

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start development server (with hot reload)
npm run dev

# Generate TypeScript types
npm run generate-types

# View in Workbench
# Open http://localhost:3000 in browser
```

---

## 📊 Status Values

- `pending` - Job created, waiting for processing
- `processing` - AI generation in progress
- `completed` - Job description generated and saved
- `failed` - Generation failed (check error field)

---

## 🚨 Error Handling

**400 Bad Request:**
- Missing required fields
- Description not 100-150 characters
- Invalid YOE value

**404 Not Found:**
- Job ID doesn't exist

**500 Internal Server Error:**
- Gemini API failure
- File system error
- State management issue

All errors include detailed messages for debugging.
