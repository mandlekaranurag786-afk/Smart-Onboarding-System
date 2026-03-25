# OnboardIQ Backend - Multi-Agent System

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `backend/.env` and set your GROQ_API_KEY (already configured)

### 3. Test the Agent System
```bash
python3 backend/test_agents.py
```

You should see:
```
✓ All 5 agents working together
✓ Orchestrator controlling flow
✓ LLM-powered intelligent routing
✓ Complete onboarding workflow
```

## What's Built

### ✅ Complete Multi-Agent System

**5 Agents Working Together:**
1. **Orchestrator** - Controls entire flow
2. **Onboarding Trigger** - Welcome emails, checklist creation
3. **IT Asset Agent** - SLA monitoring, escalation
4. **Scheduling Agent** - LLM-powered meeting scheduling
5. **Progress Monitor** - Completion tracking

### ✅ Agentic Intelligence

The **Scheduling Agent** uses LLM reasoning to:
- Find delivery head for department
- Check availability
- Route to fallback if unavailable
- Generate reasoning traces

Example:
```
Candidate: Tejas (AI Department)
→ Primary: Sajal (AI Delivery Head)
→ Check: Sajal on leave until March 25
→ Fallback: Jane Smith (Senior Manager)
→ Decision: Route to Jane
```

### ✅ Human-in-Loop

**IT Asset Assignment:**
- IT receives email with Yes/No buttons
- Click Yes → flow continues
- Click No → capture reason, schedule reminder

## Architecture

See [AGENT_ARCHITECTURE.md](./AGENT_ARCHITECTURE.md) for complete details.

```
Orchestrator (Agent 0)
    ↓
Onboarding Trigger (Agent 1)
    ↓
IT Asset Agent (Agent 2) → [Human Decision]
    ↓
Scheduling Agent (Agent 3) → [LLM Reasoning]
    ↓
Progress Monitor (Agent 4)
```

## What's Next (10-Day Sprint)

### Days 1-2: Database Setup ✅ (Partially Done)
- SQLAlchemy models
- Alembic migrations
- Store candidates, tasks, reasoning traces

### Days 3-4: FastAPI Endpoints
```python
POST   /api/candidates          # Trigger onboarding
GET    /api/candidates/{id}     # Get candidate details
GET    /api/candidates/{id}/progress  # Progress tracking
POST   /api/it/decision         # IT Yes/No
GET    /api/candidates/{id}/reasoning  # Agent reasoning traces
```

### Days 5-6: Email Integration
- SMTP setup
- Email templates
- IT decision buttons (unique tokens)
- Reminder emails

### Days 7-8: Background Jobs
- Hourly IT SLA check
- Daily reminder emails
- Progress monitoring scheduler

### Days 9-10: Frontend Integration
- Connect to Next.js frontend
- Display reasoning traces
- Real-time progress updates
- Demo preparation

## Testing

### Test Complete Flow
```bash
python3 backend/test_agents.py
```

### Test Individual Agents
The test file includes individual agent tests showing:
- Agent 1: Checklist generation
- Agent 2: IT monitoring
- Agent 3: LLM-powered scheduling with fallback
- Agent 4: Progress tracking

## Configuration

### LLM Setup (Groq)
Already configured in `.env`:
```
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

### Email Setup
Update in `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Team Contacts
```
HR_EMAIL=mohini@konverge.ai
IT_EMAIL=sagar@konverge.ai
ADMIN_EMAIL=admin@konverge.ai
```

## Key Features

✅ **Multi-Agent Orchestration** - 5 agents working together
✅ **LLM-Powered Routing** - Intelligent decision making
✅ **Availability Checking** - Automatic fallback routing
✅ **Human-in-Loop** - IT decision point
✅ **SLA Tracking** - 24-hour IT monitoring
✅ **Progress Monitoring** - Continuous tracking
✅ **Graceful Degradation** - Falls back if LLM fails

## Project Status

**✅ COMPLETE:** Core agent system
**🚧 IN PROGRESS:** Database integration
**📋 TODO:** FastAPI endpoints, Email, Frontend

**Timeline:** 10 days to complete
**Current Day:** 1
**Next Milestone:** Database + FastAPI endpoints

## Questions?

See [AGENT_ARCHITECTURE.md](./AGENT_ARCHITECTURE.md) for detailed documentation.
