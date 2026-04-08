"use client";

import React from 'react';
import { Clock, CheckCircle2, AlertTriangle, User, Calendar } from 'lucide-react';

export type ITTaskStatusType = 'pending' | 'completed' | 'in_progress' | 'overdue' | 'blocked';

interface ITTaskStatusBadgeProps {
  status: ITTaskStatusType;
  daysPending?: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ITTaskStatusBadge({ status, daysPending, size = 'md' }: ITTaskStatusBadgeProps) {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-3 py-1 text-xs',
    lg: 'px-4 py-1.5 text-sm'
  };

  const statusConfig = {
    pending: {
      label: 'Pending',
      icon: Clock,
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-700',
      borderColor: 'border-yellow-200',
      iconColor: 'text-yellow-600'
    },
    completed: {
      label: 'Completed',
      icon: CheckCircle2,
      bgColor: 'bg-green-100',
      textColor: 'text-green-700',
      borderColor: 'border-green-200',
      iconColor: 'text-green-600'
    },
    in_progress: {
      label: 'In Progress',
      icon: Clock,
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-700',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-600'
    },
    overdue: {
      label: 'Delayed',
      icon: AlertTriangle,
      bgColor: 'bg-red-100',
      textColor: 'text-red-700',
      borderColor: 'border-red-200',
      iconColor: 'text-red-600'
    },
    blocked: {
      label: 'Blocked',
      icon: AlertTriangle,
      bgColor: 'bg-gray-100',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      iconColor: 'text-gray-600'
    }
  };

  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-semibold ${sizeClasses[size]} ${config.bgColor} ${config.textColor} ${config.borderColor}`}>
      <Icon size={size === 'sm' ? 10 : size === 'md' ? 12 : 14} className={config.iconColor} />
      {config.label}
      {status === 'pending' && daysPending !== undefined && daysPending > 0 && (
        <span className="ml-1 opacity-75">({daysPending}d)</span>
      )}
    </span>
  );
}

interface ITTaskDetailProps {
  taskId: number;
  candidateName: string;
  status: ITTaskStatusType;
  createdAt: string;
  responseReceivedAt?: string;
  responderName?: string;
  responderEmail?: string;
  daysPending: number;
  onManualOverride?: () => void;
  isHRAdmin?: boolean;
}

export function ITTaskDetail({
  taskId,
  candidateName,
  status,
  createdAt,
  responseReceivedAt,
  responderName,
  responderEmail,
  daysPending,
  onManualOverride,
  isHRAdmin = false
}: ITTaskDetailProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-slate-800 text-sm">IT Equipment Allocation</h4>
          <p className="text-xs text-slate-500 mt-0.5">Task #{taskId}</p>
        </div>
        <ITTaskStatusBadge status={status} daysPending={daysPending} size="md" />
      </div>

      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2 text-slate-600">
          <Calendar size={14} className="text-slate-400" />
          <span className="font-medium">Created:</span>
          <span>{formatDate(createdAt)}</span>
        </div>

        {status === 'pending' && daysPending > 0 && (
          <div className="flex items-center gap-2 text-yellow-700 bg-yellow-50 px-2 py-1 rounded">
            <Clock size={14} />
            <span className="font-medium">Pending for {daysPending} day{daysPending !== 1 ? 's' : ''}</span>
          </div>
        )}

        {responseReceivedAt && (
          <div className="flex items-center gap-2 text-slate-600">
            <CheckCircle2 size={14} className="text-green-500" />
            <span className="font-medium">Responded:</span>
            <span>{formatDate(responseReceivedAt)}</span>
          </div>
        )}

        {responderName && (
          <div className="flex items-center gap-2 text-slate-600">
            <User size={14} className="text-slate-400" />
            <span className="font-medium">Responder:</span>
            <span>{responderName}</span>
            {responderEmail && (
              <span className="text-slate-400">({responderEmail})</span>
            )}
          </div>
        )}
      </div>

      {isHRAdmin && onManualOverride && (
        <div className="pt-2 border-t border-gray-100">
          <button
            onClick={onManualOverride}
            className="w-full px-3 py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Manual Override
          </button>
        </div>
      )}
    </div>
  );
}
