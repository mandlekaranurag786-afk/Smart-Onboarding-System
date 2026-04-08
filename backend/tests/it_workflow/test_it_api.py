"""
Test script for IT Tasks API endpoints
"""
import requests
import json
from app.database import create_db_session
from app.models import Task
from app.services import ITTaskService

BASE_URL = "http://localhost:8000"

def test_button_response_post():
    """Test POST /api/it-tasks/response/button"""
    print("Testing POST /api/it-tasks/response/button...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get an IT task with a token
        task = db.query(Task).filter(
            Task.task_type == "it_equipment_allocation",
            Task.it_response_token.isnot(None),
            Task.it_response_received_at.is_(None)  # Not yet responded
        ).first()
        
        if not task:
            print("⚠ No pending IT tasks with tokens found")
            print("  Creating a test task...")
            
            # Create a test task
            from app.models import Candidate, Checklist
            from datetime import datetime, timedelta
            
            candidate = db.query(Candidate).first()
            if not candidate or not candidate.checklist:
                print("❌ No candidate with checklist found")
                return False
            
            task = ITTaskService.create_it_task(
                checklist_id=candidate.checklist.id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                joining_date=datetime.now() + timedelta(days=7),
                db=db
            )
            print(f"  ✓ Created test task {task.id}")
        
        print(f"\nUsing task: {task.id}")
        print(f"Token: {task.it_response_token}")
        
        # Test POST request
        payload = {
            "token": task.it_response_token,
            "response": "complete",
            "responder_email": "ninawetejas08@gmail.com",
            "responder_name": "Test IT Member",
            "message": "Laptop allocated and configured"
        }
        
        print(f"\nSending POST request...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/it-tasks/response/button",
            json=payload
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True, "Response should be successful"
            assert data["task_id"] == task.id, "Task ID should match"
            assert data["new_status"] in ["completed", "delayed"], "Status should be valid"
            print("\n✓ POST endpoint working correctly")
            return True
        else:
            print(f"\n❌ POST request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_button_response_get():
    """Test GET /api/it-tasks/response/button"""
    print("\n\nTesting GET /api/it-tasks/response/button...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get an IT task with a token (create new one for GET test)
        from app.models import Candidate
        from datetime import datetime, timedelta
        
        candidate = db.query(Candidate).first()
        if not candidate or not candidate.checklist:
            print("❌ No candidate with checklist found")
            return False
        
        task = ITTaskService.create_it_task(
            checklist_id=candidate.checklist.id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            joining_date=datetime.now() + timedelta(days=7),
            db=db
        )
        
        print(f"\nCreated test task: {task.id}")
        print(f"Token: {task.it_response_token}")
        
        # Test GET request
        url = f"{BASE_URL}/api/it-tasks/response/button?token={task.it_response_token}&response=complete"
        
        print(f"\nSending GET request...")
        print(f"URL: {url}")
        
        response = requests.get(url)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response contains HTML: {bool('<html>' in response.text)}")
        
        if response.status_code == 200 and '<html>' in response.text:
            if 'Response Recorded Successfully' in response.text:
                print("✓ GET endpoint working correctly")
                print("✓ Success page rendered")
                return True
            else:
                print("⚠ HTML returned but unexpected content")
                return False
        else:
            print(f"❌ GET request failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_get_task_status():
    """Test GET /api/it-tasks/{task_id}/status"""
    print("\n\nTesting GET /api/it-tasks/{task_id}/status...")
    print("=" * 60)
    
    db = create_db_session()
    try:
        # Get an IT task
        task = db.query(Task).filter(
            Task.task_type == "it_equipment_allocation"
        ).first()
        
        if not task:
            print("⚠ No IT tasks found")
            return False
        
        print(f"\nQuerying status for task: {task.id}")
        
        response = requests.get(f"{BASE_URL}/api/it-tasks/{task.id}/status")
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["task_id"] == task.id, "Task ID should match"
            assert "candidate_name" in data, "Should include candidate name"
            assert "status" in data, "Should include status"
            assert "days_pending" in data, "Should include days pending"
            print("\n✓ Status endpoint working correctly")
            return True
        else:
            print(f"\n❌ Status request failed with status {response.status_code}")
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
    print("IT Tasks API Test Suite")
    print("=" * 60)
    print("\n⚠ Make sure the API server is running on http://localhost:8000")
    print()
    
    input("Press Enter to start tests...")
    
    success1 = test_button_response_post()
    success2 = test_button_response_get()
    success3 = test_get_task_status()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("✅ All API tests passed!")
    else:
        print("❌ Some API tests failed!")
    print("=" * 60)
