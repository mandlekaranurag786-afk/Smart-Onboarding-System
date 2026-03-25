"""
Agent 0 - Orchestrator
The brain that controls the entire onboarding flow
"""
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Main orchestrator that coordinates all other agents.
    Controls the flow: Trigger → IT → Scheduling → Progress Monitor
    """
    
    def __init__(self):
        self.name = "Orchestrator"
        logger.info("Orchestrator Agent initialized")
    
    async def start_onboarding(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start the complete onboarding flow for a new candidate.
        
        Flow:
        1. Trigger Agent 1 (Onboarding Trigger)
        2. Monitor Agent 2 (IT Asset Agent)
        3. Trigger Agent 3 (Scheduling Agent) when IT completes
        4. Monitor Agent 4 (Progress Monitor)
        
        Args:
            candidate_data: {name, email, department, joining_date, reporting_manager}
            
        Returns:
            Orchestration result with all agent statuses
        """
        logger.info(f"Starting onboarding for: {candidate_data.get('name')}")
        
        orchestration_log = {
            "candidate": candidate_data.get('name'),
            "started_at": datetime.now().isoformat(),
            "agents_triggered": [],
            "status": "in_progress"
        }
        
        try:
            # Import agents dynamically to avoid circular imports
            from app.agents.onboarding_trigger import OnboardingTriggerAgent
            from app.agents.it_asset_agent import ITAssetAgent
            from app.agents.scheduling_agent import SchedulingAgent
            from app.agents.progress_monitor import ProgressMonitorAgent
            
            # Agent 1: Onboarding Trigger
            trigger_agent = OnboardingTriggerAgent()
            trigger_result = await trigger_agent.trigger_onboarding(candidate_data)
            orchestration_log["agents_triggered"].append({
                "agent": "OnboardingTrigger",
                "status": trigger_result.get("status"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Agent 2: IT Asset Agent (starts monitoring)
            it_agent = ITAssetAgent()
            it_result = await it_agent.start_monitoring(candidate_data)
            orchestration_log["agents_triggered"].append({
                "agent": "ITAssetAgent",
                "status": it_result.get("status"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Agent 3: Scheduling Agent (triggered after IT completes)
            # This will be triggered by IT Agent callback
            scheduling_agent = SchedulingAgent()
            scheduling_result = await scheduling_agent.schedule_meetings(candidate_data)
            orchestration_log["agents_triggered"].append({
                "agent": "SchedulingAgent",
                "status": scheduling_result.get("status"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Agent 4: Progress Monitor (continuous monitoring)
            monitor_agent = ProgressMonitorAgent()
            monitor_result = await monitor_agent.start_monitoring(candidate_data)
            orchestration_log["agents_triggered"].append({
                "agent": "ProgressMonitor",
                "status": monitor_result.get("status"),
                "timestamp": datetime.now().isoformat()
            })
            
            orchestration_log["status"] = "success"
            orchestration_log["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Onboarding orchestration completed for: {candidate_data.get('name')}")
            
            return orchestration_log
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            orchestration_log["status"] = "failed"
            orchestration_log["error"] = str(e)
            return orchestration_log
    
    async def handle_agent_callback(self, agent_name: str, event: str, data: Dict[str, Any]):
        """
        Handle callbacks from other agents.
        
        Example: IT Agent completes → trigger Scheduling Agent
        """
        logger.info(f"Callback from {agent_name}: {event}")
        
        if agent_name == "ITAssetAgent" and event == "it_completed":
            # Trigger scheduling agent
            from app.agents.scheduling_agent import SchedulingAgent
            scheduling_agent = SchedulingAgent()
            await scheduling_agent.schedule_meetings(data)
        
        elif agent_name == "SchedulingAgent" and event == "meetings_scheduled":
            # Update progress monitor
            logger.info("Meetings scheduled, progress monitor updated")
        
        return {"status": "callback_handled"}
