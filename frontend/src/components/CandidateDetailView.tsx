"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, User, Mail, Briefcase, Calendar, CheckCircle2, Clock, 
  AlertTriangle, ChevronDown, ChevronUp, RefreshCw, Shield
} from 'lucide-react';
import { ITTaskStatusBadge, ITTaskDetail } from './ITTaskStatus';
import { useITTaskStatus, manualOverrideITTask } from '../hooks/useITTaskStatus';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Task {
  id: number;
  name: string;
  description?: string;
  task_type: string;
  owner: string;
  status: string;
  assigned_to_name?: string;
  due_date?: string;
  completed_date?: string;
  it_response_received_at?: string;
  it_responder_name?: string;
  it_responder_email?: string;
  created_at: string;
}

interface Candidate {
  id: number;
  name: string;
  email: string;
  department: string;
  role: string;
  joining_date: string;
  reporting_manager: string;
  status: string;
}

interface CandidateDetailViewProps {
  candidate: Candidate;
  onClose: () => void;
  isHRAdmin?: boolean;
}

export function CandidateDetailView({ candidate, onClose, isHRAdmin = false }: CandidateDetailViewProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null);
  const [selectedITTaskId, setSelectedITTaskId] = useState<number | null>(null);
  const { taskStatus, isLoading: isLoadingTaskStatus, refetch: refetchTaskStatus } = useITTaskStatus(
    selectedITTaskId,
    {
      onRemoteUpdate: async () => {
        await fetchCandidateTasks(false);
      },
    }
  );

  useEffect(() => {
    fetchCandidateTasks();
  }, [candidate.id]);

  const fetchCandidateTasks = async (showLoader = true) => {
    if (showLoader) {
      setIsLoading(true);
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/${candidate.id}/progress`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const data = await response.json();
      setTasks(data.tasks || []);
      
      // Auto-select first IT task if exists
      const itTask = data.tasks?.find((t: Task) => t.task_type === 'it_equipment_allocation');
      if (itTask) {
        setSelectedITTaskId(itTask.id);
      }
    } catch (error) {
      console.error('Error fetching candidate tasks:', error);
    } finally {
      if (showLoader) {
        setIsLoading(false);
      }
    }
  };

  const handleManualOverride = async () => {
    if (!selectedITTaskId) return;
    
    const confirmed = window.confirm(
      'Are you sure you want to manually mark this IT task as completed? This action cannot be undone.'
    );
    
    if (confirmed) {
      const success = await manualOverrideITTask(selectedITTaskId, 'completed');
      if (success) {
        await fetchCandidateTasks();
        await refetchTaskStatus();
        alert('Task status updated successfully!');
      } else {
        alert('Failed to update task status. Please try again.');
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 size={16} className="text-green-600" />;
      case 'in_progress':
        return <Clock size={16} className="text-blue-600" />;
      case 'pending':
        return <Clock size={16} className="text-yellow-600" />;
      default:
        return <AlertTriangle size={16} className="text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const calculateDaysPending = (createdAt: string) => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - created.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const itTasks = tasks.filter(t => t.task_type === 'it_equipment_allocation');

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
                <User size={32} />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{candidate.name}</h2>
                <div className="flex items-center gap-4 mt-2 text-sm text-white/90">
                  <span className="flex items-center gap-1">
                    <Mail size={14} />
                    {candidate.email}
                  </span>
                  <span className="flex items-center gap-1">
                    <Briefcase size={14} />
                    {candidate.role}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Candidate Info */}
          <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-slate-50 rounded-lg">
            <div>
              <p className="text-xs text-slate-500 font-semibold">Department</p>
              <p className="text-sm text-slate-800">{candidate.department}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold">Reporting Manager</p>
              <p className="text-sm text-slate-800">{candidate.reporting_manager}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold">Joining Date</p>
              <p className="text-sm text-slate-800">
                {new Date(candidate.joining_date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold">Status</p>
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getStatusColor(candidate.status)}`}>
                {candidate.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>

          {/* IT Task Status Section */}
          {itTasks.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                  <Shield size={20} className="text-blue-600" />
                  IT Equipment Allocation Status
                </h3>
                <button
                  onClick={() => {
                    fetchCandidateTasks();
                    refetchTaskStatus();
                  }}
                  className="text-blue-600 hover:text-blue-700 transition-colors"
                  title="Refresh"
                >
                  <RefreshCw size={18} />
                </button>
              </div>

              {isLoadingTaskStatus ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw size={24} className="animate-spin text-blue-600" />
                </div>
              ) : taskStatus ? (
                <ITTaskDetail
                  taskId={taskStatus.task_id}
                  candidateName={taskStatus.candidate_name}
                  status={taskStatus.status}
                  createdAt={taskStatus.created_at}
                  responseReceivedAt={taskStatus.response_received_at}
                  responderName={taskStatus.responder_name}
                  responderEmail={taskStatus.responder_email}
                  daysPending={taskStatus.days_pending}
                  onManualOverride={isHRAdmin ? handleManualOverride : undefined}
                  isHRAdmin={isHRAdmin}
                />
              ) : (
                <div className="text-center py-4 text-slate-500 text-sm">
                  No IT task status available
                </div>
              )}
            </div>
          )}

          {/* All Tasks */}
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4">All Tasks</h3>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw size={24} className="animate-spin text-blue-600" />
              </div>
            ) : tasks.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                No tasks found for this candidate
              </div>
            ) : (
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors"
                  >
                    <div
                      className="p-4 cursor-pointer flex items-center justify-between"
                      onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(task.status)}
                        <div className="flex-1">
                          <h4 className="font-semibold text-sm text-slate-800">{task.name}</h4>
                          <p className="text-xs text-slate-500">
                            Owner: {task.owner} {task.assigned_to_name && `• Assigned to: ${task.assigned_to_name}`}
                          </p>
                        </div>
                        {task.task_type === 'it_equipment_allocation' && (
                          <ITTaskStatusBadge
                            status={task.status as any}
                            daysPending={calculateDaysPending(task.created_at)}
                            size="sm"
                          />
                        )}
                      </div>
                      {expandedTaskId === task.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>

                    <AnimatePresence>
                      {expandedTaskId === task.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="border-t border-gray-200 bg-slate-50 px-4 py-3"
                        >
                          <div className="space-y-2 text-xs">
                            {task.description && (
                              <p className="text-slate-600">{task.description}</p>
                            )}
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <span className="font-semibold text-slate-700">Task Type:</span>
                                <span className="ml-2 text-slate-600">{task.task_type}</span>
                              </div>
                              <div>
                                <span className="font-semibold text-slate-700">Status:</span>
                                <span className="ml-2 text-slate-600">{task.status}</span>
                              </div>
                              {task.due_date && (
                                <div>
                                  <span className="font-semibold text-slate-700">Due Date:</span>
                                  <span className="ml-2 text-slate-600">
                                    {new Date(task.due_date).toLocaleDateString()}
                                  </span>
                                </div>
                              )}
                              {task.completed_date && (
                                <div>
                                  <span className="font-semibold text-slate-700">Completed:</span>
                                  <span className="ml-2 text-slate-600">
                                    {new Date(task.completed_date).toLocaleDateString()}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
