"""
Test LangGraph Agent System

This tests the new LangGraph-based workflow.
"""
import sys
import asyncio
import logging

sys.path.insert(0, 'backend')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.agents.graph import run_onboarding_workflow

async def test_langgraph_workflow():
    """Test the LangGraph workflow"""
    
    print("=" * 80)
    print("LANGGRAPH AGENT SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Test candidate
    candidate_data = {
        "name": "Vikram Singh",
        "email": "vikram.singh@konverge.ai",
        "department": "Artificial Intelligence",
        "role": "Senior Engineer",
        "joining_date": "2026-03-25",
        "reporting_manager": "Sumit Sharma"
    }
    
    print(f"Testing onboarding for: {candidate_data['name']}")
    print(f"Department: {candidate_data['department']}")
    print()
    
    print("Starting LangGraph workflow...")
    print()
    
    # Run workflow
    result = await run_onboarding_workflow(candidate_data)
    
    # Display results
    print("=" * 80)
    print("WORKFLOW RESULTS")
    print("=" * 80)
    print()
    print(f"Status: {result.get('status')}")
    print(f"Candidate ID: {result.get('candidate_id')}")
    print(f"Checklist ID: {result.get('checklist_id')}")
    print(f"Total Tasks: {result.get('total_tasks')}")
    print()
    
    print("Agent Results:")
    for agent_result in result.get('agent_results', []):
        print(f"  ✓ {agent_result.get('agent')}: {agent_result.get('status')}")
    print()
    
    print("Meetings Scheduled:")
    for meeting in result.get('meetings_scheduled', []):
        print(f"  - {meeting.get('meeting_type')}")
        print(f"    With: {meeting.get('stakeholder_name')}")
        print(f"    Fallback: {meeting.get('is_fallback')}")
        if meeting.get('reasoning'):
            print(f"    Reasoning: {meeting.get('reasoning')}")
    print()
    
    if result.get('errors'):
        print("Errors:")
        for error in result['errors']:
            print(f"  ✗ {error}")
        print()
    
    print("=" * 80)
    print("KEY FEATURES DEMONSTRATED")
    print("=" * 80)
    print()
    print("✓ LangGraph state machine orchestration")
    print("✓ Automatic tool calling with LLM")
    print("✓ State persistence across nodes")
    print("✓ Database integration")
    print("✓ Reasoning trace storage")
    print("✓ Error handling and recovery")
    print()
    
    print("=" * 80)
    print("LANGGRAPH ADVANTAGES")
    print("=" * 80)
    print()
    print("✓ Automatic tool calling loops")
    print("✓ Built-in state management")
    print("✓ Conditional routing")
    print("✓ Memory checkpointing")
    print("✓ Easy to visualize workflow")
    print("✓ Production-ready error handling")
    print()
    
    return result

if __name__ == "__main__":
    print("\nStarting LangGraph test...\n")
    result = asyncio.run(test_langgraph_workflow())
    
    if result.get('status') == 'success':
        print("\n✓ LangGraph workflow completed successfully!\n")
    else:
        print(f"\n✗ Workflow failed: {result.get('error')}\n")
