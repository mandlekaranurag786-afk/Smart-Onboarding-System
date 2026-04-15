"""
Test script to verify IT notification is sent when new joinee is added
"""
import asyncio
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, '/tmp/tmp.yMEqJqxqQo/backend')

from app.database import create_db_session
from app.models.candidate import Candidate
from app.agents.graph import run_onboarding_workflow


async def test_it_notification():
    """Test that IT notification is sent during onboarding"""
    print("=" * 60)
    print("Testing IT Notification Fix")
    print("=" * 60)
    
    # Test candidate data
    test_candidate = {
        "name": "Test Candidate IT Notification",
        "email": f"test.it.notification.{datetime.now().timestamp()}@example.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "joining_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "reporting_manager": "John Manager",
        "reporting_manager_email": "john.manager@example.com"
    }
    
    print(f"\n1. Creating candidate: {test_candidate['name']}")
    print(f"   Email: {test_candidate['email']}")
    print(f"   Department: {test_candidate['department']}")
    print(f"   Joining Date: {test_candidate['joining_date']}")
    
    # Run onboarding workflow
    print("\n2. Running onboarding workflow...")
    result = await run_onboarding_workflow(test_candidate)
    
    print(f"\n3. Workflow Status: {result.get('status')}")
    print(f"   Candidate ID: {result.get('candidate_id')}")
    print(f"   Checklist ID: {result.get('checklist_id')}")
    
    # Check agent results
    print("\n4. Agent Results:")
    agent_results = result.get('agent_results', [])
    
    it_agent_found = False
    it_email_sent = False
    
    for agent_result in agent_results:
        agent_name = agent_result.get('agent', 'Unknown')
        status = agent_result.get('status', 'Unknown')
        print(f"   - {agent_name}: {status}")
        
        if agent_name == "ITAssetAgent":
            it_agent_found = True
            it_task_id = agent_result.get('it_task_id')
            it_email_status = agent_result.get('it_email_status')
            it_email_recipient = agent_result.get('it_email_recipient')
            
            print(f"     * IT Task ID: {it_task_id}")
            print(f"     * IT Email Status: {it_email_status}")
            print(f"     * IT Email Recipient: {it_email_recipient}")
            
            if it_email_status == "success":
                it_email_sent = True
    
    # Verify IT task was created
    print("\n5. Verification:")
    if it_agent_found:
        print("   ✓ IT Asset Agent executed")
    else:
        print("   ✗ IT Asset Agent NOT found")
    
    if it_email_sent:
        print("   ✓ IT notification email sent successfully")
    else:
        print("   ✗ IT notification email NOT sent")
    
    # Check database for IT task
    db = create_db_session()
    try:
        from app.models.task import Task, TaskOwner
        
        candidate = db.query(Candidate).filter_by(id=result.get('candidate_id')).first()
        if candidate and candidate.checklist:
            it_tasks = [t for t in candidate.checklist.tasks if t.owner == TaskOwner.IT]
            
            if it_tasks:
                print(f"   ✓ IT task created in database (Task ID: {it_tasks[0].id})")
                print(f"     * Task Name: {it_tasks[0].name}")
                print(f"     * Assigned To: {it_tasks[0].assigned_to_email}")
                print(f"     * Response Token: {it_tasks[0].it_response_token[:30]}..." if it_tasks[0].it_response_token else "     * Response Token: None")
            else:
                print("   ✗ No IT task found in database")
    finally:
        db.close()
    
    # Final result
    print("\n" + "=" * 60)
    if it_agent_found and it_email_sent:
        print("✓ TEST PASSED: IT notification is working correctly!")
    else:
        print("✗ TEST FAILED: IT notification is not working")
    print("=" * 60)
    
    return it_agent_found and it_email_sent


if __name__ == "__main__":
    success = asyncio.run(test_it_notification())
    sys.exit(0 if success else 1)
