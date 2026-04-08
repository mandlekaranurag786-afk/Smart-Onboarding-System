import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ITTaskStatus {
  task_id: number;
  candidate_name: string;
  status: 'pending' | 'completed' | 'in_progress' | 'overdue' | 'blocked';
  created_at: string;
  response_received_at?: string;
  responder_name?: string;
  responder_email?: string;
  days_pending: number;
}

export function useITTaskStatus(taskId: number | null) {
  const [taskStatus, setTaskStatus] = useState<ITTaskStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTaskStatus = useCallback(async () => {
    if (!taskId) {
      setTaskStatus(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/it-tasks/${taskId}/status`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch task status: ${response.status}`);
      }

      const data = await response.json();
      setTaskStatus(data);
    } catch (err) {
      console.error('Error fetching IT task status:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchTaskStatus();
  }, [fetchTaskStatus]);

  return {
    taskStatus,
    isLoading,
    error,
    refetch: fetchTaskStatus
  };
}

export async function manualOverrideITTask(taskId: number, newStatus: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus }),
    });

    if (!response.ok) {
      throw new Error(`Failed to override task: ${response.status}`);
    }

    return true;
  } catch (err) {
    console.error('Error overriding IT task:', err);
    return false;
  }
}
