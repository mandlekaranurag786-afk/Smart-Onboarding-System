# QA Testing Document: Smart Onboarding System

This document outlines the testing scenarios built for the updated candidate onboarding flow with dynamic task updates and role-based access rules.

## 1. HR Portal - Task Progression, Skipping & Recovery
**Scenario 1: HR skips a task for a candidate**
- **Pre-condition**: HR is logged into the OnboardingIQ dashboard. A candidate has tasks in the checklist.
- **Steps**:
  1. Open the Employee Directory.
  2. Click on a candidate to open their journey checklist.
  3. Identify any non-completed task (current or future).
  4. Click the "Skip Step" button.
- **Expected Results**:
  1. The task status visibly changes to "Skip" (marked with amber color) and is stored on the backend with the `is_fallback` flag.
  2. If the skipped task was the "Active" one, the next pending task in sequence becomes the new "Active" current step.
  3. If the task was a future task, the current "Active" task remains unchanged.
  4. The task skip is recorded accurately without failing the overall onboarding completion count.

**Scenario 1b: HR recovers a skipped task**
- **Pre-condition**: HR is logged in. A candidate has a task marked as "Skip".
- **Steps**:
  1. Open the candidate's journey checklist.
  2. Identify a task with the "Skip" (amber) status.
  3. Click the "Recover" button.
- **Expected Results**:
  1. The task status reverts to "Wait" (or "Active" if it's the next pending task).
  2. The `is_fallback` flag is cleared on the backend, and `completed_date` is reset to null.
  3. The completion percentage is recalculated correctly.

## 2. Final Review Acknowledgment
**Scenario 2: Final steps restrict skipping**
- **Pre-condition**: Candidate has completed or skipped tasks 1 to 8. The "Final Review" step is active.
- **Steps**:
  1. Ensure you are on the HR dashboard.
  2. View the candidate's journey checklist.
  3. Observe the buttons available for the "Final Review" step.
- **Expected Results**:
  1. The "Skip Step" button must NOT be present.
  2. An "Acknowledge Final" button is shown.
  3. Clicking "Acknowledge Final" correctly marks the final review as Done.

## 3. Onboarded State Progression
**Scenario 3: Completing 100% of tasks**
- **Pre-condition**: A candidate sequence is completed up to the final task.
- **Steps**:
  1. Complete the "Final Review" task using the "Acknowledge Final" button.
  2. Allow the dashboard to auto-refresh via the triggered `loadCandidates` and `updateTaskStatus` APIs.
- **Expected Results**:
  1. The candidate's `completion_percentage` hits 100%.
  2. The candidate's status badge updates to "Onboarded".
  3. In the Analytics tab, the "Onboarded" KPI count increments precisely by 1 for this candidate.

## 4. Candidate Portal - Smart Scheduling Constraint
**Scenario 4: Validating Meeting Acknowledgements**
- **Pre-condition**: Candidate is logged in. A meeting task (e.g., HR Walkthrough, Manager Intro) is the currently active step.
- **Steps**:
  1. Check the task list as a Candidate when HR has NOT yet scheduled the meeting.
  2. Check the task list as a Candidate when HR HAS scheduled the meeting.
- **Expected Results**:
  1. When NOT scheduled: The button should display "Waiting Schedule" and remain disabled (`canAcknowledge` is false).
  2. When scheduled: The button updates to "Acknowledge" and becomes clickable, allowing the candidate to mark the step as completed.

## 5. Backend Integrations Verification
**Scenario 5: Check completion trigger cascades**
- **Pre-condition**: Active backend with task progression endpoints functional.
- **Steps**:
  1. Perform completes and skips via API or Frontend.
  2. Review the logs and backend database for task state (`status` toggling between IN_PROGRESS, COMPLETED).
- **Expected Results**:
  1. The DB trigger `checklists.calculate_completion()` efficiently propagates completed tasks up to updating the Candidate model to `ONBOARDED`.
  2. Fallback updates correctly flag `fallback_reason` and do not break checklist increments.
