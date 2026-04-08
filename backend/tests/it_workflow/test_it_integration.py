"""
Test script for IT Equipment Allocation Integration
"""
from app.database import create_db_session
from app.models import Candidate, Task, Checklist
from app.models.task import TaskOwner
from datetime import datetime

def test_it_task_in_workflow():
    """Test that IT equipment allocation task is created in workflow"""
    print("Testing IT Equipment Allocation Integration...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get a recent candidate
        candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
        
        if not candidate:
            print("⚠ No candidates in database")
            return False
        
        print(f"\nChecking candidate: {candidate.name} (ID: {candidate.id})")
        
        # Get checklist
        checklist = candidate.checklist
        if not checklist:
            print("⚠ No checklist found")
            return False
        
        print(f"Checklist ID: {checklist.id}")
        
        # Find IT equipment allocation task
        it_tasks = [
            task for task in checklist.tasks 
            if task.task_type == "it_equipment_allocation"
        ]
        
        if not it_tasks:
            print("\n❌ No IT equipment allocation task found!")
            print("\nAvailable tasks:")
            for task in checklist.tasks:
                print(f"  - {task.name} ({task.task_type}, {task.owner.value})")
            return False
        
        it_task = it_tasks[0]
        
        print(f"\n✓ IT Equipment Allocation task found!")
        print(f"  Task ID: {it_task.id}")
        print(f"  Task name: {it_task.name}")
        print(f"  Task type: {it_task.task_type}")
        print(f"  Owner: {it_task.owner.value}")
        print(f"  Status: {it_task.status.value}")
        print(f"  Due date: {it_task.due_date}")
        
        # Verify response token
        if it_task.it_response_token:
            print(f"  Response token: {it_task.it_response_token}")
            print("  ✓ Response token generated")
        else:
            print("  ❌ No response token!")
            return False
        
        # Verify token format
        token_parts = it_task.it_response_token.split('_')
        if len(token_parts) == 3:
            print("  ✓ Token format correct")
        else:
            print(f"  ❌ Invalid token format: {it_task.it_response_token}")
            return False
        
        # Check other IT-specific fields
        print(f"\n  IT-specific fields:")
        print(f"    - Reminder count: {it_task.it_reminder_sent_count}")
        print(f"    - Response received: {it_task.it_response_received_at or 'Not yet'}")
        print(f"    - Responder: {it_task.it_responder_name or 'None'}")
        
        print("\n✅ IT Equipment Allocation integration verified!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_task_count():
    """Test that correct number of tasks are created"""
    print("\n\nTesting Task Count...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get a recent candidate
        candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
        
        if not candidate or not candidate.checklist:
            print("⚠ No candidate or checklist found")
            return False
        
        tasks = candidate.checklist.tasks
        print(f"\nTotal tasks: {len(tasks)}")
        print("\nTask breakdown:")
        
        task_by_owner = {}
        for task in tasks:
            owner = task.owner.value
            if owner not in task_by_owner:
                task_by_owner[owner] = []
            task_by_owner[owner].append(task.name)
        
        for owner, task_names in task_by_owner.items():
            print(f"\n  {owner} ({len(task_names)} tasks):")
            for name in task_names:
                print(f"    - {name}")
        
        # Verify we have 9 tasks (8 standard + 1 IT)
        expected_count = 9
        if len(tasks) == expected_count:
            print(f"\n✓ Correct number of tasks ({expected_count})")
            return True
        else:
            print(f"\n⚠ Expected {expected_count} tasks, found {len(tasks)}")
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("IT Equipment Allocation Integration Test")
    print("=" * 60)
    print()
    
    success1 = test_it_task_in_workflow()
    success2 = test_task_count()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed!")
    print("=" * 60)
