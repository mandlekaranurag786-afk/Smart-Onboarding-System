import { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ITTaskStatus {
  task_id: number;
  candidate_id: number;
  candidate_name: string;
  status: 'pending' | 'completed' | 'in_progress' | 'overdue' | 'blocked';
  created_at: string;
  response_received_at?: string;
  responder_name?: string;
  responder_email?: string;
  days_pending: number;
}

interface UseITTaskStatusOptions {
  onRemoteUpdate?: (status: ITTaskStatus) => void;
}

export function useITTaskStatus(taskId: number | null, options?: UseITTaskStatusOptions) {
  const [taskStatus, setTaskStatus] = useState<ITTaskStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const onRemoteUpdateRef = useRef(options?.onRemoteUpdate);

  useEffect(() => {
    onRemoteUpdateRef.current = options?.onRemoteUpdate;
  }, [options?.onRemoteUpdate]);

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

  useEffect(() => {
    if (!taskId) {
      return;
    }

    const eventSource = new EventSource(`${API_BASE_URL}/api/it-tasks/${taskId}/stream`);

    eventSource.addEventListener('task_update', (event) => {
      try {
        const nextStatus = JSON.parse((event as MessageEvent).data) as ITTaskStatus;
        setTaskStatus(nextStatus);
        setError(null);
        onRemoteUpdateRef.current?.(nextStatus);
      } catch (err) {
        console.error('Error parsing IT task stream event:', err);
      }
    });

    eventSource.onerror = () => {
      eventSource.close();
      void fetchTaskStatus();
    };

    return () => {
      eventSource.close();
    };
  }, [fetchTaskStatus, taskId]);

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
