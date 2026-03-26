"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Briefcase, GitBranch, BarChart2, MessageSquare, Settings, 
  Search, Bell, Mail, Target, ChevronDown, Check, Clock, Bot, Plus, X, Rocket,
  LayoutDashboard, FileText, Workflow, PieChart, Send, Cog, CheckCircle2,
  AlertTriangle, Info, Shield, Database, Globe, Zap, Calendar,
  LogOut, Eye, EyeOff, Lock, ArrowRight, ListTodo
} from 'lucide-react';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Utility Functions
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
};

const createCandidate = async (candidateData: {
  name: string;
  email: string;
  department: string;
  role: string;
  joining_date: string;
  reporting_manager: string;
}) => {
  return apiRequest('/api/candidates/', {
    method: 'POST',
    body: JSON.stringify(candidateData),
  });
};

const fetchCandidates = async () => {
  return apiRequest('/api/candidates/');
};

const fetchStakeholders = async () => {
  return apiRequest('/api/stakeholders/');
};

type SlotOption = {
  name: string;
  role: string;
  date: string;
  time: string;
};

type ScheduleSlotsResponse = {
  candidate_name: string;
  meeting_type: string;
  assigned_to: string;
  selected_interviewer?: string;
  smart_suggestion: SlotOption | null;
  available_slots: SlotOption[];
  all_interviewers: { name: string; role: string }[];
};

type BookMeetingResponse = {
  message: string;
  booking: {
    candidate_name: string;
    meeting_type: string;
    interviewer_name: string;
    interviewer_role: string;
    date: string;
    time: string;
    status: string;
    booked_by: string;
    booked_at: string;
    meeting_link: string;
  };
};

const fetchScheduleSlots = async (params: {
  candidate_name: string;
  meeting_type: string;
  interviewer_name?: string;
}) => {
  const search = new URLSearchParams({
    candidate_name: params.candidate_name,
    meeting_type: params.meeting_type,
  });
  if (params.interviewer_name) {
    search.set('interviewer_name', params.interviewer_name);
  }
  return apiRequest(`/api/schedule/slots?${search.toString()}`) as Promise<ScheduleSlotsResponse>;
};

const fetchScheduledMeetings = async (candidateName: string) => {
  const search = new URLSearchParams({ candidate_name: candidateName });
  return apiRequest(`/api/schedule/meetings?${search.toString()}`) as Promise<{ meetings: any[] }>;
};

const bookMeeting = async (payload: {
  candidate_name: string;
  meeting_type: string;
  interviewer_name: string;
  date: string;
  time: string;
  booked_by?: string;
}) => {
  return apiRequest('/api/schedule/book', {
    method: 'POST',
    body: JSON.stringify(payload),
  }) as Promise<BookMeetingResponse>;
};

// Mock user database — replace with real API later
const MOCK_USERS: Record<string, { password: string; role: 'HR' | 'Candidate'; name: string; department?: string }> = {
  'hr@konverge.ai': { password: 'admin123', role: 'HR', name: 'HR Admin' },
  'mohini@konverge.ai': { password: 'welcome1', role: 'HR', name: 'Mohini Moghe' },
  'tejas@konverge.ai': { password: 'welcome1', role: 'Candidate', name: 'Tejas Ninanwe', department: 'Delivery and Practices > Artificial Intelligence' },
  'mugdha@konverge.ai': { password: 'welcome1', role: 'Candidate', name: 'Mugdha', department: 'Delivery and Practices > Artificial Intelligence' },
};

// Role-based navigation — candidates see a completely different sidebar
const HR_NAV_ITEMS = [
  { label: 'Employees' as const, icon: Users },
  { label: 'Workflow' as const, icon: Workflow },
  { label: 'Analytics' as const, icon: PieChart },
  { label: 'Chat' as const, icon: MessageSquare },
  { label: 'System Settings' as const, icon: Cog },
] as const;

const CANDIDATE_NAV_ITEMS = [
  { label: 'My Dashboard' as const, icon: LayoutDashboard },
  { label: 'Chat' as const, icon: MessageSquare },
  { label: 'Help & Support' as const, icon: Info },
] as const;

type TabType = 'Employees' | 'Workflow' | 'Analytics' | 'Chat' | 'System Settings' | 'My Dashboard' | 'Help & Support';

const TASKS_DETAIL = [
  { id: 1, title: 'Document Signing', desc: 'Offer letter, NDA, company policies', owner: 'HR' },
  { id: 2, title: 'Work Profile Builder', desc: 'Candidate fills complete profile', owner: 'Candidate' },
  { id: 3, title: 'Asset Assignment', desc: 'Laptop, mouse, accessories', owner: 'IT' },
  { id: 4, title: 'Account Provisioning', desc: 'Keka, Teams, SharePoint access', owner: 'System' },
  { id: 5, title: 'Meeting: HR (Mohini)', desc: 'Company policies walkthrough', owner: 'HR' },
  { id: 6, title: 'Meeting: Infrastructure Team', desc: 'Resource & Access setup briefing', owner: 'IT' },
  { id: 7, title: 'Meeting: Practice Head (Kalpit)', desc: 'Technical roadmap & expectations', owner: 'Manager' },
  { id: 8, title: 'Group Access Provisioning', desc: 'Teams/SharePoint groups', owner: 'IT' },
  { id: 9, title: 'Karma Portal Acknowledgment', desc: 'Candidate confirms completion', owner: 'Candidate' },
];

// Department-specific task templates
const DEPARTMENT_TEMPLATES: Record<string, number[]> = {
  'Delivery and Practices > Artificial Intelligence': [1, 2, 3, 4, 5, 6, 7, 8, 9],
  'HR': [1, 2, 3, 4, 5, 9],
  'Sales': [1, 2, 3, 4, 5, 7, 9],
};

const ROLE_MAPPINGS: Record<string, Record<string, string>> = {
  'Delivery and Practices > Artificial Intelligence': {
    'HR': 'Mohini Moghe',
    'Infrastructure': 'Infrastructure Team',
    'Practice Head': 'Kalpit',
    'Reporting Manager': 'Sumit Patil'
  },
  'HR': {
    'HR': 'Mohini Moghe',
    'Reporting Manager': 'Mohini Moghe'
  },
  'Sales': {
    'HR': 'Mohini Moghe',
    'Reporting Manager': 'Ambar Gosavi'
  }
};

// Simulated Organization Chart for Role-Based Resolution
const ORG_CHART: Record<string, Record<string, string>> = {
  'AI': {
    'Practice Head': 'Kalpit',
    'Engineering Manager': 'Sumit Patil',
    'Delivery Head': 'Sajal'
  },
  'HR': {
    'Practice Head': 'Mohini Moghe',
    'Senior Manager': 'Mohini Moghe'
  },
  'Sales': {
    'Practice Head': 'Ambar Gosavi',
    'Sales Lead': 'Ambar Gosavi'
  }
};

const getMeetingTypeFromTaskTitle = (taskTitle: string) => {
  const normalizedTitle = taskTitle.toLowerCase();
  if (normalizedTitle.includes('hr')) return 'HR Introduction';
  if (normalizedTitle.includes('practice head') || normalizedTitle.includes('delivery head')) {
    return 'Delivery Head Introduction';
  }
  return 'Manager Introduction';
};

const getTaskIdFromMeetingType = (meetingType: string) => {
  const normalizedType = meetingType.toLowerCase();
  if (normalizedType.includes('hr')) return 5;
  if (normalizedType.includes('delivery')) return 7;
  if (normalizedType.includes('manager')) return 6;
  return null;
};

const slotKey = (slot: SlotOption) => `${slot.name}|${slot.date}|${slot.time}`;

export default function AnalyticsDashboard() {
  // AUTH STATES
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<{ email: string; role: 'HR' | 'Candidate'; name: string } | null>(null);

  // DASHBOARD STATES
  const [userRole, setUserRole] = useState<'HR'|'Candidate'>('HR');
  const [activeTab, setActiveTab] = useState<TabType>('Analytics');
  const [currentTime, setCurrentTime] = useState("");
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', joinDate: '', department: '', manager: '', position: 'SDE', location: 'Pune' });
  const [sortOrder, setSortOrder] = useState<'asc'|'desc'>('asc');
  const [filterDate, setFilterDate] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [directorySearch, setDirectorySearch] = useState('');
  const [toasts, setToasts] = useState<{id: number; message: string; type: 'success' | 'info' | 'warning'}[]>([]);

  const showToast = useCallback((message: string, type: 'success' | 'info' | 'warning' = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);
  
  // Settings States
  const [settings, setSettings] = useState({ emailParams: true, slaAlerts: true, ragEnabled: true });
  // Chat States
  const [activeChatId, setActiveChatId] = useState<number | null>(1);
  // Selected candidate to expand task list
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null);

  // Smart Onboarding States
  const [skippedTasks, setSkippedTasks] = useState<Record<number, number[]>>({});
  const [scheduledMeetings, setScheduledMeetings] = useState<Record<number, Record<number, {
    slot: string;
    interviewerName: string;
    date: string;
    time: string;
    meetingType: string;
    meetingLink: string;
  }>>>({});
  const [schedulingTask, setSchedulingTask] = useState<{ candidateId: number, taskId: number } | null>(null);
  const [slotsData, setSlotsData] = useState<ScheduleSlotsResponse | null>(null);
  const [selectedInterviewerName, setSelectedInterviewerName] = useState('');
  const [selectedSlotId, setSelectedSlotId] = useState('');
  const [isScheduleLoading, setIsScheduleLoading] = useState(false);
  const [isBookingMeeting, setIsBookingMeeting] = useState(false);
  const [scheduleError, setScheduleError] = useState('');

  const toggleSkipTask = (candidateId: number, taskId: number) => {
    setSkippedTasks(prev => {
      const current = prev[candidateId] || [];
      if (current.includes(taskId)) {
        return { ...prev, [candidateId]: current.filter(id => id !== taskId) };
      } else {
        return { ...prev, [candidateId]: [...current, taskId] };
      }
    });
    showToast(`Task status updated for candidate.`, 'info');
  };

  const getTasksForCandidate = (candidate: any) => {
    const templateIds = DEPARTMENT_TEMPLATES[candidate.department] || [1, 2, 3, 4, 5, 9];
    return templateIds.map(id => {
      const task = TASKS_DETAIL.find(t => t.id === id);
      if (task?.title.includes('Reporting Manager') || task?.title.includes('Manager')) {
        return { ...task, title: `Meeting: ${candidate.manager} (Manager)` };
      }
      return task || { id, title: 'Unknown Task', desc: '', owner: 'System' };
    });
  };

  // Initial candidate records - will be loaded from API
  const [candidates, setCandidates] = useState<any[]>([]);

  // Derived sorted and filtered candidates
  const filteredNavCandidates = [...candidates]
    .filter(c => {
      if (!filterDate) return true;
      // Convert HTML5 date 'YYYY-MM-DD' to 'MM/DD/YYYY' to match candidate records
      const [year, month, day] = filterDate.split('-');
      const formattedFilter = `${month}/${day}/${year}`;
      return c.date === formattedFilter;
    })
    .sort((a, b) => {
      return sortOrder === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
    });

  const toggleSort = () => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');

  useEffect(() => {
    // Format date like "July 24, 2020, 4:30 PM"
    const updateTime = () => {
      const now = new Date();
      const options: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true };
      setCurrentTime(now.toLocaleString('en-US', options));
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  // Load candidates from API
  const loadCandidates = async () => {
    try {
      const data = await fetchCandidates();
      // Transform API response to match frontend format
      const transformedCandidates = data.map((candidate: any) => ({
        id: candidate.id,
        name: candidate.name,
        position: candidate.role,
        department: candidate.department,
        manager: candidate.reporting_manager,
        date: new Date(candidate.joining_date).toLocaleDateString('en-US', {
          month: '2-digit',
          day: '2-digit',
          year: 'numeric'
        }),
        progress: candidate.completion_percentage,
        tasksCompleted: candidate.completed_tasks,
        totalTasks: candidate.total_tasks,
        status: candidate.status
      }));

      const scheduledMeetingMap: Record<number, Record<number, {
        slot: string;
        interviewerName: string;
        date: string;
        time: string;
        meetingType: string;
        meetingLink: string;
      }>> = {};

      await Promise.all(
        transformedCandidates.map(async (candidate: any) => {
          try {
            const meetingsResponse = await fetchScheduledMeetings(candidate.name);
            for (const meeting of meetingsResponse.meetings || []) {
              const mappedTaskId = getTaskIdFromMeetingType(meeting.meeting_type || '');
              if (!mappedTaskId) continue;
              if (!scheduledMeetingMap[candidate.id]) {
                scheduledMeetingMap[candidate.id] = {};
              }
              scheduledMeetingMap[candidate.id][mappedTaskId] = {
                slot: `${meeting.date}, ${meeting.time}`,
                interviewerName: meeting.interviewer_name,
                date: meeting.date,
                time: meeting.time,
                meetingType: meeting.meeting_type,
                meetingLink: meeting.meeting_link || '',
              };
            }
          } catch (error) {
            console.warn(`Could not fetch meetings for ${candidate.name}:`, error);
          }
        })
      );

      setCandidates(transformedCandidates);
      setScheduledMeetings(scheduledMeetingMap);
    } catch (error) {
      console.error('Error loading candidates:', error);
      const errorMessage = error instanceof TypeError && error.message === 'Failed to fetch'
        ? 'API unreachable. Please ensure the backend server is running on port 8000.'
        : 'Failed to load candidates from database';
      showToast(errorMessage, 'warning');
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadCandidates();
  }, []);

  const getSchedulingContext = () => {
    if (!schedulingTask) return null;
    const candidate = candidates.find(c => c.id === schedulingTask.candidateId);
    const task = TASKS_DETAIL.find(t => t.id === schedulingTask.taskId);
    if (!candidate || !task) return null;
    return { candidate, task };
  };

  const loadSchedulingOptions = useCallback(async (
    candidateName: string,
    taskTitle: string,
    interviewerName?: string
  ) => {
    setIsScheduleLoading(true);
    setScheduleError('');
    try {
      const meetingType = getMeetingTypeFromTaskTitle(taskTitle);
      const response = await fetchScheduleSlots({
        candidate_name: candidateName,
        meeting_type: meetingType,
        interviewer_name: interviewerName,
      });
      setSlotsData(response);
      setSelectedInterviewerName(response.selected_interviewer || interviewerName || response.assigned_to);
      const defaultSlot = response.smart_suggestion || response.available_slots[0] || null;
      setSelectedSlotId(defaultSlot ? slotKey(defaultSlot) : '');
    } catch (error) {
      console.error('Error loading schedule slots:', error);
      setSlotsData(null);
      setSelectedSlotId('');
      setScheduleError(error instanceof Error ? error.message : 'Unable to load scheduling data.');
    } finally {
      setIsScheduleLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!schedulingTask) {
      setSlotsData(null);
      setSelectedInterviewerName('');
      setSelectedSlotId('');
      setScheduleError('');
      return;
    }
    const candidate = candidates.find(c => c.id === schedulingTask.candidateId);
    const task = TASKS_DETAIL.find(t => t.id === schedulingTask.taskId);
    if (!candidate || !task) return;
    loadSchedulingOptions(candidate.name, task.title);
  }, [schedulingTask, candidates, loadSchedulingOptions]);

  const handleInterviewerChange = async (name: string) => {
    const context = getSchedulingContext();
    if (!context) return;
    setSelectedInterviewerName(name);
    await loadSchedulingOptions(context.candidate.name, context.task.title, name);
  };

  const scheduleMeetingForSlot = async (slot: SlotOption | null) => {
    if (!slot) {
      showToast('Please select a valid available slot.', 'warning');
      return;
    }
    const context = getSchedulingContext();
    if (!context) {
      showToast('Could not resolve candidate/task for scheduling.', 'warning');
      return;
    }

    setIsBookingMeeting(true);
    try {
      const meetingType = getMeetingTypeFromTaskTitle(context.task.title);
      const response = await bookMeeting({
        candidate_name: context.candidate.name,
        meeting_type: meetingType,
        interviewer_name: slot.name,
        date: slot.date,
        time: slot.time,
        booked_by: loggedInUser?.name || 'HR',
      });

      setScheduledMeetings(prev => ({
        ...prev,
        [context.candidate.id]: {
          ...(prev[context.candidate.id] || {}),
          [context.task.id]: {
            slot: `${response.booking.date}, ${response.booking.time}`,
            interviewerName: response.booking.interviewer_name,
            date: response.booking.date,
            time: response.booking.time,
            meetingType: response.booking.meeting_type,
            meetingLink: response.booking.meeting_link || '',
          }
        }
      }));

      showToast(
        `Meeting scheduled with ${response.booking.interviewer_name} on ${response.booking.date} at ${response.booking.time}`,
        'success'
      );
      setSchedulingTask(null);
      await loadCandidates();
    } catch (error) {
      console.error('Error booking meeting:', error);
      showToast(error instanceof Error ? error.message : 'Failed to book meeting.', 'warning');
    } finally {
      setIsBookingMeeting(false);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAdding(true);

    try {
      // Prepare data for API
      const candidateData = {
        name: formData.name,
        email: formData.email,
        department: formData.department,
        role: formData.position,
        joining_date: formData.joinDate, // Already in YYYY-MM-DD format
        reporting_manager: formData.manager,
      };

      // Call backend API
      const result = await createCandidate(candidateData);

      // Refresh candidates list
      await loadCandidates();

      // Reset form and close modal
      setIsAdding(false);
      setIsAddModalOpen(false);
      setFormData({ name: '', email: '', joinDate: '', department: '', manager: '', position: 'SDE', location: 'Pune' });

      showToast(`✅ ${result.name} onboarded successfully! LangGraph workflow triggered with 9-task checklist.`, 'success');
    } catch (error) {
      console.error('Error creating candidate:', error);
      setIsAdding(false);
      const errorMessage = error instanceof TypeError && error.message === 'Failed to fetch'
        ? 'API unreachable. Unable to create candidate. Ensure backend is running.'
        : `❌ Failed to onboard candidate: ${error instanceof Error ? error.message : 'Unknown error'}`;
      showToast(errorMessage, 'warning');
    }
  };

  const handleGenericAction = (message: string) => {
    showToast(message, 'info');
  };

  // LOGIN HANDLER
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setIsLoggingIn(true);

    setTimeout(() => {
      const user = MOCK_USERS[loginEmail.toLowerCase()];
      if (!user || user.password !== loginPassword) {
        setLoginError('Invalid email or password. Please try again.');
        setIsLoggingIn(false);
        return;
      }

      setLoggedInUser({ email: loginEmail.toLowerCase(), role: user.role, name: user.name });
      setUserRole(user.role);
      setActiveTab(user.role === 'HR' ? 'Analytics' : 'My Dashboard');
      if (user.role === 'Candidate') {
        const cand = candidates.find(c => c.name === user.name);
        if (cand) setActiveChatId(cand.id);
      } else {
        setActiveChatId(1);
      }
      setIsLoggedIn(true);
      setIsLoggingIn(false);
      setLoginEmail('');
      setLoginPassword('');
    }, 1200);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setLoggedInUser(null);
    setUserRole('HR');
    setActiveTab('Analytics');
    setLoginEmail('');
    setLoginPassword('');
    setLoginError('');
  };

  const pageVariants: any = {
    initial: { opacity: 0, y: 15 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
    exit: { opacity: 0, y: -15, transition: { duration: 0.2 } }
  };

  // ═══════════════════════════════════════════════════════
  // LOGIN SCREEN
  // ═══════════════════════════════════════════════════════
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#0f172a]">
        {/* Animated gradient background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a]"></div>
          <motion.div 
            animate={{ x: [0, 30, 0], y: [0, -20, 0] }} 
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute top-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
          />
          <motion.div 
            animate={{ x: [0, -20, 0], y: [0, 30, 0] }} 
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-20 right-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"
          />
          <motion.div 
            animate={{ scale: [1, 1.2, 1] }} 
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl"
          />
        </div>

        {/* Login Card */}
        <motion.div 
          initial={{ opacity: 0, y: 30, scale: 0.95 }} 
          animate={{ opacity: 1, y: 0, scale: 1 }} 
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="relative z-10 w-full max-w-md mx-4"
        >
          {/* Brand Header */}
          <motion.div 
            initial={{ opacity: 0, y: -10 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ delay: 0.2 }}
            className="text-center mb-10"
          >
            <div className="flex items-center justify-center gap-4 mb-4">
              <img src="/konverge-logo.png" alt="Konverge AI" className="h-10 w-auto object-contain" />
              <div className="w-[1px] h-8 bg-white/20 mx-1 hidden xs:block"></div>
              <span className="text-3xl font-black tracking-tight text-white">OnboardIQ</span>
            </div>
            <p className="text-sm text-slate-400 font-medium">AI-Powered Onboarding Platform by <span className="text-blue-400 font-bold">KONVERGE.AI</span></p>
          </motion.div>

          {/* Login Form Card */}
          <div className="bg-white/[0.07] backdrop-blur-xl rounded-3xl border border-white/10 p-10 shadow-2xl">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-white tracking-tight">Welcome back</h2>
              <p className="text-sm text-slate-400 mt-1">Sign in to access your dashboard</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Email Address</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    type="email" 
                    required
                    value={loginEmail}
                    onChange={(e) => { setLoginEmail(e.target.value); setLoginError(''); }}
                    placeholder="you@konverge.ai"
                    className="w-full bg-white/[0.06] border border-white/10 rounded-xl pl-11 pr-4 py-3.5 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all font-medium"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Password</label>
                <div className="relative">
                  <Lock size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={loginPassword}
                    onChange={(e) => { setLoginPassword(e.target.value); setLoginError(''); }}
                    placeholder="Enter your password"
                    className="w-full bg-white/[0.06] border border-white/10 rounded-xl pl-11 pr-12 py-3.5 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all font-medium"
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors">
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <AnimatePresence>
                {loginError && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }} 
                    animate={{ opacity: 1, height: 'auto' }} 
                    exit={{ opacity: 0, height: 0 }}
                    className="flex items-center gap-2 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs font-semibold"
                  >
                    <AlertTriangle size={14} /> {loginError}
                  </motion.div>
                )}
              </AnimatePresence>

              <button 
                type="submit"
                disabled={isLoggingIn}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white py-4 rounded-xl font-bold text-sm transition-all duration-300 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoggingIn ? (
                  <><Clock size={16} className="animate-spin" /> Authenticating...</>
                ) : (
                  <>Sign In <ArrowRight size={16} /></>
                )}
              </button>
            </form>
          </div>

          {/* Demo Credentials Hint */}
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            transition={{ delay: 0.6 }}
            className="mt-8 bg-white/[0.04] backdrop-blur rounded-2xl border border-white/5 p-6"
          >
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Demo Credentials</p>
            <div className="grid grid-cols-2 gap-4">
              <div 
                onClick={() => { setLoginEmail('hr@konverge.ai'); setLoginPassword('admin123'); setLoginError(''); }}
                className="cursor-pointer p-3 rounded-xl bg-white/[0.04] border border-white/5 hover:border-blue-500/30 hover:bg-blue-500/5 transition-all group"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <Shield size={10} className="text-blue-400" />
                  </div>
                  <span className="text-xs font-bold text-blue-400 group-hover:text-blue-300">HR Admin</span>
                </div>
                <p className="text-[10px] text-slate-500 font-mono">hr@konverge.ai</p>
                <p className="text-[10px] text-slate-600 font-mono">admin123</p>
              </div>
              <div 
                onClick={() => { setLoginEmail('tejas@konverge.ai'); setLoginPassword('welcome1'); setLoginError(''); }}
                className="cursor-pointer p-3 rounded-xl bg-white/[0.04] border border-white/5 hover:border-emerald-500/30 hover:bg-emerald-500/5 transition-all group"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Users size={10} className="text-emerald-400" />
                  </div>
                  <span className="text-xs font-bold text-emerald-400 group-hover:text-emerald-300">Candidate</span>
                </div>
                <p className="text-[10px] text-slate-500 font-mono">tejas@konverge.ai</p>
                <p className="text-[10px] text-slate-600 font-mono">welcome1</p>
              </div>
            </div>
          </motion.div>

          {/* Footer */}
          <p className="text-center text-[10px] text-slate-600 mt-8 font-medium">© 2026 KONVERGE.AI — All rights reserved</p>
        </motion.div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════
  // MAIN DASHBOARD (after login)
  // ═══════════════════════════════════════════════════════
  return (
    <div className="min-h-screen flex bg-[#f5f8fa] font-sans text-slate-800">
      
      {/* SIDEBAR: Match dark blue styling */}
      <aside className="w-64 bg-[#2b3553] text-white flex flex-col shrink-0">
        
        {/* User Profile */}
        <div className="flex flex-col items-center pt-8 pb-6 border-b border-white/10">
          <div className="w-20 h-20 rounded-full bg-slate-400 border-2 border-[#2b3553] shadow-md mb-4 overflow-hidden flex items-center justify-center bg-gradient-to-br from-indigo-500 to-blue-600">
            <span className="text-2xl font-black tracking-tighter text-white">K</span>
          </div>
          <h2 className="text-sm font-bold tracking-widest uppercase">KONVERGE.AI</h2>
        </div>

        {/* Navigation — role-based */}
        <nav className="flex-1 py-4 space-y-0.5">
          {(userRole === 'HR' ? HR_NAV_ITEMS : CANDIDATE_NAV_ITEMS).map(({ label, icon: Icon }) => (
            <button
              key={label}
              onClick={() => setActiveTab(label)}
              className={`w-full flex items-center gap-3 px-6 py-3 text-[13px] font-semibold tracking-wide transition-all duration-200 relative
                ${activeTab === label 
                  ? 'bg-white/10 text-white border-l-[3px] border-blue-400 pl-[21px]' 
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border-l-[3px] border-transparent pl-[21px]'}`}
            >
              <Icon size={18} className={activeTab === label ? 'text-blue-400' : ''} />
              {label}
            </button>
          ))}
        </nav>

        {/* Logo Mark + Logout */}
        <div className="mt-auto">
          {/* Logged-in User Info */}
          <div className="px-5 py-4 border-t border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold shadow-md shrink-0">
                {loggedInUser?.name.split(' ').map(n => n[0]).join('') || 'U'}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-white truncate">{loggedInUser?.name || 'User'}</p>
                <p className="text-[10px] text-slate-400 truncate">{loggedInUser?.email}</p>
              </div>
            </div>
          </div>

          <div className="px-5 pb-4">
            <button 
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-xl text-xs font-bold transition-all duration-200 border border-white/5 hover:border-red-500/20"
            >
              <LogOut size={14} /> Sign Out
            </button>
          </div>

          <div className="px-5 pb-6 flex items-center gap-3">
            <img src="/konverge-logo.png" alt="Konverge AI Logo" className="h-7 w-auto object-contain opacity-90" />
            <div className="w-[1px] h-5 bg-white/10 mx-0.5"></div>
            <span className="text-xl font-black tracking-tight text-white">OnboardIQ</span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden">
        
        {/* TOP NAVBAR */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <div className="flex items-center text-slate-400 w-80 relative bg-slate-50 rounded-xl px-1">
              <Search size={16} className="absolute left-3 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search candidates, settings..." 
                className="w-full pl-9 pr-4 py-2 text-sm bg-transparent border-none focus:outline-none focus:ring-0 text-slate-700 placeholder:text-slate-400 font-medium"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-5 text-sm text-slate-500">
            <span className="text-xs font-semibold text-slate-400 tracking-tight hidden xl:block">{currentTime}</span>
            
            <div className="flex items-center gap-1 border-l border-gray-100 pl-4">
              <button onClick={() => setActiveTab('Chat')} className="p-2 hover:bg-slate-50 rounded-lg relative transition-all hover:text-slate-700">
                <Mail size={18} />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              </button>
              <button onClick={() => setActiveTab('Chat')} className="p-2 hover:bg-slate-50 rounded-lg relative transition-all hover:text-slate-700">
                <MessageSquare size={18} />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full"></span>
              </button>
              <button onClick={() => showToast('No new notifications', 'info')} className="p-2 hover:bg-slate-50 rounded-lg transition-all hover:text-slate-700">
                <Bell size={18} />
              </button>
              <button onClick={() => setActiveTab('System Settings')} className="p-2 hover:bg-slate-50 rounded-lg transition-all hover:text-slate-700">
                <Settings size={18} />
              </button>
            </div>
            
            {/* User Avatar */}
            <div className="flex items-center gap-3 border-l border-gray-100 pl-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                {loggedInUser?.name.split(' ').map(n => n[0]).join('') || 'U'}
              </div>
              <div className="hidden lg:block">
                <p className="text-xs font-bold text-slate-800 leading-tight">{loggedInUser?.name}</p>
                <p className="text-[10px] text-slate-400 font-medium">{loggedInUser?.role === 'HR' ? 'Human Resources' : 'New Joinee'}</p>
              </div>
            </div>
          </div>
        </header>

        {/* DASHBOARD CONTENT SWITCHER */}
        <div className="flex-1 overflow-y-auto p-8 bg-[#f5f8fa]">
          
          <AnimatePresence mode='wait'>
            {/* HR ONLY: Analytics Tab */}
            {activeTab === 'Analytics' && userRole === 'HR' && (
              <motion.div key="analytics" variants={pageVariants} initial="initial" animate="animate" exit="exit">
                <div className="flex justify-between items-end mb-8">
                  <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Analytics</h1>
                  <div className="flex gap-4 items-center">
                    <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                      <span className="text-xs font-bold text-slate-500">Date:</span>
                      <input 
                        type="date" 
                        value={filterDate}
                        onChange={(e) => setFilterDate(e.target.value)}
                        className="text-sm text-slate-700 outline-none cursor-pointer"
                      />
                      {filterDate && (
                        <button onClick={() => setFilterDate('')} className="text-slate-400 hover:text-red-500 ml-1">
                          <X size={14} />
                        </button>
                      )}
                    </div>
                    <button 
                      onClick={() => setIsAddModalOpen(true)}
                      className="bg-[#2b3553] hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition-transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg"
                    >
                      <Plus size={16} /> Add New Joinee
                    </button>
                  </div>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-6 gap-4 mb-8">
                  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1 min-h-[140px]">
                    <h3 className="text-sm font-bold text-slate-600 mb-2">Offers to Send</h3>
                    <p className="text-5xl font-bold text-slate-900">2</p>
                  </div>
                  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1">
                    <h3 className="text-sm font-bold text-slate-600 mb-2">Time to Accept</h3>
                    <div className="flex items-baseline gap-1">
                      <p className="text-5xl font-bold text-slate-900">&lt; 1</p>
                      <span className="text-sm font-medium text-slate-400">day</span>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1">
                    <h3 className="text-sm font-bold text-slate-600 mb-2">Time to Onboard</h3>
                    <div className="flex items-baseline gap-1">
                      <p className="text-5xl font-bold text-slate-900">1</p>
                      <span className="text-sm font-medium text-slate-400">day</span>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1">
                    <h3 className="text-sm font-bold text-slate-600 mb-2">Onboarded</h3>
                    <p className="text-5xl font-bold text-slate-900">{candidates.filter(c => c.progress === 100).length}</p>
                  </div>
                  <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1 relative">
                    <h3 className="text-sm font-bold text-slate-600 mb-3 absolute top-5 text-center w-full">Offer Acceptance<br/>Ratio</h3>
                    <div className="relative w-16 h-16 mt-6">
                      <svg viewBox="0 0 36 36" className="w-16 h-16 text-blue-500">
                        <path className="text-gray-100" strokeWidth="4" stroke="currentColor" fill="none"
                              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <path strokeWidth="4" strokeDasharray="100, 100" stroke="currentColor" fill="none"
                              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center text-xs font-bold">100%</div>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex flex-col items-center justify-center col-span-1 relative">
                    <h3 className="text-sm font-bold text-slate-600 absolute top-4">Applications received</h3>
                    <p className="text-2xl font-bold text-slate-900 mt-4 mb-0.5">24</p>
                    <p className="text-[10px] text-slate-400 mb-2 max-w-[100px] text-center leading-tight">Total amount of applications</p>
                    <div className="flex items-end gap-1 h-8 w-full px-2">
                      {[0, 0, 0, 1, 0, 2, 4, 7, 10].map((h, i) => (
                        <div key={i} className="w-full bg-blue-400 rounded-t-sm" style={{height: `${h*10}%`}}></div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Candidate List (Refactored to Cards per Sumit's suggestion) */}
                <div className="space-y-4">
                  {filteredNavCandidates.map((candidate) => {
                    const candidateTasks = getTasksForCandidate(candidate);
                    const skippedCount = (skippedTasks[candidate.id] || []).length;
                    const progress = Math.min(100, Math.round(((candidate.tasksCompleted + skippedCount) / candidateTasks.length) * 100));
                    const isExpanded = selectedCandidateId === candidate.id;

                    return (
                      <motion.div 
                        key={candidate.id}
                        layout
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`bg-white rounded-2xl border transition-all duration-300 ${isExpanded ? 'shadow-xl ring-2 ring-blue-100 border-blue-200' : 'shadow-sm border-gray-100 hover:border-blue-200 hover:shadow-md'}`}
                      >
                        <div 
                          onClick={() => setSelectedCandidateId(isExpanded ? null : candidate.id)}
                          className="p-6 cursor-pointer"
                        >
                          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                            {/* Candidate Basic Info */}
                            <div className="flex items-center gap-4">
                              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-blue-500/20">
                                {candidate.name.split(' ').map((n: string) => n[0]).join('')}
                              </div>
                              <div>
                                <h3 className="text-lg font-bold text-slate-800">{candidate.name}</h3>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-xs font-semibold text-slate-500">{candidate.position}</span>
                                  <span className="w-1 h-1 bg-slate-300 rounded-full"></span>
                                  <span className="text-xs font-semibold text-slate-400">{candidate.department.split('>').pop()}</span>
                                </div>
                              </div>
                            </div>

                            {/* Status & Manager */}
                            <div className="flex flex-wrap items-center gap-6 lg:gap-12">
                              <div className="space-y-1">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Reporting To</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-5 h-5 rounded-full bg-violet-100 flex items-center justify-center"><Users size={12} className="text-violet-600" /></div>
                                  <span className="text-sm font-bold text-slate-700">{candidate.manager}</span>
                                </div>
                              </div>
                              <div className="space-y-1">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Join Date</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center"><Calendar size={12} className="text-blue-600" /></div>
                                  <span className="text-sm font-bold text-slate-700">{candidate.date}</span>
                                </div>
                              </div>
                              <div className="space-y-1">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Current Status</p>
                                <span className={`inline-flex px-2.5 py-1 rounded-lg text-xs font-bold
                                  ${candidate.status === 'Onboarded' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : candidate.status === 'Onboarding Started' ? 'bg-blue-50 text-blue-600 border border-blue-100' : 'bg-amber-50 text-amber-600 border border-amber-100'}`}>
                                  {candidate.status}
                                </span>
                              </div>
                            </div>

                            {/* Progress Semi-Circle (Compact) */}
                            <div className="flex flex-col lg:flex-row items-center gap-4">
                              {/* Next Step Quick Action */}
                              {(() => {
                                const nextTaskIdx = candidate.tasksCompleted;
                                const nextTask = candidateTasks[nextTaskIdx];
                                if (!nextTask || nextTask.id > candidateTasks.length || !nextTask.title.toLowerCase().includes('meeting')) return null;
                                
                                const scheduled = scheduledMeetings[candidate.id]?.[nextTask.id];
                                if (scheduled) return (
                                  <div className="hidden lg:flex flex-col items-end mr-2">
                                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Scheduled</span>
                                    <span className="text-xs font-bold text-blue-600">{scheduled.slot}</span>
                                  </div>
                                );

                                return (
                                  <div className="hidden lg:flex items-center gap-3 pr-4 border-r border-slate-100">
                                    <div className="text-right">
                                      <p className="text-[10px] font-bold text-amber-500 uppercase tracking-widest">Action Required</p>
                                      <p className="text-xs font-bold text-slate-700">Schedule Interview</p>
                                    </div>
                                    <button 
                                      onClick={(e) => { e.stopPropagation(); setSchedulingTask({ candidateId: candidate.id, taskId: nextTask.id }); }}
                                      className="p-2 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                                    >
                                      <Calendar size={18} />
                                    </button>
                                  </div>
                                );
                              })()}

                              <div className="flex items-center gap-4 bg-slate-50 px-4 py-3 rounded-2xl border border-slate-100 min-w-[180px]">
                                <div className="relative w-10 h-10">
                                  <svg viewBox="0 0 36 36" className="w-10 h-10 -rotate-90">
                                    <circle cx="18" cy="18" r="16" fill="none" stroke="#e2e8f0" strokeWidth="4" />
                                    <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeDasharray={`${progress}, 100`} className="text-blue-500" />
                                  </svg>
                                  <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black">{progress}%</div>
                                </div>
                                <div className="flex flex-col">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Onboarding</span>
                                  <span className="text-sm font-black text-slate-800">{candidate.tasksCompleted + skippedCount}/{candidateTasks.length} <span className="text-[10px] text-slate-400">Tasks</span></span>
                                </div>
                                <ChevronDown size={18} className={`ml-auto text-slate-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
                              </div>
                            </div>
                          </div>
                        </div>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div 
                              initial={{ opacity: 0, height: 0 }} 
                              animate={{ opacity: 1, height: 'auto' }} 
                              exit={{ opacity: 0, height: 0 }} 
                              className="overflow-hidden border-t border-slate-100"
                            >
                              <div className="p-8 bg-slate-50/50">
                                <div className="flex justify-between items-center mb-6">
                                  <h4 className="text-sm font-bold text-slate-700 uppercase tracking-widest flex items-center gap-2">
                                    <ListTodo size={18} className="text-blue-600" />
                                    Journey Checklist
                                  </h4>
                                  <div className="flex gap-4">
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Verified</div>
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase"><div className="w-2 h-2 rounded-full bg-blue-500"></div> Pending</div>
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase"><div className="w-2 h-2 rounded-full bg-amber-500"></div> Skipped</div>
                                  </div>
                                </div>

                                <div className="flex flex-col gap-3">
                                  {candidateTasks.map((task, idx) => {
                                    const isSkipped = (skippedTasks[candidate.id] || []).includes(task.id);
                                    const isDone = idx < (candidate.tasksCompleted || 0);
                                    const scheduled = scheduledMeetings[candidate.id]?.[task.id];
                                    const isCurrent = idx === (candidate.tasksCompleted || 0) && !isSkipped;
                                    
                                    return (
                                      <div key={task.id} className={`group flex items-start gap-4 p-4 rounded-2xl border transition-all duration-200 
                                        ${isDone ? 'bg-white border-emerald-100' : isSkipped ? 'bg-amber-50/50 border-amber-100 opacity-80' : isCurrent ? 'bg-white border-blue-200 shadow-lg ring-2 ring-blue-50' : 'bg-white/50 border-gray-100 opacity-60'}`}>
                                        
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 font-extrabold text-sm shadow-sm
                                          ${isDone ? 'bg-emerald-500 text-white' : isSkipped ? 'bg-amber-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-blue-500/20' : 'bg-slate-100 text-slate-400'}`}>
                                          {isDone ? <Check size={18} /> : (idx + 1)}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                          <div className="flex items-center flex-wrap gap-2">
                                            <p className={`text-sm font-bold truncate ${isDone ? 'text-emerald-800' : isSkipped ? 'text-amber-800' : isCurrent ? 'text-blue-900' : 'text-slate-400'}`}>{task.title}</p>
                                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter
                                              ${task.owner === 'HR' ? 'bg-violet-100 text-violet-600' : task.owner === 'IT' ? 'bg-orange-100 text-orange-600' : task.owner === 'Candidate' ? 'bg-teal-100 text-teal-600' : task.owner === 'System' ? 'bg-slate-200 text-slate-600' : 'bg-blue-100 text-blue-600'}`}>
                                              {task.owner}
                                            </span>
                                          </div>
                                          <p className="text-[11px] text-slate-400 mt-1 leading-tight line-clamp-1">{task.desc}</p>
                                          
                                          {scheduled && (
                                            <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-blue-50 rounded-lg border border-blue-100">
                                              <Clock size={10} className="text-blue-500" />
                                              <span className="text-[10px] font-bold text-blue-600 truncate">{scheduled.slot} with {scheduled.interviewerName}</span>
                                            </div>
                                          )}

                                          {/* Action Buttons (Visible on Hover or for Next Step) */}
                                          <div className={`mt-3 flex items-center gap-2 transition-opacity duration-200 ${isCurrent ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                                            {!isDone && !isSkipped && task.title.toLowerCase().includes('meeting') && (
                                              <button 
                                                onClick={(e) => { e.stopPropagation(); setSchedulingTask({ candidateId: candidate.id, taskId: task.id }); }}
                                                className="px-3 py-1.5 bg-blue-600 text-white text-[10px] font-bold rounded-lg hover:bg-blue-700 transition-colors shadow-md shadow-blue-500/10 flex items-center gap-1.5"
                                              >
                                                <Calendar size={12} /> {scheduled ? 'Reschedule' : 'Schedule'}
                                              </button>
                                            )}
                                            {!isDone && (
                                              <button 
                                                onClick={(e) => { e.stopPropagation(); toggleSkipTask(candidate.id, task.id); }}
                                                className={`px-3 py-1.5 rounded-lg text-[10px] font-bold border transition-colors flex items-center gap-1.5
                                                  ${isSkipped ? 'bg-amber-100 border-amber-200 text-amber-700' : 'bg-slate-100 border-slate-200 text-slate-600 hover:bg-amber-50 hover:text-amber-600 hover:border-amber-200'}`}
                                              >
                                                <Zap size={12} /> {isSkipped ? 'Skipped' : 'Skip Step'}
                                              </button>
                                            )}
                                          </div>
                                        </div>

                                        <div className={`shrink-0 px-2 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest self-start mt-1
                                          ${isDone ? 'bg-emerald-50 text-emerald-600' : isSkipped ? 'bg-amber-50 text-amber-600' : isCurrent ? 'bg-blue-50 text-blue-600' : 'bg-gray-50 text-slate-300'}`}>
                                          {isDone ? 'Done' : isSkipped ? 'Skip' : isCurrent ? 'Next' : 'Pending'}
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    );
                  })}
                </div>

                {/* SCHEDULING MODAL (Refined for Smart Suggestions) */}
                <AnimatePresence>
                  {schedulingTask && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSchedulingTask(null)} className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" />
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden border border-blue-100"
                      >
                        <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-transparent">
                          <h3 className="text-xl font-bold text-slate-800">Schedule Onboarding Meeting</h3>
                          <p className="text-sm text-slate-500 mt-1">Select an interviewer and availability slot</p>
                        </div>
                        
                        <div className="p-6 space-y-6">
                          {isScheduleLoading && (
                            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 text-sm font-semibold text-slate-600">
                              Loading smart suggestion and available slots...
                            </div>
                          )}

                          {!isScheduleLoading && scheduleError && (
                            <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800">
                              <div className="flex items-center gap-2">
                                <AlertTriangle size={16} />
                                <span className="text-xs font-bold uppercase tracking-widest">Scheduling Error</span>
                              </div>
                              <p className="mt-2 text-sm">{scheduleError}</p>
                            </div>
                          )}

                          {!isScheduleLoading && !scheduleError && slotsData && (
                            <>
                              <div className="p-5 rounded-2xl text-white shadow-lg relative overflow-hidden bg-blue-600 shadow-blue-500/20">
                                <div className="relative z-10">
                                  <div className="flex items-center gap-2 mb-3">
                                    <Bot size={18} className="text-blue-200" />
                                    <span className="text-xs font-bold uppercase tracking-widest text-white/80">Smart Suggestion</span>
                                  </div>

                                  {slotsData.smart_suggestion ? (
                                    <div className="flex items-center justify-between gap-4">
                                      <div>
                                        <p className="text-lg font-bold">{slotsData.smart_suggestion.name}</p>
                                        <p className="text-xs text-white/70">{slotsData.smart_suggestion.role}</p>
                                        <p className="text-[11px] font-semibold mt-2">
                                          {slotsData.smart_suggestion.date} at {slotsData.smart_suggestion.time}
                                        </p>
                                      </div>
                                      <button
                                        onClick={() => scheduleMeetingForSlot(slotsData.smart_suggestion)}
                                        disabled={isBookingMeeting}
                                        className="px-4 py-2 bg-white text-blue-600 rounded-xl font-bold text-xs hover:bg-blue-50 transition-colors shadow-sm disabled:opacity-50"
                                      >
                                        {isBookingMeeting ? 'Booking...' : 'Quick Book'}
                                      </button>
                                    </div>
                                  ) : (
                                    <p className="text-sm text-blue-100">
                                      No smart suggestion available right now for this interviewer.
                                    </p>
                                  )}
                                </div>
                              </div>

                              <div className="space-y-4">
                                <div>
                                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Manual Selection</label>
                                  <select
                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-blue-500/20 outline-none"
                                    value={selectedInterviewerName}
                                    onChange={(e) => handleInterviewerChange(e.target.value)}
                                    disabled={isBookingMeeting}
                                  >
                                    {slotsData.all_interviewers.map((person) => (
                                      <option key={`${person.name}-${person.role}`} value={person.name}>
                                        {person.name} ({person.role})
                                      </option>
                                    ))}
                                  </select>
                                </div>

                                <div>
                                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Available Slots</label>
                                  {slotsData.available_slots.length === 0 ? (
                                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs font-semibold text-amber-700">
                                      No available slots for {selectedInterviewerName || 'selected interviewer'}.
                                    </div>
                                  ) : (
                                    <div className="grid grid-cols-2 gap-2">
                                      {slotsData.available_slots.map((slot) => {
                                        const selected = selectedSlotId === slotKey(slot);
                                        return (
                                          <button
                                            key={slotKey(slot)}
                                            onClick={() => setSelectedSlotId(slotKey(slot))}
                                            className={`px-3 py-2 border rounded-xl text-xs font-bold transition-all text-left ${
                                              selected
                                                ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                                                : 'border-slate-200 text-slate-700 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700'
                                            }`}
                                          >
                                            <div>{slot.date}</div>
                                            <div>{slot.time}</div>
                                          </button>
                                        );
                                      })}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </>
                          )}
                        </div>

                        <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-3">
                          <button
                            onClick={() => setSchedulingTask(null)}
                            className="flex-1 py-3 text-sm font-bold text-slate-500 hover:text-slate-700 transition-colors"
                            disabled={isBookingMeeting}
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => {
                              const selectedSlot = slotsData?.available_slots.find(slot => slotKey(slot) === selectedSlotId) || null;
                              scheduleMeetingForSlot(selectedSlot);
                            }}
                            disabled={isBookingMeeting || isScheduleLoading || !selectedSlotId}
                            className="flex-[2] py-3 bg-[#2b3553] text-white rounded-xl text-sm font-bold shadow-lg shadow-slate-900/10 hover:bg-slate-700 transition-all disabled:opacity-50"
                          >
                            {isBookingMeeting ? 'Booking...' : 'Confirm Booking'}
                          </button>
                        </div>
                      </motion.div>
                    </div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {/* CANDIDATE ONLY: My Dashboard Tab */}
            {activeTab === 'My Dashboard' && userRole === 'Candidate' && (
              <motion.div key="my-dashboard" variants={pageVariants} initial="initial" animate="animate" exit="exit">
                {(() => {
                  const myData = candidates.find(c => c.name === loggedInUser?.name) || candidates[0];
                  const completedCount = myData.tasksCompleted;
                  const totalCount = myData.totalTasks;
                  const progressPct = Math.round((completedCount / totalCount) * 100);
                  const circumference = 2 * Math.PI * 54;
                  const dashOffset = circumference - (progressPct / 100) * circumference;
                  const currentTask = TASKS_DETAIL[completedCount] || null;

                  return (
                    <div className="space-y-6">
                      {/* Hero Section */}
                      <div className="bg-white rounded-2xl p-8 border border-blue-100 shadow-sm relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-bl from-blue-50 to-indigo-50 rounded-bl-[120px] -z-0 opacity-60"></div>
                        <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-emerald-50 to-transparent rounded-tr-[60px] -z-0 opacity-40"></div>
                        
                        <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
                          <div className="relative shrink-0">
                            <svg width="140" height="140" className="-rotate-90">
                              <circle cx="70" cy="70" r="54" fill="none" stroke="#e2e8f0" strokeWidth="10" />
                              <motion.circle 
                                cx="70" cy="70" r="54" fill="none" stroke="url(#progressGradCandidate)" strokeWidth="10" strokeLinecap="round"
                                strokeDasharray={circumference}
                                initial={{ strokeDashoffset: circumference }}
                                animate={{ strokeDashoffset: dashOffset }}
                                transition={{ duration: 1.5 }}
                              />
                              <defs>
                                <linearGradient id="progressGradCandidate" x1="0%" y1="0%" x2="100%" y2="100%">
                                  <stop offset="0%" stopColor="#3b82f6" />
                                  <stop offset="100%" stopColor="#6366f1" />
                                </linearGradient>
                              </defs>
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                              <span className="text-3xl font-black text-slate-800">{progressPct}%</span>
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Complete</span>
                            </div>
                          </div>

                          <div className="flex-1">
                            <h2 className="text-2xl font-bold text-slate-800 mb-1">Welcome, {loggedInUser?.name}! 👋</h2>
                            <p className="text-slate-500 text-sm mb-6">{myData.department} &bull; Joined {myData.date}</p>
                            
                            <div className="grid grid-cols-3 gap-4">
                              <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                                <div className="flex items-center gap-2 mb-1"><CheckCircle2 size={16} className="text-emerald-600" /><span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">Done</span></div>
                                <p className="text-2xl font-black text-emerald-800">{completedCount}<span className="text-sm font-bold text-emerald-500">/{totalCount}</span></p>
                              </div>
                              <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                                <div className="flex items-center gap-2 mb-1"><Clock size={16} className="text-blue-600" /><span className="text-xs font-bold text-blue-700 uppercase tracking-wider">Next</span></div>
                                <p className="text-sm font-bold text-blue-800 leading-tight">{currentTask ? currentTask.title : 'All Done!'}</p>
                              </div>
                              <div className="bg-violet-50 rounded-xl p-4 border border-violet-100">
                                <div className="flex items-center gap-2 mb-1"><Users size={16} className="text-violet-600" /><span className="text-xs font-bold text-violet-700 uppercase tracking-wider">Manager</span></div>
                                <p className="text-sm font-bold text-violet-800 leading-tight">{myData.manager}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Checklist */}
                      <div className="space-y-3">
                        {TASKS_DETAIL.map((task) => {
                          const isDone = task.id <= completedCount;
                          const isCurrent = task.id === completedCount + 1;
                          return (
                            <div key={task.id} className={`flex items-center gap-4 p-5 rounded-2xl border transition-all ${isDone ? 'bg-emerald-50 border-emerald-100' : isCurrent ? 'bg-white border-blue-200 shadow-md ring-1 ring-blue-100' : 'bg-white opacity-50 border-gray-100'}`}>
                              <div className={`w-11 h-11 rounded-full flex items-center justify-center shrink-0 font-bold ${isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-400'}`}>
                                {isDone ? <Check size={20} /> : task.id}
                              </div>
                              <div className="flex-1">
                                <h4 className={`text-sm font-bold ${isDone ? 'text-emerald-800' : isCurrent ? 'text-blue-800' : 'text-slate-400'}`}>{task.title}</h4>
                                <p className="text-xs text-slate-400 mt-0.5">{task.desc}</p>
                              </div>
                              {isCurrent && task.owner === 'Candidate' && (
                                <button onClick={() => showToast(`"${task.title}" marked as complete!`, 'success')} className="px-5 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors">Complete Now</button>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {/* Help Card */}
                      <div className="bg-slate-900 rounded-2xl p-6 flex items-center justify-between text-white">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center"><Bot size={24} className="text-blue-400" /></div>
                          <div>
                            <h4 className="font-bold text-sm">Need help?</h4>
                            <p className="text-slate-400 text-xs mt-0.5">Ask our AI Assistant or contact HR directly</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => setIsChatOpen(true)} className="px-5 py-2.5 bg-blue-600 font-bold text-xs rounded-xl shadow-lg shadow-blue-500/20">Ask AI</button>
                          <button onClick={() => setActiveTab('Chat')} className="px-5 py-2.5 bg-white/10 font-bold text-xs rounded-xl border border-white/10">Contact HR</button>
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </motion.div>
            )}

            {/* HELP & SUPPORT TAB (Candidate Only) */}
            {activeTab === 'Help & Support' && userRole === 'Candidate' && (
              <motion.div key="help" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-8">
                <div>
                  <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Help & Support</h1>
                  <p className="text-sm text-slate-500 mt-1">Common questions about your onboarding journey</p>
                </div>

                {/* FAQ Section */}
                <div className="space-y-3">
                  {[
                    { q: 'How do I access VPN?', a: 'After your IT Account Provisioning task is complete, you will receive VPN credentials via email. Install GlobalProtect and use your Keka credentials to connect.' },
                    { q: 'What is the leave policy?', a: 'New joinees are eligible for 18 Casual Leaves, 12 Sick Leaves, and 15 Earned Leaves per year (pro-rated from date of joining). Leaves can be applied via Keka portal.' },
                    { q: 'When do I get my laptop?', a: 'Laptops are assigned during the "Asset Assignment" step. IT typically ships within 1-2 business days of your joining date.' },
                    { q: 'How do I access Teams/SharePoint?', a: 'After Account Provisioning (Step 4) and Group Access Provisioning (Step 8), you will receive invitations to all relevant Teams channels and SharePoint sites.' },
                    { q: 'Who is my SPOC for onboarding queries?', a: 'Your primary HR contact is Mohini. For IT issues, raise a ticket on ServiceNow. For team-specific queries, reach out to your Reporting Manager.' },
                    { q: 'What is the probation period?', a: 'The standard probation period at KONVERGE.AI is 6 months from the date of joining. Performance reviews are conducted quarterly.' },
                  ].map((faq, i) => (
                    <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                      <div className="p-5">
                        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 text-xs font-black">{i + 1}</div>
                          {faq.q}
                        </h3>
                        <p className="text-sm text-slate-500 mt-2 ml-8 leading-relaxed">{faq.a}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Contact HR */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                  <h3 className="text-sm font-bold text-slate-800 mb-4">Still have questions?</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center gap-3 p-4 bg-violet-50 rounded-xl border border-violet-100">
                      <Mail size={20} className="text-violet-600 shrink-0" />
                      <div>
                        <p className="text-xs font-bold text-violet-800">Email HR</p>
                        <p className="text-xs text-violet-600">hr@konverge.ai</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl border border-blue-100">
                      <MessageSquare size={20} className="text-blue-600 shrink-0" />
                      <div>
                        <p className="text-xs font-bold text-blue-800">Chat with HR</p>
                        <p className="text-xs text-blue-600">Via OnboardIQ Chat</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                      <Bot size={20} className="text-emerald-600 shrink-0" />
                      <div>
                        <p className="text-xs font-bold text-emerald-800">AI Assistant</p>
                        <p className="text-xs text-emerald-600">24/7 Available</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'Employees' && userRole === 'HR' && (
              <motion.div key="employees" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-6">
                <div className="flex justify-between items-end mb-8">
                  <div>
                    <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Employees Directory</h1>
                    <p className="text-sm text-slate-500 mt-1">Direct access to all registered personnel profiles.</p>
                  </div>
                  <div className="relative w-72">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input 
                      type="text" 
                      placeholder="Search by name or position..." 
                      className="w-full bg-white border border-gray-200 rounded-xl pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-blue-100 outline-none transition-all shadow-sm"
                      value={directorySearch}
                      onChange={(e) => setDirectorySearch(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {candidates.filter(c => 
                    c.name.toLowerCase().includes(directorySearch.toLowerCase()) || 
                    c.position.toLowerCase().includes(directorySearch.toLowerCase())
                  ).map(c => (
                    <motion.div whileHover={{ y: -4, boxShadow: "0px 10px 20px rgba(0,0,0,0.05)" }} key={c.id} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col items-center transition-all">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-xl font-bold mb-4 shadow-md">
                        {c.name.split(' ').map((n: string) => n[0]).join('')}
                      </div>
                      <h3 className="text-lg font-bold text-slate-800">{c.name}</h3>
                      <p className="text-blue-500 font-semibold text-xs mb-4 uppercase tracking-wider">{c.position}</p>
                      
                      <div className="w-full grid grid-cols-2 gap-2 pt-4 border-t border-gray-50 text-[11px]">
                         <div className="flex flex-col">
                           <span className="text-slate-400 font-bold uppercase tracking-tighter">Department</span>
                           <span className="text-slate-700 truncate">{c.department.split('>').pop()}</span>
                         </div>
                         <div className="flex flex-col">
                           <span className="text-slate-400 font-bold uppercase tracking-tighter">Manager</span>
                           <span className="text-slate-700">{c.manager}</span>
                         </div>
                      </div>
                      
                      <button onClick={() => handleGenericAction(`Viewing ${c.name}'s full profile`)} className="mt-6 w-full py-2 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-lg text-xs font-bold transition-colors">View Full Profile</button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}


            {activeTab === 'Workflow' && userRole === 'HR' && (
              <motion.div key="workflow" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-12 pb-20">
                <div className="flex justify-between items-end mb-4">
                  <div>
                    <h1 className="text-4xl font-black text-slate-800 tracking-tight flex items-center gap-3">
                      <div className="p-2 bg-blue-600 rounded-2xl text-white shadow-lg shadow-blue-500/30">
                        <Workflow size={28} />
                      </div>
                      Onboarding Engine
                    </h1>
                    <p className="text-slate-500 mt-2 font-medium">Dynamic, rule-based journey resolution powered by Org-Graph logic.</p>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-5 py-2.5 bg-white border border-slate-200 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all flex items-center gap-2 shadow-sm">
                      <Settings size={14} /> Global Logic
                    </button>
                    <button className="px-5 py-2.5 bg-blue-600 rounded-2xl text-xs font-bold text-white hover:bg-blue-700 transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20 active:scale-95">
                      <Plus size={16} /> Create Rule
                    </button>
                  </div>
                </div>
                
                {/* Smart Rules Summary Section */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                  {Object.entries(DEPARTMENT_TEMPLATES).map(([dept, taskIds], dIdx) => {
                    const deptName = dept.split('>').pop()?.trim() || dept;
                    const mappings = ROLE_MAPPINGS[dept] || {};
                    
                    return (
                      <motion.div 
                        initial={{ opacity:0, y: 20 }}
                        animate={{ opacity:1, y: 0 }}
                        transition={{ delay: dIdx * 0.1 }}
                        key={dept} 
                        className="group relative bg-white/70 backdrop-blur-xl rounded-[40px] border border-white shadow-[0_20px_50px_rgba(0,0,0,0.04)] hover:shadow-[0_40px_80px_rgba(0,0,0,0.06)] transition-all duration-500 overflow-hidden flex flex-col min-h-[500px]"
                      >
                        {/* Decorative Background Element */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/5 to-transparent rounded-bl-[100px] -z-0"></div>
                        
                        <div className="p-8 pb-6 border-b border-slate-50/50 relative z-10">
                          <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center gap-4">
                              <div className="w-14 h-14 rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-xl shadow-blue-500/30 group-hover:scale-110 transition-transform">
                                <Rocket size={26} />
                              </div>
                              <div>
                                <h3 className="text-xl font-bold text-slate-800 tracking-tight">{deptName}</h3>
                                <div className="flex items-center gap-2 mt-1">
                                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{taskIds.length} Automated Steps</span>
                                </div>
                              </div>
                            </div>
                            <div className="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-[9px] font-black uppercase tracking-widest border border-blue-100/50">
                              Active
                            </div>
                          </div>
                          
                          <div className="flex flex-col gap-3">
                            <div className="flex items-center justify-between p-4 bg-slate-900/[0.02] rounded-3xl border border-slate-100/50">
                              <div className="flex items-center gap-3">
                                <div className="p-2 bg-white rounded-xl shadow-sm border border-slate-50">
                                  <Bot size={16} className="text-blue-600" />
                                </div>
                                <div>
                                  <span className="text-[10px] font-black text-slate-400 uppercase leading-none block mb-1">Primary Rule</span>
                                  <span className="text-xs font-bold text-slate-700">Auto-Resolve Roles</span>
                                </div>
                              </div>
                              <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="p-8 flex-1 space-y-8 relative z-10">
                          <div>
                            <div className="flex justify-between items-center mb-4">
                              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Inherited Context</p>
                              <div className="h-[1px] flex-1 bg-slate-100 mx-4"></div>
                            </div>
                            <div className="grid grid-cols-1 gap-3">
                              {Object.entries(mappings).map(([role, person], i) => (
                                <div key={role} className="flex items-center justify-between p-3 bg-white border border-slate-50 rounded-2xl shadow-sm">
                                  <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-500 font-black text-[10px] border border-slate-100">
                                      {role.charAt(0)}
                                    </div>
                                    <span className="text-xs font-semibold text-slate-500">{role}</span>
                                  </div>
                                  <span className="text-xs font-black text-slate-800">{person}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <div className="flex justify-between items-center mb-4">
                              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Logic Execution Node</p>
                              <div className="h-[1px] flex-1 bg-slate-100 mx-4"></div>
                            </div>
                            <div className="p-5 bg-gradient-to-br from-slate-50 to-white rounded-[32px] border border-slate-100 shadow-inner relative overflow-hidden">
                               <div className="absolute top-0 right-0 p-3 opacity-10">
                                 <Zap size={40} className="text-blue-600" />
                               </div>
                               <div className="flex items-center gap-2 mb-3">
                                 <div className="w-6 h-6 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600">
                                   <Zap size={14} />
                                 </div>
                                 <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter">AI Rule Gate v2.4</span>
                               </div>
                               <p className="text-[11px] text-slate-700 font-bold leading-relaxed pr-8">
                                  {deptName === 'AI' ? 
                                    "Devs → Async Practice Head Sync → Infra Auto-Provisioning" :
                                    "Common → HR Policy Awareness → Manager Introduction"}
                               </p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="p-6 bg-slate-50/30 border-t border-slate-50 flex gap-3 mt-auto">
                          <button onClick={() => showToast(`Dry-run: ${deptName} Logic Success!`, 'success')} className="flex-1 py-3.5 text-[11px] font-black text-blue-600 bg-white border-2 border-blue-50 hover:border-blue-100 hover:bg-blue-50/50 rounded-2xl transition-all shadow-sm flex items-center justify-center gap-2">
                            <CheckCircle2 size={14} /> Test Logic
                          </button>
                          <button onClick={() => showToast(`Opening Logic Configurator...`, 'info')} className="flex-1 py-3.5 text-[11px] font-black text-slate-600 bg-white border-2 border-slate-100 hover:bg-slate-50 rounded-2xl transition-all shadow-sm flex items-center justify-center gap-2">
                            <Cog size={14} /> Config
                          </button>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>

                {/* Modernized Journey Timeline */}
                <motion.div 
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white p-12 rounded-[50px] border border-slate-100 shadow-[0_40px_100px_rgba(0,0,0,0.03)] relative overflow-x-auto"
                >
                   <div className="flex justify-between items-center mb-16">
                    <div>
                      <h4 className="text-xs font-black text-slate-800 uppercase tracking-[0.2em] flex items-center gap-3">
                        <div className="p-2 bg-indigo-50 rounded-xl text-indigo-600">
                          <GitBranch size={20} />
                        </div>
                        Global Journey Sequence
                      </h4>
                      <p className="text-[11px] text-slate-400 font-bold mt-2 ml-10">THE UNDERLYING BLUEPRINT FOR ALL DEPARTMENT-SPECIFIC OVERRIDES.</p>
                    </div>
                    <div className="flex gap-4">
                      <div className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest"><div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/20"></div> Fixed</div>
                      <div className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest"><div className="w-2.5 h-2.5 rounded-full bg-blue-600 shadow-lg shadow-blue-500/20"></div> Dynamic</div>
                    </div>
                   </div>

                   <div className="flex min-w-[1200px] justify-between relative px-8 pb-4">
                     {/* Connector Line - High Fidelity Gradient */}
                     <div className="absolute top-[36px] left-16 right-16 h-[6px] bg-slate-50 -z-0 rounded-full overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 via-blue-600 to-indigo-600 opacity-20"></div>
                        <motion.div 
                          initial={{ x: '-100%' }}
                          animate={{ x: '100%' }}
                          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                          className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-40"
                        />
                     </div>
                     
                     {TASKS_DETAIL.map((task, idx) => (
                       <motion.div 
                         key={task.id} 
                         initial={{ opacity: 0, scale: 0.8 }}
                         animate={{ opacity: 1, scale: 1 }}
                         transition={{ delay: idx * 0.05 }}
                         className="relative z-10 flex flex-col items-center group cursor-pointer"
                       >
                         {/* 3D Styled Step Indicator */}
                         <div className={`w-18 h-18 rounded-[32px] flex flex-col items-center justify-center border-[6px] border-white shadow-[0_15px_35px_rgba(0,0,0,0.08)] transition-all duration-500 group-hover:scale-110 group-hover:-translate-y-2
                           ${idx === 0 ? 'bg-gradient-to-br from-emerald-400 to-emerald-600 text-white' : idx === 1 ? 'bg-gradient-to-br from-blue-500 to-indigo-700 text-white' : 'bg-white text-slate-300'}`}>
                           {idx === 0 ? <Check size={28} strokeWidth={3} /> : <span className={`text-2xl font-black ${idx > 1 ? 'text-slate-100' : 'text-white'}`}>{idx + 1}</span>}
                         </div>

                         <div className="mt-8 text-center px-4">
                            <h4 className="text-[12px] font-black text-slate-800 leading-tight mb-2 uppercase tracking-tight group-hover:text-blue-600 transition-colors whitespace-nowrap">{task.title}</h4>
                            <div className="flex justify-center">
                              <span className={`text-[9px] font-black px-2.5 py-1 rounded-full uppercase tracking-[0.1em] shadow-sm transform group-hover:scale-105 transition-transform
                                ${task.owner === 'HR' ? 'bg-violet-600 text-white' : task.owner === 'IT' ? 'bg-orange-500 text-white' : task.owner === 'Candidate' ? 'bg-teal-500 text-white' : 'bg-slate-400 text-white'}`}>
                                {task.owner}
                              </span>
                            </div>
                         </div>

                         {/* Hover Context (Tooltip-like) */}
                         <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none">
                            <div className="bg-slate-900 text-white text-[9px] font-black px-3 py-1.5 rounded-lg whitespace-nowrap shadow-xl flex items-center gap-2">
                               <Bot size={10} className="text-blue-400" /> Automated Rule
                            </div>
                            <div className="w-2 h-2 bg-slate-900 mx-auto rotate-45 -mt-1"></div>
                         </div>
                       </motion.div>
                     ))}
                   </div>
                </motion.div>
              </motion.div>
            )}

            {activeTab === 'Chat' && (
              <motion.div key="chat" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="h-[600px] border border-gray-100 rounded-2xl overflow-hidden flex bg-white shadow-xl">
                {/* Chat Sidebar */}
                <div className="w-80 border-r border-gray-100 bg-gray-50 flex flex-col">
                  <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="font-bold text-slate-800 text-lg">Inbox</h3>
                    <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-[10px] font-bold">2</div>
                  </div>
                  <div className="p-4">
                    <div className="relative">
                      <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input type="text" placeholder="Search chats..." className="w-full bg-white border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:ring-1 focus:ring-blue-500 outline-none" />
                    </div>
                  </div>
                  <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    {candidates
                      .filter(c => userRole === 'HR' || c.name === loggedInUser?.name)
                      .map(c => (
                        <button 
                           key={c.id} 
                           onClick={() => setActiveChatId(c.id)}
                           className={`w-full text-left p-3 rounded-xl transition-all flex items-center gap-4 hover:shadow-sm
                             ${activeChatId === c.id ? 'bg-white shadow-lg shadow-blue-900/5 ring-1 ring-blue-50' : 'hover:bg-white text-slate-500'}`}
                        >
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-sm shrink-0
                            ${activeChatId === c.id ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
                            {c.name.charAt(0)}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex justify-between items-center mb-0.5">
                              <span className={`text-sm truncate font-bold ${activeChatId === c.id ? 'text-blue-600' : 'text-slate-800'}`}>{c.name}</span>
                              <span className="text-[10px] font-medium text-slate-400">12:35 PM</span>
                            </div>
                            <p className="text-xs truncate text-slate-400">Can you check my VPN access?</p>
                          </div>
                        </button>
                      ))}
                  </div>
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col bg-white">
                  {/* Chat Header */}
                  <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <div className="flex items-center gap-4">
                       <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg shadow-inner ring-4 ring-blue-50">
                         {candidates.find(c => c.id === activeChatId)?.name.charAt(0) || 'A'}
                       </div>
                       <div>
                         <h3 className="font-bold text-slate-800">{candidates.find(c => c.id === activeChatId)?.name || 'AI Support Assistant'}</h3>
                         <div className="flex items-center gap-1.5 text-emerald-500 text-[10px] font-bold uppercase tracking-wider">
                           <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Online
                         </div>
                       </div>
                    </div>
                    <div className="flex gap-2">
                       <button className="p-2.5 rounded-xl border border-gray-100 text-slate-400 hover:text-slate-800 hover:bg-gray-50 transition-all"><Settings size={18} /></button>
                       <button className="p-2.5 rounded-xl border border-gray-100 text-slate-400 hover:text-slate-800 hover:bg-gray-50 transition-all"><Users size={18} /></button>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 p-8 space-y-6 overflow-y-auto flex flex-col bg-slate-50/30">
                     <div className="flex justify-center mb-4">
                        <span className="bg-white px-3 py-1 rounded-full text-[10px] font-bold text-slate-400 border border-gray-100 uppercase tracking-widest shadow-sm">Today</span>
                     </div>
                     
                     <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} className="max-w-[70%] self-start flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-200 shrink-0 mt-1"></div>
                        <div className="bg-white p-4 rounded-2xl rounded-tl-sm shadow-sm border border-gray-100 text-sm text-slate-600 leading-relaxed font-medium">
                          Hello Team! I have started my onboarding. Quick question: What is the laptop replacement policy for new joinees?
                        </div>
                     </motion.div>
                     
                     <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} transition={{delay: 0.2}} className="max-w-[70%] self-end">
                        <div className="bg-[#2b3553] text-white p-4 rounded-2xl rounded-tr-sm shadow-xl shadow-blue-900/10 text-sm leading-relaxed font-medium">
                          Laptops can be replaced every 3 years or immediately in case of severe hardware failure. Contact IT Operations for exceptions. We've also updated your checklist!
                        </div>
                        <div className="text-[10px] font-bold text-slate-400 mt-2 text-right uppercase tracking-tighter">Read 12:45 PM</div>
                     </motion.div>
                  </div>

                  {/* Input Container */}
                  <div className="p-6 bg-white border-t border-gray-100">
                    <div className="flex gap-3 items-center bg-gray-50 border border-gray-100 rounded-2xl p-2 pl-5 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-100 transition-all">
                      <input type="text" placeholder="Type a message..." className="flex-1 bg-transparent border-none py-3 text-sm focus:outline-none text-slate-700 placeholder:text-slate-400 font-medium" />
                      <button className="bg-blue-600 hover:bg-blue-700 text-white w-12 h-12 rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95 flex items-center justify-center flex-shrink-0">
                        <Rocket size={20} className="rotate-45" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'System Settings' && userRole === 'HR' && (
              <motion.div key="settings" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-8">
                <div>
                  <h1 className="text-3xl font-bold text-slate-800 tracking-tight">System Settings</h1>
                  <p className="text-sm text-slate-500 mt-1">Configure platform behavior, integrations, and security policies.</p>
                </div>

                {/* Notifications & Alerts */}
                <div>
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2"><Bell size={14} /> Notifications & Alerts</h2>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 divide-y divide-gray-50">
                    {[
                      { key: 'emailParams' as const, title: 'Email Notifications', desc: 'Parallel emails routed to Admin, HR, IT, and Candidate upon task creation.', icon: Mail },
                      { key: 'slaAlerts' as const, title: 'SLA Breach Alerts', desc: 'Automatically flag overdue tasks to managers after 48h.', icon: AlertTriangle },
                    ].map(item => (
                      <div key={item.key} onClick={() => setSettings({...settings, [item.key]: !settings[item.key]})} className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors cursor-pointer group">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 group-hover:text-blue-500 transition-colors shrink-0 mt-0.5">
                            <item.icon size={20} />
                          </div>
                          <div>
                            <h3 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors text-sm">{item.title}</h3>
                            <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
                          </div>
                        </div>
                        <div className={`w-11 h-6 duration-300 rounded-full relative shrink-0 ${settings[item.key] ? 'bg-emerald-500' : 'bg-gray-300'}`}>
                           <motion.div animate={{ x: settings[item.key] ? 20 : 0 }} className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5 shadow-sm"></motion.div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI & Integrations */}
                <div>
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2"><Zap size={14} /> AI & Integrations</h2>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 divide-y divide-gray-50">
                    <div onClick={() => setSettings({...settings, ragEnabled: !settings.ragEnabled})} className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors cursor-pointer group">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-500 shrink-0 mt-0.5">
                          <Bot size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors text-sm">Azure OpenAI RAG</h3>
                          <p className="text-xs text-slate-400 mt-0.5">Policy documents loaded for the AI Chat Assistant. Uses GPT-4o via Azure.</p>
                        </div>
                      </div>
                      <div className={`w-11 h-6 duration-300 rounded-full relative shrink-0 ${settings.ragEnabled ? 'bg-emerald-500' : 'bg-gray-300'}`}>
                         <motion.div animate={{ x: settings.ragEnabled ? 20 : 0 }} className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5 shadow-sm"></motion.div>
                      </div>
                    </div>
                    <div className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors group">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-500 shrink-0 mt-0.5">
                          <Globe size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-800 text-sm">Microsoft Teams Integration</h3>
                          <p className="text-xs text-slate-400 mt-0.5">Auto-post onboarding updates to team channels.</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full uppercase tracking-wider">Coming Soon</span>
                    </div>
                    <div className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors group">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500 shrink-0 mt-0.5">
                          <Calendar size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-800 text-sm">Keka HRMS Sync</h3>
                          <p className="text-xs text-slate-400 mt-0.5">Sync employee data, attendance, and leave balances with Keka.</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full uppercase tracking-wider">Coming Soon</span>
                    </div>
                  </div>
                </div>

                {/* Security & Data */}
                <div>
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2"><Shield size={14} /> Security & Data</h2>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 divide-y divide-gray-50">
                    <div className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors group">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center text-rose-500 shrink-0 mt-0.5">
                          <Shield size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-800 text-sm">Role-Based Access Control</h3>
                          <p className="text-xs text-slate-400 mt-0.5">Enforce HR, IT, Manager, and Candidate permissions.</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full uppercase tracking-wider">Active</span>
                    </div>
                    <div className="p-5 flex justify-between items-center hover:bg-slate-50/50 transition-colors group">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 shrink-0 mt-0.5">
                          <Database size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-800 text-sm">Data Retention Policy</h3>
                          <p className="text-xs text-slate-400 mt-0.5">Onboarding records are retained for 3 years as per compliance.</p>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-slate-600">3 Years</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </main>

      {/* FLOATING AI ASSISTANT BUTTON & CHAT WINDOW */}
      <motion.div 
        drag 
        dragConstraints={{ left: -1000, right: 0, top: -800, bottom: 0 }}
        dragElastic={0.1}
        className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3"
      >
        <AnimatePresence>
          {isChatOpen && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.8, y: 20 }} 
              animate={{ opacity: 1, scale: 1, y: 0 }} 
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              onPointerDownCapture={(e) => e.stopPropagation()} // Prevent dragging when interacting with chat
              className="bg-white w-[350px] h-[450px] rounded-2xl shadow-2xl border border-blue-100 flex flex-col overflow-hidden"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-[#2b3553] to-indigo-900 p-4 shrink-0 flex justify-between items-center text-white">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center"><Bot size={18} /></div>
                  <div>
                    <h3 className="text-sm font-bold leading-tight">AI Onboarding Assistant</h3>
                    <p className="text-[10px] text-emerald-300">Always Available • RAG Active</p>
                  </div>
                </div>
                <button onClick={() => setIsChatOpen(false)} className="hover:bg-white/20 p-1.5 rounded-full transition-colors"><X size={16} /></button>
              </div>
              
              {/* Chat Body */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 text-sm">
                <div className="flex gap-2 w-full">
                  <div className="w-6 h-6 rounded-full bg-[#2b3553] shrink-0 flex items-center justify-center text-white"><Bot size={12} /></div>
                  <div className="bg-white p-3 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100 text-slate-700 w-fit max-w-[85%]">
                    Hello Tejas! I am your AI assistant. I have access to all HR policy documents, IT manuals, and your specific onboarding plan. How can I help you today?
                  </div>
                </div>
                
                <div className="flex gap-2 w-full flex-row-reverse">
                  <div className="w-6 h-6 rounded-full bg-blue-500 shrink-0 flex items-center justify-center text-white text-[10px] font-bold">TN</div>
                  <div className="bg-blue-600 p-3 rounded-2xl rounded-tr-sm shadow-sm text-white w-fit max-w-[85%]">
                    What is the leave policy?
                  </div>
                </div>

                <div className="flex gap-2 w-full">
                  <div className="w-6 h-6 rounded-full bg-[#2b3553] shrink-0 flex items-center justify-center text-white"><Bot size={12} /></div>
                  <div className="bg-white p-3 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100 text-slate-700 w-fit max-w-[85%]">
                    Based on the <strong>2026 HR Leave Policy</strong>, you are entitled to 20 Privilege Leaves (PL) and 8 Casual/Sick Leaves (CL/SL) per calendar year. During your 6-month probation, you can accrue and use 1 CL/SL per month.
                  </div>
                </div>
                
                <div className="flex gap-2 w-full flex-row-reverse">
                  <div className="w-6 h-6 rounded-full bg-blue-500 shrink-0 flex items-center justify-center text-white text-[10px] font-bold">TN</div>
                  <div className="bg-blue-600 p-3 rounded-2xl rounded-tr-sm shadow-sm text-white w-fit max-w-[85%]">
                    How do I access the VPN?
                  </div>
                </div>
                
                <div className="flex gap-2 w-full">
                  <div className="w-6 h-6 rounded-full bg-[#2b3553] shrink-0 flex items-center justify-center text-white"><Bot size={12} /></div>
                  <div className="bg-white p-3 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100 text-slate-700 w-fit max-w-[85%]">
                    Step 3 of your checklist ("Asset Assignment") has been verified. IT has pre-installed Cisco AnyConnect on your machine. Open the app and connect to <strong>vpn.company.com</strong> using your Microsoft SSO credentials.
                  </div>
                </div>
              </div>

              {/* Input */}
              <div className="p-3 bg-white border-t border-slate-100 flex gap-2">
                <input 
                  type="text" 
                  placeholder="Ask me anything..." 
                  className="flex-1 bg-slate-50 border border-slate-200 rounded-full px-4 py-2 text-xs focus:ring-1 focus:ring-blue-500 outline-none text-slate-700"
                />
                <button className="w-8 h-8 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-colors">
                  <Rocket size={14} className="rotate-45" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button 
          onClick={() => setIsChatOpen(!isChatOpen)} 
          className="w-16 h-16 rounded-full bg-[#2b3553] text-white flex items-center justify-center shadow-2xl hover:scale-105 transition-transform cursor-grab active:cursor-grabbing border-2 border-white"
        >
          <Bot size={32} className="text-emerald-400" />
        </button>
      </motion.div>

      {/* ADD JOINEE MODAL (Trigger #1) */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/40 backdrop-blur-sm"
              onClick={() => !isAdding && setIsAddModalOpen(false)}
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white border border-gray-100 p-8 rounded-2xl w-full max-w-lg shadow-2xl"
            >
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Add New Joinee</h2>
                  <p className="text-xs text-slate-500 mt-1">Initialize boarding process and 9-task checklist.</p>
                </div>
                <button onClick={() => !isAdding && setIsAddModalOpen(false)} className="text-slate-400 hover:text-slate-800">
                  <X size={24} />
                </button>
              </div>

              <form onSubmit={handleAddSubmit} className="space-y-5">
                <div className="grid grid-cols-2 gap-5">
                  <div className="col-span-2">
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Full Name</label>
                    <input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="e.g. Rahul Sharma" />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Email Address</label>
                    <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="jane.doe@company.com" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Joining Date</label>
                    <input required type="date" value={formData.joinDate} onChange={e => setFormData({...formData, joinDate: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Position</label>
                    <input required type="text" value={formData.position} onChange={e => setFormData({...formData, position: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="e.g. Developer" />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Department</label>
                    <select required value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800">
                      <option value="">Select Dept</option>
                      <option value="Unassigned">Unassigned</option>
                      <optgroup label="Administration">
                        <option value="Administration > CTO's Office">Administration &gt; CTO&apos;s Office</option>
                        <option value="Administration > Advisory">Administration &gt; Advisory</option>
                        <option value="Administration > Solutions">Administration &gt; Solutions</option>
                      </optgroup>
                      <optgroup label="Delivery and Practices">
                        <option value="Delivery and Practices > Artificial Intelligence">Delivery and Practices &gt; Artificial Intelligence</option>
                        <option value="Delivery and Practices > Cloud Data">Delivery and Practices &gt; Cloud Data</option>
                        <option value="Delivery and Practices > Data Product">Delivery and Practices &gt; Data Product</option>
                        <option value="Delivery and Practices > Delivery">Delivery and Practices &gt; Delivery</option>
                        <option value="Delivery and Practices > Service Engineering">Delivery and Practices &gt; Service Engineering</option>
                      </optgroup>
                      <optgroup label="Enabling Services">
                        <option value="Enabling Services > Admin">Enabling Services &gt; Admin</option>
                        <option value="Enabling Services > Business Partnering">Enabling Services &gt; Business Partnering</option>
                        <option value="Enabling Services > Finance and Legal">Enabling Services &gt; Finance and Legal</option>
                        <option value="Enabling Services > Governance, Risk">Enabling Services &gt; Governance, Risk</option>
                        <option value="Enabling Services > Human Resources">Enabling Services &gt; Human Resources</option>
                        <option value="Enabling Services > IT Operations">Enabling Services &gt; IT Operations</option>
                        <option value="Enabling Services > IT Security">Enabling Services &gt; IT Security</option>
                        <option value="Enabling Services > Learning and Development">Enabling Services &gt; Learning and Development</option>
                      </optgroup>
                      <option value="Finance & Legal">Finance &amp; Legal</option>
                      <option value="HR">HR</option>
                      <option value="Management">Management</option>
                      <option value="Sales and Marketing">Sales and Marketing</option>
                      <option value="Strategy">Strategy</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Reporting Manager</label>
                    <select required value={formData.manager} onChange={e => setFormData({...formData, manager: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800">
                      <option value="">Select Manager</option>
                      <option value="Mohini Moghe">Mohini Moghe</option>
                      <option value="Prathamesh Kashelikar">Prathamesh Kashelikar</option>
                      <option value="Kaustubh Vartak">Kaustubh Vartak</option>
                      <option value="Sumit Patil">Sumit Patil</option>
                      <option value="Piyush Patil">Piyush Patil</option>
                      <option value="Ambar Gosavi">Ambar Gosavi</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Location</label>
                    <select required value={formData.location} onChange={e => setFormData({...formData, location: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800">
                      <option value="Pune">Pune</option>
                      <option value="Nagpur">Nagpur</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2 flex justify-end gap-3 mt-2 border-t border-gray-100">
                  <button type="button" onClick={() => !isAdding && setIsAddModalOpen(false)} className="px-5 py-2.5 text-sm font-bold text-slate-500 hover:text-slate-800" disabled={isAdding}>Cancel</button>
                  <button type="submit" disabled={isAdding} className="px-6 py-2.5 rounded-lg bg-[#2b3553] hover:bg-slate-700 text-white text-sm font-bold flex items-center gap-2">
                    {isAdding ? <><Clock className="animate-spin" size={16} /> Creating Record...</> : 'Initialize Onboarding'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* TOAST NOTIFICATIONS */}
      <div className="fixed top-4 right-4 z-[100] space-y-3 max-w-sm">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 100, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              className={`flex items-start gap-3 px-5 py-4 rounded-2xl shadow-2xl border backdrop-blur-sm
                ${toast.type === 'success' ? 'bg-emerald-50/95 border-emerald-200 text-emerald-800' 
                  : toast.type === 'warning' ? 'bg-amber-50/95 border-amber-200 text-amber-800'
                  : 'bg-white/95 border-blue-100 text-slate-700'}`}
            >
              <div className="shrink-0 mt-0.5">
                {toast.type === 'success' ? <CheckCircle2 size={18} className="text-emerald-500" /> 
                  : toast.type === 'warning' ? <AlertTriangle size={18} className="text-amber-500" />
                  : <Info size={18} className="text-blue-500" />}
              </div>
              <p className="text-sm font-semibold leading-snug">{toast.message}</p>
              <button onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))} className="shrink-0 text-slate-400 hover:text-slate-700 -mt-0.5">
                <X size={14} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

    </div>
  );
}
