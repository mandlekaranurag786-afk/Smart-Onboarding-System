# Database Migrations

This directory contains database migration scripts for the OnboardIQ system.

## IT Equipment Allocation Workflow Migration

### Overview
The `add_it_equipment_allocation_fields.py` migration adds support for the IT Equipment Allocation Workflow feature, which enables two-way communication between HR and IT teams regarding equipment allocation for new joiners.

### Changes Made

#### 1. Task Model Extensions
Added the following columns to the `tasks` table:

| Column Name | Type | Description |
|------------|------|-------------|
| `it_response_token` | VARCHAR(255) | Unique token for authenticating IT team responses |
| `it_response_received_at` | DATETIME | Timestamp when IT team responded |
| `it_response_type` | VARCHAR(50) | Type of response: "button_click" or "email_reply" |
| `it_responder_email` | VARCHAR(255) | Email of IT team member who responded |
| `it_responder_name` | VARCHAR(255) | Name of IT team member who responded |
| `it_response_message` | TEXT | Message/notes from IT team response |
| `it_reminder_sent_count` | INTEGER | Number of reminder emails sent (default: 0) |
| `it_last_reminder_sent_at` | DATETIME | Timestamp of last reminder email sent |

#### 2. New Table: it_team_members
Created a new table to manage authorized IT team members:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | INTEGER | Primary key |
| `name` | VARCHAR(255) | Full name of IT team member |
| `email` | VARCHAR(255) | Email address (unique, indexed) |
| `is_active` | INTEGER | Active status (0=inactive, 1=active) |
| `notification_enabled` | INTEGER | Notification preference (0=disabled, 1=enabled) |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record update timestamp |

#### 3. Indexes Created
- `idx_tasks_it_response_token` (UNIQUE) - For fast token lookups
- `idx_tasks_status` - For filtering tasks by status
- `idx_tasks_created_at` - For reminder queries
- `idx_it_team_members_email` - For authorization checks

### Running the Migration

The migration runs automatically when you initialize the database:

```python
from app.database import init_db
init_db()
```

Or run it manually:

```bash
cd backend
python -m app.migrations.add_it_equipment_allocation_fields
```

### Seeding IT Team Members

After running the migration, seed initial IT team members:

```bash
cd backend
python -m app.seed_it_team
```

This will add the IT team member configured in your `.env` file (`IT_EMAIL`).

### Rollback

To rollback the migration (removes `it_team_members` table only):

```python
from app.migrations.add_it_equipment_allocation_fields import rollback_migration
rollback_migration()
```

**Note:** SQLite doesn't support `DROP COLUMN`, so task table columns cannot be automatically removed. You would need to manually recreate the table to remove columns.

### Verification

Verify the migration was successful:

```python
from app.models import Task, ITTeamMember
from app.database import create_db_session

db = create_db_session()
try:
    # Check Task model has new fields
    task = db.query(Task).first()
    print(f"Token field exists: {hasattr(task, 'it_response_token')}")
    
    # Check ITTeamMember table
    members = db.query(ITTeamMember).all()
    print(f"IT Team Members: {len(members)}")
finally:
    db.close()
```

### Environment Variables

Make sure these are configured in your `.env` file:

```env
# IT Team Configuration
IT_EMAIL=it.team@company.com
IT_TASK_REMINDER_DAYS=2
IT_TASK_TOKEN_EXPIRY_DAYS=30

# Backend URL for webhook callbacks
BACKEND_URL=https://api.onboardiq.com
```

### Next Steps

After running this migration, you can proceed with:
1. Implementing token generation service (Task 2)
2. Creating IT notification email templates (Task 3)
3. Building the webhook endpoints for IT responses (Task 6)
