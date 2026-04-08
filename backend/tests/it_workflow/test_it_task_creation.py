"""
Test script for IT Task Creation
"""
from app.services import ITTaskService
from app.database import create_db_session
from app.models import Task, Candidate, Checklist
from datetime import datetime, timedelta

def test_it_task_creation():
    """Test IT task creation"""
    print("Testing IT Task Creation...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get a candidate from database
        candidate = db.query(Candidate).first()
        if not candidate:
            print("⚠ No candidates in database, skipping test")
            return False
        
        print(f"\nUsing candidate: {candidate.name} (ID: {candidate.id})")
        
        # Get or create a checklist for the candidate
        checklist = db.query(Checklist).filter(
            Checklist.candidate_id == candidate.id
        ).first()
        
        if not checklist:
            print("⚠ No checklist found for candidate, skipping test")
            return False
        
        print(f"Using checklist: ID {checklist.id}")
        
        # Create IT task
        joining_date = candidate.joining_date or datetime.now() + timedelta(days=7)
        
        print(f"\nCreating IT task...")
        print(f"  Joining date: {joining_date}")
        
        task = ITTaskService.create_it_task(
            checklist_id=checklist.id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            joining_date=joining_date,
            db=db
        )
        
        print(f"\n✓ IT task created successfully!")
        print(f"  Task ID: {task.id}")
        print(f"  Task name: {task.name}")
        print(f"  Task type: {task.task_type}")
        print(f"  Owner: {task.owner.value}")
        print(f"  Status: {task.status.value}")
        print(f"  Due date: {task.due_date}")
        print(f"  Response token: {task.it_response_token}")
        
        # Verify task properties
        assert task.id is not None, "Task should have an ID"
        assert task.it_response_token is not None, "Task should have a response token"
        assert task.task_type == "it_equipment_allocation", "Task type should be correct"
        assert task.owner.value == "IT", "Task owner should be IT"
        assert task.status.value == "pending", "Task status should be pending"
        assert task.it_reminder_sent_count == 0, "Reminder count should be 0"
        
        print("\n✓ All task properties verified")
        
        # Test token format
        token_parts = task.it_response_token.split('_')
        assert len(token_parts) == 3, "Token should have 3 parts"
        assert token_parts[0] == str(task.id), "First part should be task ID"
        assert token_parts[1].isdigit(), "Second part should be timestamp"
        assert len(token_parts[2]) == 16, "Third part should be 16-char hash"
        
        print("✓ Token format verified")
        
        # Verify task can be retrieved by token
        retrieved_task = ITTaskService.validate_token(task.it_response_token, db)
        assert retrieved_task is not None, "Task should be retrievable by token"
        assert retrieved_task.id == task.id, "Retrieved task should match created task"
        
        print("✓ Task retrievable by token")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_multiple_task_creation():
    """Test creating multiple IT tasks"""
    print("\n\nTesting Multiple IT Task Creation...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get multiple candidates
        candidates = db.query(Candidate).limit(3).all()
        if len(candidates) < 2:
            print("⚠ Need at least 2 candidates, skipping test")
            return False
        
        print(f"\nCreating IT tasks for {len(candidates)} candidates...")
        
        tokens = set()
        task_ids = []
        
        for candidate in candidates:
            # Get checklist
            checklist = db.query(Checklist).filter(
                Checklist.candidate_id == candidate.id
            ).first()
            
            if not checklist:
                print(f"  ⚠ No checklist for {candidate.name}, skipping")
                continue
            
            # Create task
            joining_date = candidate.joining_date or datetime.now() + timedelta(days=7)
            task = ITTaskService.create_it_task(
                checklist_id=checklist.id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                joining_date=joining_date,
                db=db
            )
            
            tokens.add(task.it_response_token)
            task_ids.append(task.id)
            print(f"  ✓ Created task {task.id} for {candidate.name}")
        
        # Verify all tokens are unique
        assert len(tokens) == len(task_ids), "All tokens should be unique"
        print(f"\n✓ All {len(tokens)} tokens are unique")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("IT Task Creation Test Suite")
    print("=" * 60)
    print()
    
    success1 = test_it_task_creation()
    success2 = test_multiple_task_creation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)
