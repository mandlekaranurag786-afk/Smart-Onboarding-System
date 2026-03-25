# OnboardIQ API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Create Candidate (Trigger Onboarding)

**POST** `/api/candidates/`

Create a new candidate and trigger the complete onboarding flow.

**Request Body:**
```json
{
  "name": "Aayush",
  "email": "aayush@konverge.ai",
  "department": "Engineering",
  "role": "Engineer",
  "joining_date": "25/03/2026",
  "reporting_manager": "Kaustubh Vartak"
}
```

**Response:**
```json
{
  "id": 3,
  "name": "Aayush",
  "email": "aayush@konverge.ai",
  "department": "Engineering",
  "role": "Engineer",
  "joining_date": "2026-03-25",
  "reporting_manager": "Kaustubh Vartak",
  "status": "onboarding_started",
  "completion_percentage": 0.0,
  "total_tasks": 9,
  "completed_tasks": 0
}
```

**What Happens:**
1. Orchestrator agent triggered
2. Candidate record created in database
3. 9-task checklist generated
4. Emails sent to HR, IT, Admin, Candidate
5. IT monitoring started
6. Meetings scheduled (with LLM routing)
7. Progress monitoring started

---

### 3. Get All Candidates

**GET** `/api/candidates/`

Get list of all candidates with their progress.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Tejas Patil",
    "email": "tejas@konverge.ai",
    "department": "Artificial Intelligence",
    "role": "Employee",
    "joining_date": "2026-03-24",
    "reporting_manager": "Sumit Sharma",
    "status": "onboarding_started",
    "completion_percentage": 0.0,
    "total_tasks": 9,
    "completed_tasks": 0
  },
  {
    "id": 2,
    "name": "Mugdha",
    "email": "mugdha@konverge.ai",
    "department": "Artificial Intelligence",
    "role": "Employee",
    "joining_date": "2026-03-24",
    "reporting_manager": "Sumit Sharma",
    "status": "onboarding_started",
    "completion_percentage": 0.0,
    "total_tasks": 9,
    "completed_tasks": 0
  }
]
```

---

### 4. Get Single Candidate

**GET** `/api/candidates/{candidate_id}`

Get details of a specific candidate.

**Response:**
```json
{
  "id": 1,
  "name": "Tejas Patil",
  "email": "tejas@konverge.ai",
  "department": "Artificial Intelligence",
  "role": "Employee",
  "joining_date": "2026-03-24",
  "reporting_manager": "Sumit Sharma",
  "status": "onboarding_started",
  "completion_percentage": 0.0,
  "total_tasks": 9,
  "completed_tasks": 0
}
```

---

### 5. Get Candidate Progress

**GET** `/api/candidates/{candidate_id}/progress`

Get detailed progress with all tasks.

**Response:**
```json
{
  "candidate_id": 1,
  "candidate_name": "Tejas Patil",
  "status": "onboarding_started",
  "completion_percentage": 0.0,
  "total_tasks": 9,
  "completed_tasks": 0,
  "tasks": [
    {
      "id": 1,
      "name": "Document Signing",
      "owner": "HR",
      "status": "pending",
      "assigned_to": null,
      "due_date": null,
      "completed_date": null
    },
    {
      "id": 2,
      "name": "Work Profile Builder",
      "owner": "Candidate",
      "status": "pending",
      "assigned_to": null,
      "due_date": null,
      "completed_date": null
    }
    // ... 7 more tasks
  ]
}
```

---

### 6. Update Task Status

**PATCH** `/api/tasks/{task_id}`

Update the status of a task.

**Request Body:**
```json
{
  "status": "completed"
}
```

**Valid Statuses:**
- `pending`
- `in_progress`
- `completed`
- `overdue`
- `blocked`

**Response:**
```json
{
  "id": 1,
  "name": "Document Signing",
  "status": "completed",
  "message": "Task updated successfully"
}
```

---

### 7. Get Stakeholders

**GET** `/api/stakeholders/`

Get all team members (HR, IT, Managers, etc.)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Mohini",
    "email": "mohini@konverge.ai",
    "role": "HR",
    "department": "Human Resources",
    "is_available": true,
    "on_leave_until": null
  },
  {
    "id": 3,
    "name": "Sajal",
    "email": "sajal@konverge.ai",
    "role": "Delivery Head",
    "department": "Artificial Intelligence",
    "is_available": false,
    "on_leave_until": "2026-03-25"
  }
]
```

---

### 8. Get Reasoning Traces

**GET** `/api/reasoning/{candidate_id}`

Get all LLM reasoning traces for a candidate (for auditability).

**Response:**
```json
[
  {
    "id": 1,
    "agent_name": "SchedulingAgent",
    "task_type": "meeting_scheduling",
    "decision": "Route to Jane Smith",
    "reasoning": "Sajal on leave until March 25, Jane is fallback",
    "confidence_score": 95,
    "assigned_stakeholder_name": "Jane Smith",
    "is_fallback": true,
    "fallback_reason": "Primary stakeholder unavailable",
    "trace_steps": [
      {
        "step": 1,
        "action": "check_availability",
        "result": "Sajal unavailable"
      },
      {
        "step": 2,
        "action": "get_fallback",
        "result": "Jane Smith"
      }
    ],
    "created_at": "2026-03-25T10:54:16.567632"
  }
]
```

---

## Frontend Integration

### Update Frontend API Base URL

In your Next.js frontend, update the API base URL:

```typescript
// frontend/src/lib/api.ts or similar
const API_BASE_URL = "http://localhost:8000";

export async function createCandidate(data: CandidateData) {
  const response = await fetch(`${API_BASE_URL}/api/candidates/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error("Failed to create candidate");
  }
  
  return response.json();
}

export async function getCandidates() {
  const response = await fetch(`${API_BASE_URL}/api/candidates/`);
  return response.json();
}
```

### Example: Add New Joinee from Frontend

```typescript
// When user submits the form
const handleSubmit = async (formData) => {
  try {
    const candidate = await createCandidate({
      name: formData.name,
      email: formData.email,
      department: formData.department,
      role: formData.role,
      joining_date: formData.joiningDate, // "25/03/2026"
      reporting_manager: formData.reportingManager
    });
    
    console.log("Candidate created:", candidate);
    // Refresh the candidates list
    fetchCandidates();
  } catch (error) {
    console.error("Error creating candidate:", error);
  }
};
```

---

## Starting the API Server

### Option 1: Using the script

```bash
./backend/start_api.sh
```

### Option 2: Direct command

```bash
cd backend
export PYTHONPATH=.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Python

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will start at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get candidates
curl http://localhost:8000/api/candidates/

# Create candidate
curl -X POST http://localhost:8000/api/candidates/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aayush",
    "email": "aayush@konverge.ai",
    "department": "Engineering",
    "role": "Engineer",
    "joining_date": "25/03/2026",
    "reporting_manager": "Kaustubh Vartak"
  }'
```

### Using Python test script

```bash
python3 backend/test_api.py
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (Next.js default)
- `http://localhost:3001` (Alternative port)

If your frontend runs on a different port, update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:YOUR_PORT"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Real-Time Updates

The API saves data to the database immediately. When you:

1. **Add a new joinee** → POST `/api/candidates/`
   - Candidate created in DB
   - Checklist generated
   - All agents triggered
   - Data persisted

2. **Refresh the page** → GET `/api/candidates/`
   - Fetches latest data from DB
   - Shows all candidates with real-time progress

3. **Update task** → PATCH `/api/tasks/{id}`
   - Task status updated in DB
   - Completion percentage recalculated
   - Changes reflected immediately

---

## Status

✅ **API Complete and Working**
✅ **Database Integration Active**
✅ **All Endpoints Tested**
✅ **Ready for Frontend Connection**

**Next Step:** Update your Next.js frontend to use these endpoints instead of mock data.
