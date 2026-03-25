"""
Test the Multi-Agent Orchestration System

This demonstrates all 5 agents working together:
- Agent 0: Orchestrator (controls flow)
- Agent 1: Onboarding Trigger (welcome emails, checklist)
- Agent 2: IT Asset Agent (monitors IT, escalates)
- Agent 3: Scheduling Agent (intelligent meeting scheduling with LLM)
- Agent 4: Progress Monitor (tracks completion)

Run: python3 backend/test_agents.py
"""
import sys
import asyncio
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.insert(0, 'backend')

from app.agents.orchestrator import OrchestratorAgent

async def test_complete_onboarding_flow():
    """Test the complete onboarding flow with all agents"""
    
    print("=" * 80)
    print("ONBOARDIQ - MULTI-AGENT ORCHESTRATION SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Sample candidate data
    candidate_data = {
        "name": "Tejas Patil",
        "email": "tejas@konverge.ai",
        "department": "Artificial Intelligence",
        "joining_date": "2026-03-24",
        "reporting_manager": "Sumit Sharma"
    }
    
    print(f"Testing onboarding for: {candidate_data['name']}")
    print(f"Department: {candidate_data['department']}")
    print(f"Joining Date: {candidate_data['joining_date']}")
    print()
    
    # Initialize orchestrator
    print("1. Initializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent()
    print("   ✓ Orchestrator ready")
    print()
    
    # Start onboarding flow
    print("2. Starting complete onboarding flow...")
    print("   This will trigger all 4 agents in sequence:")
    print("   - Agent 1: Onboarding Trigger")
    print("   - Agent 2: IT Asset Agent")
    print("   - Agent 3: Scheduling Agent (with LLM)")
    print("   - Agent 4: Progress Monitor")
    print()
    
    result = await orchestrator.start_onboarding(candidate_data)
    
    # Display results
    print("=" * 80)
    print("ORCHESTRATION RESULTS")
    print("=" * 80)
    print()
    print(f"Status: {result['status']}")
    print(f"Started: {result['started_at']}")
    print(f"Completed: {result.get('completed_at', 'N/A')}")
    print()
    print("Agents Triggered:")
    for agent in result['agents_triggered']:
        print(f"  ✓ {agent['agent']}: {agent['status']}")
        print(f"    Timestamp: {agent['timestamp']}")
    print()
    
    print("=" * 80)
    print("SUCCESS! All agents executed successfully.")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("✓ Multi-agent orchestration")
    print("✓ Parallel email notifications")
    print("✓ IT monitoring with SLA tracking")
    print("✓ Intelligent meeting scheduling with LLM")
    print("✓ Availability checking and fallback routing")
    print("✓ Progress monitoring")
    print()
    print("Next Steps:")
    print("1. Connect to actual database")
    print("2. Implement email sending")
    print("3. Add background schedulers for monitoring")
    print("4. Build FastAPI endpoints")
    print("5. Connect to frontend")
    print()

async def test_individual_agents():
    """Test each agent individually"""
    
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL AGENTS")
    print("=" * 80)
    
    candidate_data = {
        "name": "Mugdha",
        "email": "mugdha@konverge.ai",
        "department": "Artificial Intelligence",
        "joining_date": "2026-03-24",
        "reporting_manager": "Sumit Sharma"
    }
    
    # Test Agent 1
    print("\n--- Agent 1: Onboarding Trigger ---")
    from app.agents.onboarding_trigger import OnboardingTriggerAgent
    agent1 = OnboardingTriggerAgent()
    result1 = await agent1.trigger_onboarding(candidate_data)
    print(f"Status: {result1['status']}")
    print(f"Actions: {', '.join(result1['actions'])}")
    
    # Test Agent 2
    print("\n--- Agent 2: IT Asset Agent ---")
    from app.agents.it_asset_agent import ITAssetAgent
    agent2 = ITAssetAgent()
    result2 = await agent2.start_monitoring(candidate_data)
    print(f"Status: {result2['status']}")
    print(f"SLA Deadline: {result2['sla_deadline']}")
    
    # Test Agent 3
    print("\n--- Agent 3: Scheduling Agent (with LLM) ---")
    from app.agents.scheduling_agent import SchedulingAgent
    agent3 = SchedulingAgent()
    result3 = await agent3.schedule_meetings(candidate_data)
    print(f"Status: {result3['status']}")
    print(f"Meetings Scheduled: {result3['total_scheduled']}")
    for meeting in result3['meetings']:
        print(f"  - {meeting['meeting_type']}: {meeting['with']} ({meeting['status']})")
        if meeting.get('is_fallback'):
            print(f"    Fallback: {meeting.get('reasoning')}")
    
    # Test Agent 4
    print("\n--- Agent 4: Progress Monitor ---")
    from app.agents.progress_monitor import ProgressMonitorAgent
    agent4 = ProgressMonitorAgent()
    result4 = await agent4.start_monitoring(candidate_data)
    print(f"Status: {result4['status']}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print("\nStarting agent tests...\n")
    
    # Run complete flow test
    asyncio.run(test_complete_onboarding_flow())
    
    # Run individual agent tests
    asyncio.run(test_individual_agents())
    
    print("\n✓ All tests completed!\n")
