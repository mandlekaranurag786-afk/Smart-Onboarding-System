"""
Test creating a new candidate with IT equipment allocation
"""
import asyncio
from datetime import datetime, timedelta

async def test_create_candidate():
    """Test creating a new candidate"""
    print("Testing Candidate Creation with IT Equipment Allocation...")
    print("=" * 60)
    
    # Prepare test candidate data
    test_candidate = {
        "name": "Test User IT Integration",
        "email": f"test.it.{datetime.now().timestamp()}@example.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "joining_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "reporting_manager": "Test Manager",
        "reporting_manager_email": "manager@example.com"
    }
    
    print("\nCandidate Data:")
    for key, value in test_candidate.items():
        print(f"  {key}: {value}")
    
    # Run workflow
    from app.agents.graph import run_onboarding_workflow
    
    print("\nRunning onboarding workflow...")
    result = await run_onboarding_workflow(test_candidate)
    
    print(f"\nWorkflow Status: {result.get('status')}")
    
    if result.get("status") != "success":
        print(f"❌ Workflow failed: {result.get('error')}")
        return False
    
    print(f"✓ Candidate ID: {result.get('candidate_id')}")
    print(f"✓ Checklist ID: {result.get('checklist_id')}")
    print(f"✓ Total Tasks: {result.get('total_tasks')}")
    
    # Check agent results
    agent_results = result.get('agent_results', [])
    print(f"\nAgent Results ({len(agent_results)}):")
    for agent_result in agent_results:
        agent_name = agent_result.get('agent', 'Unknown')
        status = agent_result.get('status', 'Unknown')
        print(f"  - {agent_name}: {status}")
        
        # Check for IT task info
        if 'it_task_id' in agent_result:
            print(f"    IT Task ID: {agent_result['it_task_id']}")
            print(f"    IT Email Sent: {agent_result.get('it_email_sent', False)}")
    
    # Verify in database
    from app.database import create_db_session
    from app.models import Candidate, Task
    
    db = create_db_session()
    try:
        candidate = db.query(Candidate).filter_by(id=result['candidate_id']).first()
        
        if not candidate:
            print("\n❌ Candidate not found in database!")
            return False
        
        print(f"\n✓ Candidate found in database: {candidate.name}")
        
        # Check for IT equipment allocation task
        it_tasks = [
            task for task in candidate.checklist.tasks
            if task.task_type == "it_equipment_allocation"
        ]
        
        if not it_tasks:
            print("\n❌ No IT equipment allocation task found!")
            print("\nAvailable tasks:")
            for task in candidate.checklist.tasks:
                print(f"  - {task.name} ({task.task_type})")
            return False
        
        it_task = it_tasks[0]
        
        print(f"\n✓ IT Equipment Allocation task found!")
        print(f"  Task ID: {it_task.id}")
        print(f"  Task name: {it_task.name}")
        print(f"  Owner: {it_task.owner.value}")
        print(f"  Status: {it_task.status.value}")
        print(f"  Response token: {it_task.it_response_token}")
        
        if it_task.it_response_token:
            print("\n✅ IT Equipment Allocation integration successful!")
            return True
        else:
            print("\n❌ No response token generated!")
            return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Create Candidate with IT Equipment Allocation Test")
    print("=" * 60)
    print()
    
    success = asyncio.run(test_create_candidate())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    print("=" * 60)
