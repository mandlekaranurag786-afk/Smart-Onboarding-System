"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Briefcase, GitBranch, BarChart2, MessageSquare, Settings, 
  Search, Bell, Mail, Target, ChevronDown, Check, Clock, Bot, Plus, X, Rocket,
  LayoutDashboard, FileText, Workflow, PieChart, Send, Cog, CheckCircle2,
  AlertTriangle, Info, Shield, Database, Globe, Zap, Calendar,
  LogOut, Eye, EyeOff, Lock, ArrowRight, ListTodo, Sparkles, ShieldCheck, PhoneCall, Phone, 
  Activity as ActivityIcon, ChevronLeft, ChevronRight
} from 'lucide-react';
import LiveActivityStream from './components/LiveActivityStream';
import { CandidateDetailView } from '../components/CandidateDetailView';

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

const getMeetingTypeFromTaskTitle = (taskTitle: string) => {
  const normalizedTitle = taskTitle.toLowerCase();
  if (normalizedTitle.includes('hr')) return 'HR Introduction';
  if (normalizedTitle.includes('practice head') || normalizedTitle.includes('delivery head')) {
    return 'Delivery Head Introduction';
  }
  return 'Manager Introduction';
};

const slotKey = (slot: SlotOption) => `${slot.name}|${slot.date}|${slot.time}`;

const updateTaskStatus = async (taskId: number, status: string) => {
  return apiRequest(`/api/tasks/${taskId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
};

const completeMyCandidateTask = async (taskId: number) => {
  return apiRequest(`/api/candidates/me/tasks/${taskId}/complete`, {
    method: 'PATCH',
  });
};

const normalizeTaskOwner = (owner?: string) => {
  const normalized = (owner || '').toString().trim().toUpperCase().replace(/\s+/g, '_');
  if (normalized === 'CANDIDATE') return 'Candidate';
  if (normalized === 'DELIVERY_HEAD') return 'Delivery Head';
  if (normalized === 'MANAGER') return 'Manager';
  if (normalized === 'SYSTEM') return 'System';
  if (normalized === 'HR') return 'HR';
  if (normalized === 'IT') return 'IT';
  return owner || 'System';
};

const normalizeTaskStatus = (status?: string) => (status || '').toString().trim().toLowerCase();

const normalizeProgressPayload = (payload: any) => {
  if (!payload || !Array.isArray(payload.tasks)) return payload;
  return {
    ...payload,
    tasks: payload.tasks.map((task: any) => ({
      ...task,
      owner: normalizeTaskOwner(task.owner),
      status: normalizeTaskStatus(task.status),
    })),
  };
};

const fetchCandidateProgress = async (candidateId: number) => {
  return apiRequest(`/api/candidates/${candidateId}/progress`);
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
// Tab type definition

const TASKS_DETAIL = [
  { id: 1, title: 'Document Signing', desc: 'Offer letter, NDA, company policies', owner: 'HR' },
  { id: 2, title: 'Work Profile Builder', desc: 'Candidate fills complete profile', owner: 'Candidate' },
  { id: 3, title: 'Account Provisioning', desc: 'Keka, Teams, SharePoint access', owner: 'System' },
  { id: 4, title: 'Meeting: HR Walkthrough', desc: 'Company policies walkthrough', owner: 'HR' },
  { id: 5, title: 'Meeting: Reporting Manager', desc: 'Role-specific expectations & briefing', owner: 'Manager' },
  { id: 6, title: 'Meeting: Delivery Head', desc: 'Strategic roadmap & technical guidance', owner: 'Delivery Head' },
  { id: 7, title: 'Karma Portal Acknowledgment', desc: 'Candidate confirms system completion', owner: 'Candidate' },
  { id: 8, title: 'Final Review', desc: 'Onboarding process completion review', owner: 'HR' },
];

// Department-specific task templates
const DEPARTMENT_TEMPLATES: Record<string, number[]> = {
  'Delivery and Practices > Artificial Intelligence': [1, 2, 3, 4, 5, 6, 7, 8],
  'HR': [1, 2, 3, 4, 7, 8],
  'Sales': [1, 2, 3, 4, 5, 7, 8],
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

const getDepartmentLabel = (department?: string) => department?.split('>').pop()?.trim() || department || '';

const compareCandidates = (
  a: { name?: string; manager?: string; department?: string },
  b: { name?: string; manager?: string; department?: string }
) => {
  // Default sorting by name
  return (a.name || '').localeCompare(b.name || '', undefined, { sensitivity: 'base' });
};

// ═══════════════════════════════════════════════════════
// POLICY CHAT INTEGRATED COMPONENT
// ═══════════════════════════════════════════════════════
interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  sources?: Array<{
    policy_name: string;
    source_file: string;
    similarity_score: number;
    excerpt: string;
  }>;
  confidence?: 'high' | 'medium' | 'low';
}

function PolicyChatIntegrated({ 
  userRole, 
  messages, 
  setMessages, 
  input, 
  setInput 
}: { 
  userRole: 'HR' | 'Candidate',
  messages: Message[],
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>,
  input: string,
  setInput: React.Dispatch<React.SetStateAction<string>>
}) {
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = `${API_BASE_URL}/api/rag/query`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          top_k: 5,
          include_sources: true,
        }),
      });

      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();

      const botMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('[RAG Chat] Error querying RAG:', err);
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm having trouble accessing the policy database right now. Please try again in a moment.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getConfidenceBadge = (confidence?: string) => {
    if (!confidence) return null;
    
    const styles = {
      high: 'bg-green-100 text-green-700 border-green-200',
      medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      low: 'bg-red-100 text-red-700 border-red-200',
    };

    const icons = {
      high: <CheckCircle2 size={10} />,
      medium: <Info size={10} />,
      low: <AlertTriangle size={10} />,
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border ${styles[confidence as keyof typeof styles]}`}>
        {icons[confidence as keyof typeof icons]}
        {confidence.toUpperCase()}
      </span>
    );
  };

  const suggestedQuestions = [
    "What is the password policy?",
    "Can I work remotely?",
    "What is the BYOD policy?",
    "How do I report a security incident?",
  ];

  const pageVariants: any = {
    initial: { opacity: 0, y: 15 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
    exit: { opacity: 0, y: -15, transition: { duration: 0.2 } }
  };

  return (
    <motion.div key="chat" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="h-[600px] border border-gray-100 rounded-2xl overflow-hidden flex flex-col bg-white shadow-xl">
      {/* Header */}
      <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
              <Bot size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">AI Policy Assistant</h2>
              <div className="flex items-center gap-1.5 text-emerald-500 text-[10px] font-bold uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> RAG Active
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-600 font-semibold">10 Policies Indexed</p>
            <p className="text-[10px] text-slate-400">Powered by AI</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.type === 'bot' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                  <Bot size={16} className="text-white" />
                </div>
              )}
              
              <div className={`max-w-[75%] ${message.type === 'user' ? 'order-first' : ''}`}>
                <div className={`rounded-2xl px-4 py-3 ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white border border-gray-200 text-slate-800'
                }`}>
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  
                  {message.confidence && (
                    <div className="mt-2">
                      {getConfidenceBadge(message.confidence)}
                    </div>
                  )}
                </div>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 space-y-2">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-2">📚 Sources:</p>
                    {message.sources.slice(0, 2).map((source, idx) => (
                      <div key={idx} className="bg-white border border-gray-200 rounded-lg p-3 text-xs">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="flex items-center gap-1.5">
                            <FileText size={11} className="text-blue-600 shrink-0" />
                            <span className="font-semibold text-blue-600 text-[10px]">{source.policy_name}</span>
                          </div>
                          <span className="text-[9px] text-slate-500 shrink-0 bg-slate-100 px-1.5 py-0.5 rounded">
                            {(source.similarity_score * 100).toFixed(0)}% match
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-600 line-clamp-2">{source.excerpt}</p>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-[9px] text-slate-400 mt-1 px-2">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>

              {message.type === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center shrink-0 shadow-md">
                  <Users size={16} className="text-slate-600" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm flex items-center gap-3">
              <div className="flex gap-1">
                <motion.span animate={{ scale: [1, 1.2, 1], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-blue-600 rounded-full"></motion.span>
                <motion.span animate={{ scale: [1, 1.2, 1], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-indigo-600 rounded-full"></motion.span>
                <motion.span animate={{ scale: [1, 1.2, 1], opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-blue-400 rounded-full"></motion.span>
              </div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">AI is thinking...</span>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="px-6 pb-4 space-y-2 bg-slate-50">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">💡 Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInput(question)}
                className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-[11px] text-slate-600 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all font-medium"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about company policies..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm disabled:bg-gray-50 disabled:text-gray-400"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            onClick={(e) => {
              console.log('[RAG Chat] Button clicked');
            }}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 flex items-center gap-2"
          >
            {isLoading ? (
              <Clock size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}

const MANAGERS = [
  "Mohini Moghe",
  "Prathamesh Kashelikar",
  "Kaustubh Vartak",
  "Sumit Patil",
  "Piyush Patil",
  "Ambar Gosavi"
];

const DEPARTMENTS = [
  "Administration",
  "Enabling Services",
  "Delivery and Practices",
  "HR",
  "Sales and Marketing",
  "Finance and Legal"
];

export default function Home() {
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
  const [filterDate, setFilterDate] = useState<string>('');
  const [filterManager, setFilterManager] = useState<string>('');
  const [filterDepartment, setFilterDepartment] = useState<string>('');
  const [currentPageNav, setCurrentPageNav] = useState(0);
  const itemsPerPageNav = 5;
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [directorySearch, setDirectorySearch] = useState('');
  const [toasts, setToasts] = useState<{id: number; message: string; type: 'success' | 'info' | 'warning'}[]>([]);
  const [analytics, setAnalytics] = useState({
    onboarded: { total: 0 },
    in_progress: { total: 0 },
    pending_tasks: { total: 0, it: 0, hr: 0, candidate: 0 },
    avg_onboarding_time: { avg_days: 0.0 }
  });

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
  const [floatingMessages, setFloatingMessages] = useState<any[]>([
    {
      id: 1,
      type: 'bot',
      content: "Hello Tejas! I am your AI assistant. I have access to all HR policy documents, IT manuals, and your specific onboarding plan. How can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [floatingInput, setFloatingInput] = useState('');
  const [isFloatingLoading, setIsFloatingLoading] = useState(false);

  const handleFloatingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!floatingInput.trim() || isFloatingLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: floatingInput.trim(),
      timestamp: new Date()
    };

    setFloatingMessages(prev => [...prev, userMessage]);
    setFloatingInput('');
    setIsFloatingLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          top_k: 5,
          include_sources: true,
        }),
      });

      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence,
      };

      setFloatingMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('[Floating Chat] Error:', err);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm having trouble connecting. Please try again or contact HR.",
        timestamp: new Date(),
      };
      setFloatingMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsFloatingLoading(false);
    }
  };

  // Selected candidate to expand task list
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null);
  
  // Selected candidate for detail view
  const [selectedCandidateForDetail, setSelectedCandidateForDetail] = useState<any | null>(null);

  // Candidate Progress State
  const [candidateProgress, setCandidateProgress] = useState<any>(null);
  const [isRefreshingProgress, setIsRefreshingProgress] = useState(false);
  const [candidateTasksMap, setCandidateTasksMap] = useState<Record<number, any[]>>({});

  // Smart Onboarding States
  const [scheduledMeetings, setScheduledMeetings] = useState<Record<number, Record<string, {
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

  const handleExpandCandidate = async (id: number | null) => {
    setSelectedCandidateId(id);
    if (id && !candidateTasksMap[id]) {
      try {
        const data = await fetchCandidateProgress(id);
        setCandidateTasksMap(prev => ({ ...prev, [id]: data.tasks }));
      } catch (error) {
        console.error('Error loading candidate tasks for HR:', error);
      }
    }
  };

  const toggleSkipTask = async (candidateId: number, taskId: number, isSkipped: boolean = false) => {
    try {
      const endpoint = isSkipped ? `/api/tasks/${taskId}/recover` : `/api/tasks/${taskId}/skip`;
      await apiRequest(endpoint, {
        method: 'POST',
      });
      showToast(isSkipped ? `Task recovered successfully.` : `Task skipped successfully.`, 'info');
      // Reload candidates
      await loadCandidates();
      if (selectedCandidateId === candidateId) {
        // reload tasks manually
        const data = await fetchCandidateProgress(candidateId);
        setCandidateTasksMap(prev => ({ ...prev, [candidateId]: data.tasks }));
      }
    } catch (e) {
      showToast(isSkipped ? `Failed to recover task.` : `Failed to skip task.`, 'warning');
    }
  };

  const getTasksForCandidate = (candidate: any) => {
    const templateIds = DEPARTMENT_TEMPLATES[candidate.department] || [1, 2, 3, 4, 5, 7, 8];
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
      // Date Filter
      let dateMatch = true;
      if (filterDate) {
        const [year, month, day] = filterDate.split('-');
        const formattedFilter = `${month}/${day}/${year}`;
        dateMatch = c.date === formattedFilter;
      }
      
      // Name Search Filter
      let searchMatch = true;
      if (directorySearch) {
        searchMatch = c.name.toLowerCase().includes(directorySearch.toLowerCase());
      }

      // Manager Filter
      let managerMatch = true;
      if (filterManager) {
        managerMatch = c.manager === filterManager;
      }

      // Department Filter
      let departmentMatch = true;
      if (filterDepartment) {
        departmentMatch = getDepartmentLabel(c.department) === filterDepartment;
      }

      return dateMatch && searchMatch && managerMatch && departmentMatch;
    })
    .sort(compareCandidates);

  // Pagination states and calculations
  const totalPagesNav = Math.ceil(filteredNavCandidates.length / itemsPerPageNav);
  const currentNavCandidates = filteredNavCandidates.slice(
    currentPageNav * itemsPerPageNav,
    (currentPageNav + 1) * itemsPerPageNav
  );

  // Reset pagination when filter or candidates change
  useEffect(() => {
    setCurrentPageNav(0);
  }, [filterDate, directorySearch, filterManager, filterDepartment, candidates.length]);



  // Lifted Chat History & Persistence
  const [integratedMessages, setIntegratedMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'bot',
      content: "👋 Hi! I'm your AI Onboarding Assistant. I can help you with:\n\n• Company policies (password, remote work, BYOD, etc.)\n• Onboarding questions\n• IT setup guidance\n• General support\n\nAsk me anything!",
      timestamp: new Date(),
    }
  ]);
  const [integratedInput, setIntegratedInput] = useState('');

  // LocalStorage Persistence
  useEffect(() => {
    try {
      const savedIM = localStorage.getItem('onboarding_chat_integrated');
      const savedFM = localStorage.getItem('onboarding_chat_floating');
      
      if (savedIM) {
        setIntegratedMessages(JSON.parse(savedIM).map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) })));
      }
      if (savedFM) {
        setFloatingMessages(JSON.parse(savedFM).map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) })));
      }
    } catch (e) {
      console.error('Failed to load chat history:', e);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('onboarding_chat_integrated', JSON.stringify(integratedMessages));
  }, [integratedMessages]);

  useEffect(() => {
    localStorage.setItem('onboarding_chat_floating', JSON.stringify(floatingMessages));
  }, [floatingMessages]);


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
        email: candidate.email,
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

      const scheduledMeetingMap: Record<number, Record<string, {
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
              const mappedMeetingType = meeting.meeting_type || '';
              if (!mappedMeetingType) continue;
              if (!scheduledMeetingMap[candidate.id]) {
                scheduledMeetingMap[candidate.id] = {};
              }
              scheduledMeetingMap[candidate.id][mappedMeetingType] = {
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

  const getSchedulingContext = () => {
    if (!schedulingTask) return null;
    const candidate = candidates.find(c => c.id === schedulingTask.candidateId);
    const task = (candidateTasksMap[schedulingTask.candidateId] || getTasksForCandidate(candidate || {})).find(
      (t) => t.id === schedulingTask.taskId
    );
    if (!candidate || !task) return null;
    return { candidate, task };
  };

  const loadSchedulingOptions = useCallback(async (
    candidateName: string,
    taskTitle: string,
    interviewerName?: string,
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
    const task = (candidateTasksMap[schedulingTask.candidateId] || getTasksForCandidate(candidate || {})).find(
      (t) => t.id === schedulingTask.taskId
    );
    if (!candidate || !task) return;
    loadSchedulingOptions(candidate.name, task.name || task.title || '');
  }, [schedulingTask]);

  const handleInterviewerChange = async (name: string) => {
    const context = getSchedulingContext();
    if (!context) return;
    setSelectedInterviewerName(name);
    await loadSchedulingOptions(context.candidate.name, context.task.name || context.task.title || '', name);
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
      const taskTitle = context.task.name || context.task.title || '';
      const meetingType = getMeetingTypeFromTaskTitle(taskTitle);
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
          [meetingType]: {
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

  // Poll checklist/candidate data for live sync across HR and candidate portals
  useEffect(() => {
    const fetchChecklist = async () => {
      try {
        await loadCandidates();
      } catch (err) {
        console.error('Checklist fetch failed:', err);
      }
    };

    fetchChecklist();
    const interval = setInterval(fetchChecklist, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${base}/api/analytics/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setAnalytics(data);
        }
      } catch (err) {
        console.error("Analytics fetch failed:", err);
      }
    };

    fetchAnalytics();

    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, []);

  // Poll candidate checklist for logged-in candidate
  useEffect(() => {
    if (isLoggedIn && loggedInUser?.role === 'Candidate' && !candidateProgress && !isRefreshingProgress) {
      loadCandidateProgress();
    }
  }, [isLoggedIn, loggedInUser, candidateProgress, isRefreshingProgress]);

  const loadCandidateProgress = async (id?: number) => {
    if (isRefreshingProgress) return;
    const resolvedId =
      id ||
      candidateProgress?.candidate_id ||
      candidates.find((c) => c.email?.toLowerCase() === loggedInUser?.email?.toLowerCase())?.id ||
      candidates.find((c) => c.name?.toLowerCase() === loggedInUser?.name?.toLowerCase())?.id;
    if (!resolvedId) {
      console.warn('[Dashboard] Unable to resolve candidate id for progress fetch');
      return;
    }
    setIsRefreshingProgress(true);
    console.log(`[Dashboard] Fetching progress for candidate ID: ${resolvedId}`);
    
    try {
      const data = await fetchCandidateProgress(resolvedId);
      console.log(`[Dashboard] Received progress data:`, data);
      
      if (!data || !data.tasks || data.tasks.length === 0) {
        console.warn(`[Dashboard] No tasks found in progress data for ID: ${resolvedId}`);
      }
      
      setCandidateProgress(data || { tasks: [] });
    } catch (error) {
      console.error(`[Dashboard] Error loading candidate progress (ID: ${resolvedId}):`, error);
      showToast('Failed to load your onboarding progress.', 'warning');
      // Set an empty object with error to prevent infinite retries
      setCandidateProgress({ tasks: [], error: true });
    } finally {
      setIsRefreshingProgress(false);
    }
  };

  const handleCompleteTask = async (taskId: number, taskName: string, hrCandidateId?: number) => {
    try {
      if (loggedInUser?.role === 'Candidate') {
        await completeMyCandidateTask(taskId);
      } else {
        await updateTaskStatus(taskId, 'COMPLETED');
      }
      
      // Update local state immediately for snappy feel if possible, 
      // but the data refresh will handle the source of truth.
      showToast(`"${taskName}" marked as complete!`, 'success');
      
      // Re-fetch progress to unlock next steps and update counters
      if (loggedInUser?.role === 'Candidate') {
        const myEmail = loggedInUser.email?.toLowerCase();
        const candidate = candidates.find(c => c.email?.toLowerCase() === myEmail) || 
                          candidates.find(c => c.name?.toLowerCase() === loggedInUser.name?.toLowerCase());
        
        if (candidate) {
          // Add a tiny delay to ensure backend has finished all side-effects (like LangGraph steps if any)
          setTimeout(async () => {
            await loadCandidateProgress(candidate.id);
            await loadCandidates(); // Refresh the 3/9 counter as well
          }, 500);
        }
      } else {
        await loadCandidates();
        if (hrCandidateId && selectedCandidateId === hrCandidateId) {
          // reload tasks manually
          const data = await fetchCandidateProgress(hrCandidateId);
          setCandidateTasksMap(prev => ({ ...prev, [hrCandidateId]: data.tasks }));
        }
      }
    } catch (error) {
      console.error('Error completing task:', error);
      showToast(`Failed to update task: ${taskName}`, 'warning');
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

  // LOGIN HANDLER - Hybrid Authentication (API for Candidates, Mock for HR)
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setIsLoggingIn(true);

    try {
      // Check if user is in MOCK_USERS (HR users)
      const mockUser = MOCK_USERS[loginEmail.toLowerCase()];
      
      if (mockUser) {
        // Use mock authentication for HR users
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API delay
        
        if (mockUser.password !== loginPassword) {
          setLoginError('Invalid email or password. Please try again.');
          setIsLoggingIn(false);
          return;
        }
        
        // Mock user authenticated
        setLoggedInUser({ email: loginEmail.toLowerCase(), role: mockUser.role, name: mockUser.name });
        setUserRole(mockUser.role);
        setActiveTab(mockUser.role === 'HR' ? 'Analytics' : 'My Dashboard');
        
        if (mockUser.role === 'Candidate') {
          const cand = candidates.find(c => c.name === mockUser.name);
          if (cand) {
            setActiveChatId(cand.id);
            loadCandidateProgress(cand.id);
          }
        } else {
          setActiveChatId(1);
        }
        
        setIsLoggedIn(true);
        setIsLoggingIn(false);
        setLoginEmail('');
        setLoginPassword('');
        return;
      }

      // Not in MOCK_USERS, try real API authentication (for candidates)
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginEmail.toLowerCase(),
          password: loginPassword,
          user_type: 'candidate'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        setLoginError(errorData.detail || 'Invalid email or password. Please try again.');
        setIsLoggingIn(false);
        return;
      }

      const data = await response.json();
      
      // Store JWT token
      localStorage.setItem('auth_token', data.access_token);
      
      // Set user info
      const role = data.user.user_type === 'candidate' ? 'Candidate' : 'HR';
      setLoggedInUser({ 
        email: data.user.email, 
        role: role, 
        name: data.user.name 
      });
      setUserRole(role);
      setActiveTab(role === 'HR' ? 'Analytics' : 'My Dashboard');
      
      if (role === 'Candidate') {
        // For candidates, find their data
        const cand = candidates.find(c => c.email === data.user.email);
        if (cand) {
          setActiveChatId(cand.id);
          loadCandidateProgress(cand.id);
        }
      } else {
        setActiveChatId(1);
      }
      
      setIsLoggedIn(true);
      setIsLoggingIn(false);
      setLoginEmail('');
      setLoginPassword('');
      
    } catch (error: any) {
      console.error('Login error:', error);
      setLoginError('Unable to connect to server. Please try again.');
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    // Clear JWT token from localStorage
    localStorage.removeItem('auth_token');
    
    setIsLoggedIn(false);
    setLoggedInUser(null);
    setCandidateProgress(null);
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
      <div className="min-h-screen flex flex-col bg-[#f0f4ff] overflow-x-hidden selection:bg-blue-100 relative">
        {/* Abstract Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-200/30 rounded-full blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-200/30 rounded-full blur-[120px]" />
          <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-purple-100/40 rounded-full blur-[100px]" />
        </div>

        {/* Main Content Container */}
        <main className="flex-1 flex flex-col md:flex-row items-center justify-center max-w-7xl mx-auto w-full px-6 lg:px-12 relative z-10 py-12 md:py-0">
          
          {/* Left Column: Hero Content */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="w-full md:w-1/2 flex flex-col items-start space-y-8 md:pr-12"
          >
            {/* Logo Section */}
            <div className="flex items-center gap-4 group">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/30 group-hover:scale-105 transition-transform duration-300">
                <div className="relative">
                  <div className="absolute -top-1 -right-1">
                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2 }}><Sparkles size={10} className="text-white fill-white" /></motion.div>
                  </div>
                  <div className="absolute -bottom-1 -left-1">
                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}><Sparkles size={8} className="text-white fill-white" /></motion.div>
                  </div>
                  <div className="absolute top-1 left-2">
                    <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2, delay: 1 }}><Sparkles size={6} className="text-white fill-white" /></motion.div>
                  </div>
                  <Users size={22} className="text-white" />
                </div>
              </div>
              <span className="text-2xl font-black tracking-tight text-blue-900">OnboardingIQ</span>
            </div>

            {/* Hero Text */}
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-7xl font-black text-slate-900 leading-[1.1] tracking-tight">
                The Digital <br />
                <span className="text-blue-600 relative inline-block">
                  Curator
                  <span className="absolute bottom-1 left-0 w-full h-2 bg-blue-100 -z-10" />
                </span> of <br />
                Talent.
              </h1>
              <p className="text-lg text-slate-600 font-medium max-w-md leading-relaxed">
                Experience the next generation of intelligent workspaces. Automate document workflows and employee integration with AI-driven precision.
              </p>
            </div>

            {/* Security Badge */}
            <div className="flex items-center gap-4 p-4 bg-white/50 backdrop-blur-md rounded-2xl border border-white shadow-sm hover:shadow-md transition-all duration-300">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                <ShieldCheck size={20} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-800">Enterprise Security</h4>
                <p className="text-[11px] text-slate-500 font-medium">SSO and Multi-factor authentication ready.</p>
              </div>
            </div>
          </motion.div>

          {/* Right Column: Login Card */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="w-full md:w-[480px] mt-12 md:mt-0"
          >
            <div className="bg-white rounded-[40px] shadow-[0_20px_50px_rgba(0,0,0,0.06)] p-8 md:p-12 border border-white relative overflow-hidden group">
              {/* Subtle Decorative Gradient */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-50 to-transparent rounded-bl-[100px] -z-0 opacity-50 transition-opacity group-hover:opacity-100" />
              
              <div className="relative z-10">
                <div className="mb-10">
                  <h2 className="text-3xl font-black text-slate-900 tracking-tight">Welcome Back</h2>
                  <p className="text-slate-500 font-medium mt-2">Sign in to your intelligent workspace</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
                    <div className="relative group/input">
                      <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors group-focus-within/input:text-blue-500" />
                      <input 
                        type="email" 
                        required
                        value={loginEmail}
                        onChange={(e) => { setLoginEmail(e.target.value); setLoginError(''); }}
                        placeholder="name@company.com"
                        className="w-full bg-slate-50 border border-slate-100 rounded-2xl pl-12 pr-4 py-4 text-sm font-bold text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/30 transition-all"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center px-1">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Password</label>
                      <button type="button" onClick={() => showToast('Password reset link sent to registered email.', 'info')} className="text-[11px] font-black text-blue-600 hover:text-blue-700 transition-colors uppercase tracking-widest">Forgot?</button>
                    </div>
                    <div className="relative group/input">
                      <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors group-focus-within/input:text-blue-500" />
                      <input 
                        type={showPassword ? 'text' : 'password'}
                        required
                        value={loginPassword}
                        onChange={(e) => { setLoginPassword(e.target.value); setLoginError(''); }}
                        placeholder="••••••••"
                        className="w-full bg-slate-50 border border-slate-100 rounded-2xl pl-12 pr-12 py-4 text-sm font-bold text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/30 transition-all"
                      />
                      <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-blue-600 transition-colors">
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 px-1 pt-1">
                    <input type="checkbox" id="remember" className="w-5 h-5 rounded-lg border-2 border-slate-200 text-blue-600 focus:ring-blue-500 cursor-pointer" />
                    <label htmlFor="remember" className="text-xs font-bold text-slate-500 cursor-pointer select-none">Keep me signed in</label>
                  </div>

                  <AnimatePresence>
                    {loginError && (
                      <motion.div 
                        initial={{ opacity: 0, height: 0 }} 
                        animate={{ opacity: 1, height: 'auto' }} 
                        exit={{ opacity: 0, height: 0 }}
                        className="flex items-center gap-2 px-4 py-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs font-bold"
                      >
                        <AlertTriangle size={14} /> {loginError}
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <button 
                    type="submit"
                    disabled={isLoggingIn}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-[20px] font-black text-sm transition-all duration-300 shadow-xl shadow-blue-500/20 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 group/btn"
                  >
                    {isLoggingIn ? (
                      <><Clock size={18} className="animate-spin" /> Authenticating...</>
                    ) : (
                      <>Continue to Dashboard <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" /></>
                    )}
                  </button>
                </form>

                {/* Demo Credentials Redesigned */}
                <div className="mt-12 pt-8 border-t border-slate-50">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 text-center">Demo Environment Access</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div 
                      onClick={() => { setLoginEmail('hr@konverge.ai'); setLoginPassword('admin123'); setLoginError(''); }}
                      className="cursor-pointer p-4 rounded-2xl bg-slate-50/50 border border-slate-100 hover:bg-white hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/5 transition-all group/cred text-center"
                    >
                      <span className="text-[9px] font-black text-slate-400 uppercase block mb-1">Email</span>
                      <p className="text-[11px] font-black text-slate-600 group-hover/cred:text-blue-600 truncate">demo@onboardingiq.ai</p>
                    </div>
                    <div 
                      onClick={() => { setLoginEmail('tejas@konverge.ai'); setLoginPassword('welcome1'); setLoginError(''); }}
                      className="cursor-pointer p-4 rounded-2xl bg-slate-50/50 border border-slate-100 hover:bg-white hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/5 transition-all group/cred text-center"
                    >
                      <span className="text-[9px] font-black text-slate-400 uppercase block mb-1">Password</span>
                      <p className="text-[11px] font-black text-slate-600 group-hover/cred:text-blue-600">iq-demo-2024</p>
                    </div>
                  </div>
                  <p className="text-center mt-8 text-xs font-bold text-slate-500">
                    Don't have an account? <button onClick={() => showToast('Connecting to Sales team...', 'info')} className="text-blue-600 hover:underline">Contact Sales</button>
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </main>

        {/* Footer */}
        <footer className="relative z-10 px-12 py-8 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] font-black text-slate-400 uppercase tracking-widest border-t border-white/40 backdrop-blur-sm">
          <p>© 2024 OnboardingIQ. All rights reserved.</p>
          <div className="flex items-center gap-8">
            <button className="hover:text-blue-600 transition-colors">Terms of Service</button>
            <button className="hover:text-blue-600 transition-colors">Privacy Policy</button>
            <button className="hover:text-blue-600 transition-colors">Cookie Settings</button>
          </div>
        </footer>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════
  // MAIN DASHBOARD (after login)
  // ═══════════════════════════════════════════════════════
  return (
    <div className="min-h-screen flex bg-[#f0f4ff] font-sans text-slate-800 relative overflow-hidden selection:bg-blue-100">
      
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-5%] left-[-5%] w-[35%] h-[35%] bg-blue-200/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-indigo-200/20 rounded-full blur-[110px]" />
      </div>

      {/* SIDEBAR: Redesigned Light Glass Theme */}
      <aside className="w-72 bg-white/60 backdrop-blur-3xl border-r border-white/40 flex flex-col shrink-0 z-30 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        
        {/* Core Brand Header */}
        <div className="px-8 py-10">
          <div className="flex items-center gap-4 group">
            <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
              <Users size={22} className="text-white" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-blue-900 block leading-tight">OnboardingIQ</span>
              <span className="text-[10px] font-black text-blue-600/60 uppercase tracking-widest leading-none">by Konverge AI</span>
            </div>
          </div>
        </div>

        {/* User Profile Summary */}
        <div className="px-6 mb-8">
          <div className="bg-white/40 border border-white p-4 rounded-[28px] shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-black shadow-md border-2 border-white">
              {loggedInUser?.name.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-black text-slate-800 truncate">{loggedInUser?.name || 'User'}</p>
              <p className="text-[10px] font-bold text-slate-400 truncate uppercase tracking-tighter">{loggedInUser?.role === 'HR' ? 'Human Resources' : 'Talent Joinee'}</p>
            </div>
          </div>
        </div>

        {/* Navigation — role-based */}
        <nav className="flex-1 px-4 space-y-1.5">
          <p className="px-4 text-[10px] font-black text-slate-300 uppercase tracking-[0.2em] mb-4">Main Menu</p>
          {(userRole === 'HR' ? HR_NAV_ITEMS : CANDIDATE_NAV_ITEMS).map(({ label, icon: Icon }) => (
            <button
              key={label}
              onClick={() => setActiveTab(label)}
              className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl text-[13px] font-black tracking-tight transition-all duration-300 group
                ${activeTab === label 
                  ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/20 translate-x-1' 
                  : 'text-slate-500 hover:bg-white/60 hover:text-blue-600 hover:translate-x-1'}`}
            >
              <Icon size={18} className={activeTab === label ? 'text-white' : 'text-slate-400 group-hover:text-blue-500'} />
              {label}
              {activeTab === label && (
                <motion.div layoutId="activeNav" className="ml-auto w-1.5 h-1.5 bg-white rounded-full" />
              )}
            </button>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="mt-auto p-6 space-y-4">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-red-50 hover:bg-red-500 text-red-600 hover:text-white rounded-2xl text-[12px] font-black uppercase tracking-widest transition-all duration-300 group"
          >
            <LogOut size={16} className="group-hover:-translate-x-1 transition-transform" /> Sign Out
          </button>
          
          <div className="flex items-center justify-center gap-2 opacity-30 pt-2 grayscale">
            <img src="/konverge-logo.png" alt="Konverge AI Logo" className="h-6 w-auto object-contain" />
            <div className="w-[1px] h-4 bg-slate-400 mx-1"></div>
            <span className="text-sm font-black tracking-tight text-slate-900">v2.4.0</span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden">
        
        {/* TOP NAVBAR: Simplified and Integrated */}
        <header className="h-24 flex items-center justify-between px-10 shrink-0 z-20">
          <div className="flex items-center gap-4">
            <div className="relative group shadow-sm hover:shadow-md transition-all duration-300 rounded-2xl overflow-hidden bg-white/50 backdrop-blur-md border border-white">
              <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input 
                type="text" 
                placeholder="Search candidates, settings..." 
                className="w-80 pl-12 pr-4 py-3.5 text-sm bg-transparent border-none focus:outline-none focus:ring-0 text-slate-700 placeholder:text-slate-400 font-bold"
                value={directorySearch}
                onChange={(e) => setDirectorySearch(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden xl:flex flex-col items-end border-r border-slate-200 pr-6">
              <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Current Sync</span>
              <span className="text-xs font-black text-slate-600 tabular-nums">{currentTime}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <button title="Messages" onClick={() => setActiveTab('Chat')} className="w-10 h-10 flex items-center justify-center bg-white/50 backdrop-blur-md border border-white hover:bg-blue-50 hover:text-blue-600 rounded-xl relative transition-all shadow-sm">
                <Mail size={18} />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-emerald-500 rounded-full border-2 border-white"></span>
              </button>
              <button title="Notifications" onClick={() => showToast('Activity Feed updated', 'info')} className="w-10 h-10 flex items-center justify-center bg-white/50 backdrop-blur-md border border-white hover:bg-blue-50 hover:text-blue-600 rounded-xl relative transition-all shadow-sm">
                <Bell size={18} />
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-blue-500 rounded-full border-2 border-white"></span>
              </button>
              <button title="Settings" onClick={() => setActiveTab('System Settings')} className="w-10 h-10 flex items-center justify-center bg-white/50 backdrop-blur-md border border-white hover:bg-blue-50 hover:text-blue-600 rounded-xl transition-all shadow-sm">
                <Settings size={18} />
              </button>
            </div>
            
            {/* Minimal User Info */}
            <div className="flex items-center gap-3 pl-2">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-black shadow-lg shadow-blue-500/10">
                {loggedInUser?.name.split(' ').map(n => n[0]).join('') || 'U'}
              </div>
            </div>
          </div>
        </header>

        {/* DASHBOARD CONTENT SWITCHER: Premium spacing & transition */}
        <div className="flex-1 overflow-y-auto px-10 py-12 relative z-10 scrollbar-hide">
          
          <AnimatePresence mode='wait'>
            {/* HR ONLY: Analytics Tab */}
            {activeTab === 'Analytics' && userRole === 'HR' && (
              <motion.div key="analytics" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-10">
                <div className="flex justify-between items-end">
                  <div className="space-y-1">
                    <h2 className="text-4xl font-black text-slate-900 tracking-tight">Analytics Dashboard</h2>
                    <p className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none">Real-time onboarding performance metrics</p>
                  </div>
                  <div className="flex gap-4 items-center">
                    <div className="flex items-center gap-3 bg-white/50 backdrop-blur-md px-4 py-2 rounded-2xl border border-white shadow-sm">
                      <Calendar size={16} className="text-blue-600" />
                      <input 
                        type="date" 
                        value={filterDate}
                        onChange={(e) => setFilterDate(e.target.value)}
                        className="text-[10px] font-black text-slate-600 outline-none bg-transparent cursor-pointer uppercase tracking-tight"
                      />
                      {filterDate && (
                        <button title="Clear Date" onClick={() => setFilterDate('')} className="text-slate-400 hover:text-red-500 ml-1">
                          <X size={14} />
                        </button>
                      )}
                    </div>
                    <button 
                      onClick={() => setIsAddModalOpen(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-[20px] text-xs font-black uppercase tracking-widest flex items-center gap-3 transition-all shadow-lg shadow-blue-500/20 active:scale-95"
                    >
                      <Plus size={18} /> Add New Joinee
                    </button>
                  </div>
                </div>

                {/* KPI Cards Redesigned */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-6">
                  {[
                    { label: 'Onboarded', value: analytics.onboarded.total },
                    { label: 'In Progress', value: analytics.in_progress.total, subtitle: 'Candidates currently onboarding' },
                    {
                      label: 'Pending Tasks',
                      value: analytics.pending_tasks.total,
                      subtitle: `IT: ${analytics.pending_tasks.it} | HR: ${analytics.pending_tasks.hr} | Candidate: ${analytics.pending_tasks.candidate}`
                    },
                    { label: 'Avg Onboarding Time', value: analytics.avg_onboarding_time.avg_days, unit: 'days' },
                  ].map((kpi, i) => (
                    <motion.div 
                      key={kpi.label}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="bg-white/70 backdrop-blur-md rounded-[32px] p-6 shadow-sm border border-white hover:shadow-xl hover:shadow-blue-500/5 transition-all group overflow-hidden relative"
                    >
                       <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-bl-full -z-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                       <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 relative z-10">{kpi.label}</h3>
                       <div className="flex items-baseline gap-1 relative z-10">
                         <p className="text-4xl font-black text-slate-900 tracking-tighter">{kpi.value}</p>
                         {kpi.unit && <span className="text-xs font-bold text-slate-400 uppercase">{kpi.unit}</span>}
                       </div>
                       {kpi.subtitle && (
                         <div className="mt-4 flex items-center gap-2 relative z-10">
                           <span className="text-[9px] font-black px-2 py-1 bg-slate-50 text-slate-600 rounded-lg uppercase tracking-tighter shadow-sm">{kpi.subtitle}</span>
                         </div>
                       )}
                    </motion.div>
                  ))}
                </div>
                {/* Live Activity Stream */}
                <div className="pt-6">
                  <LiveActivityStream />
                </div>

                {/* Candidate Onboarding Progress: Premium List */}
                <div className="space-y-6 pt-10">
                  <div className="flex items-center justify-between px-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 w-full">
                      <div className="space-y-1">
                        <h3 className="text-xl font-bold text-slate-800 tracking-tight">Onboarding Progress</h3>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">Tracking {filteredNavCandidates.length} active onboarding journeys</p>
                      </div>

                      {/* Premium Search Bar for HR */}
                      <div className="flex flex-wrap items-center justify-end gap-3">


                        {/* Manager Filter */}
                        <div className="flex items-center gap-2 rounded-2xl border border-white bg-white/60 px-3 py-2 shadow-sm backdrop-blur-md">
                          <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Manager</span>
                          <select
                            value={filterManager}
                            onChange={(e) => setFilterManager(e.target.value)}
                            className="bg-transparent text-sm font-bold text-slate-700 focus:outline-none max-w-[120px]"
                          >
                            <option value="">All Managers</option>
                            {MANAGERS.map(m => <option key={m} value={m}>{m}</option>)}
                          </select>
                        </div>

                        {/* Department Filter */}
                        <div className="flex items-center gap-2 rounded-2xl border border-white bg-white/60 px-3 py-2 shadow-sm backdrop-blur-md">
                          <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Dept</span>
                          <select
                            value={filterDepartment}
                            onChange={(e) => setFilterDepartment(e.target.value)}
                            className="bg-transparent text-sm font-bold text-slate-700 focus:outline-none max-w-[120px]"
                          >
                            <option value="">All Depts</option>
                            {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                          </select>
                        </div>


                        <div className="relative group shadow-sm hover:shadow-md transition-all duration-300 rounded-2xl overflow-hidden bg-white/50 backdrop-blur-md border border-white">
                          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                          <input 
                            type="text" 
                            placeholder="Find candidate by name..." 
                            className="w-64 pl-12 pr-4 py-3 text-sm bg-transparent border-none focus:outline-none focus:ring-0 text-slate-700 placeholder:text-slate-400 font-bold"
                            value={directorySearch}
                            onChange={(e) => setDirectorySearch(e.target.value)}
                          />
                        </div>
                        <button 
                          onClick={() => {
                            if (!directorySearch) showToast('Please enter a name to search', 'info');
                          }}
                          className="bg-[#2b3553] hover:bg-slate-700 text-white px-5 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all shadow-lg shadow-slate-900/10 active:scale-95 flex items-center gap-2"
                        >
                          <Search size={14} /> Search
                        </button>
                      </div>
                    </div>

                    {/* Pagination - Premium Styled */}
                    {totalPagesNav > 1 && (
                      <div className="flex items-center gap-4 bg-white/80 backdrop-blur-md border border-white/40 rounded-full px-5 py-2 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
                        <span className="text-[11px] font-black text-slate-500 tabular-nums lowercase tracking-tighter">
                          {currentPageNav * itemsPerPageNav + 1}–{Math.min((currentPageNav + 1) * itemsPerPageNav, filteredNavCandidates.length)} of {filteredNavCandidates.length}
                        </span>
                        
                        <div className="flex items-center gap-1.5 border-l border-slate-100 pl-4">
                          <button 
                            onClick={() => setCurrentPageNav(prev => Math.max(0, prev - 1))}
                            disabled={currentPageNav === 0}
                            className="p-1.5 hover:bg-blue-50 rounded-full disabled:opacity-20 disabled:cursor-not-allowed transition-all duration-300 group"
                            title="Previous Page"
                          >
                            <ChevronLeft className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                          </button>

                          <button 
                            onClick={() => setCurrentPageNav(prev => Math.min(totalPagesNav - 1, prev + 1))}
                            disabled={currentPageNav === totalPagesNav - 1}
                            className="p-1.5 hover:bg-blue-50 rounded-full disabled:opacity-20 disabled:cursor-not-allowed transition-all duration-300 group"
                            title="Next Page"
                          >
                            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-6">
                  {currentNavCandidates.map((candidate) => {
                    const candidateTasks = getTasksForCandidate(candidate);
                    const totalTasksCount = candidate.totalTasks || candidateTasks.length;
                    const progress = Math.round(candidate.progress ?? Math.min(100, (candidate.tasksCompleted / totalTasksCount) * 100));
                    const isExpanded = selectedCandidateId === candidate.id;

                    return (
                      <motion.div 
                        key={candidate.id}
                        layout
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`group bg-white/70 backdrop-blur-md rounded-[32px] border transition-all duration-500 hover:shadow-2xl hover:shadow-blue-500/10 ${isExpanded ? 'shadow-xl ring-2 ring-blue-100/50 border-blue-100/30' : 'shadow-sm border-white'}`}
                      >
                        <div 
                          onClick={() => handleExpandCandidate(isExpanded ? null : candidate.id)}
                          className="p-8 cursor-pointer relative overflow-hidden"
                        >
                          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-bl-full -z-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                          
                          <div className="grid gap-8 relative z-10 lg:grid-cols-[minmax(280px,1.35fr)_minmax(430px,1fr)_auto] lg:items-center">
                            {/* Candidate Profile Info */}
                            <div className="flex items-center gap-5 min-w-0">
                              <div className="w-16 h-16 rounded-[24px] bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-black text-2xl shadow-lg shadow-blue-500/20 group-hover:scale-110 transition-transform duration-500">
                                {candidate.name.split(' ').map((n: string) => n[0]).join('')}
                              </div>
                              <div className="min-w-0">
                                <h3 className="truncate text-xl font-black text-slate-800 tracking-tight group-hover:text-blue-600 transition-colors">{candidate.name}</h3>
                                <div className="flex min-w-0 items-center gap-3 mt-1.5">
                                  <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{candidate.position}</span>
                                  <span className="h-1 w-1 shrink-0 rounded-full bg-slate-300"></span>
                                  <span className="truncate text-xs font-bold text-slate-500">{getDepartmentLabel(candidate.department)}</span>
                                </div>
                              </div>
                            </div>

                            {/* Key Stats */}
                            <div className="grid gap-6 sm:grid-cols-3 sm:gap-8 lg:grid-cols-[minmax(150px,1.1fr)_minmax(120px,0.9fr)_minmax(130px,0.9fr)] lg:gap-10">
                              <div className="min-w-0 space-y-1.5">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Reporting To</p>
                                <div className="flex min-w-0 items-center gap-2">
                                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-violet-100"><Users size={12} className="text-violet-600" /></div>
                                  <span className="truncate text-sm font-black text-slate-700">{candidate.manager}</span>
                                </div>
                              </div>
                              <div className="space-y-1.5">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Join Date</p>
                                <div className="flex items-center gap-2">
                                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-blue-100"><Calendar size={12} className="text-blue-600" /></div>
                                  <span className="text-sm font-black text-slate-700">{candidate.date}</span>
                                </div>
                              </div>
                              <div className="space-y-1.5">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Status</p>
                                <span className={`inline-flex px-3 py-1 rounded-xl text-[10px] font-black uppercase tracking-widest
                                  ${candidate.status === 'Onboarded' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : candidate.status === 'Onboarding Started' ? 'bg-blue-50 text-blue-600 border border-blue-100' : 'bg-amber-50 text-amber-600 border border-amber-100'}`}>
                                  {candidate.status}
                                </span>
                              </div>
                            </div>

                            {/* Progress & Actions */}
                            <div className="flex flex-wrap items-center gap-6 lg:justify-self-end">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedCandidateForDetail(candidate);
                                }}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
                              >
                                <Eye size={14} />
                                View Details
                              </button>
                              <div className="flex items-center gap-4 bg-white/50 backdrop-blur-sm px-5 py-4 rounded-3xl border border-white shadow-sm min-w-[200px]">
                                <div className="relative w-12 h-12">
                                  <svg viewBox="0 0 36 36" className="w-12 h-12 -rotate-90">
                                    <circle cx="18" cy="18" r="16" fill="none" stroke="#f1f5f9" strokeWidth="4" />
                                    <motion.circle 
                                      cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeDasharray={`${progress}, 100`} className="text-blue-500" 
                                      initial={{ strokeDashoffset: 100 }} animate={{ strokeDashoffset: 0 }} transition={{ duration: 1, delay: 0.5 }}
                                    />
                                  </svg>
                                  <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black">{progress}%</div>
                                </div>
                                <div className="flex flex-col">
                                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter leading-none mb-1">Journey Progress</span>
                                  <span className="text-sm font-black text-slate-800">{candidate.tasksCompleted}/{totalTasksCount} <span className="text-[10px] font-bold text-slate-400 uppercase italic">Tasks</span></span>
                                </div>
                                <ChevronDown size={18} className={`ml-auto text-slate-400 transition-transform duration-500 ${isExpanded ? 'rotate-180 text-blue-500' : ''}`} />
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
                              className="overflow-hidden border-t border-white/50 bg-white/30"
                            >
                              <div className="p-10">
                                <div className="flex justify-between items-center mb-8">
                                  <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                                      <ListTodo size={20} />
                                    </div>
                                    <h4 className="text-sm font-black text-slate-800 uppercase tracking-widest">Journey Checklist</h4>
                                  </div>
                                  <div className="flex gap-6">
                                    <div className="flex items-center gap-2 text-[9px] font-black text-slate-400 uppercase tracking-widest"><div className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/20"></div> Verified</div>
                                    <div className="flex items-center gap-2 text-[9px] font-black text-slate-400 uppercase tracking-widest"><div className="w-2 h-2 rounded-full bg-blue-500 shadow-sm shadow-blue-500/20"></div> Pending</div>
                                    <div className="flex items-center gap-2 text-[9px] font-black text-slate-400 uppercase tracking-widest"><div className="w-2 h-2 rounded-full bg-amber-500 shadow-sm shadow-amber-500/20"></div> Skipped</div>
                                  </div>
                                </div>

                                <div className="flex flex-col gap-4">
                                  {(candidateTasksMap[candidate.id] || candidateTasks).map((task, idx) => {
                                    const isSkipped = task.is_fallback === true;
                                    const taskStatus = normalizeTaskStatus(task.status);
                                    const isDone = taskStatus === 'completed' && !isSkipped;
                                    const currentTaskIdx = candidateTasksMap[candidate.id] 
                                      ? candidateTasksMap[candidate.id].findIndex((t) => normalizeTaskStatus(t.status) === 'pending')
                                      : (candidate.tasksCompleted || 0);
                                    const isCurrent = candidateTasksMap[candidate.id]
                                      ? (normalizeTaskStatus(task.status) === 'pending' && idx === currentTaskIdx)
                                      : (idx === (candidate.tasksCompleted || 0) && !isSkipped);
                                    
                                    const taskTitle = task.name || task.title;
                                    const taskOwner = task.owner;
                                    const normalizedOwner = (taskOwner || '').toString().toUpperCase().replace(/\s+/g, '_');
                                    const titleKey = (taskTitle || '').toLowerCase();
                                    const isCandidateOwnedTask = normalizedOwner === 'CANDIDATE';
                                    const isHrOwnedTask = normalizedOwner === 'HR';
                                    const isMeetingTask = titleKey.includes('meeting');
                                    const isFinalReviewTask = titleKey.includes('final review');
                                    const isDocumentSigningTask = titleKey.includes('document signing');
                                    const isKarmaTask = titleKey.includes('karma portal');
                                    const isAccountProvisioningTask = titleKey.includes('account provisioning');
                                    const isCandidateAcknowledgedTask = isCandidateOwnedTask || isDocumentSigningTask || isAccountProvisioningTask;
                                    const meetingTypeKey = isMeetingTask
                                      ? getMeetingTypeFromTaskTitle(taskTitle)
                                      : '';
                                    const scheduled = meetingTypeKey
                                      ? scheduledMeetings[candidate.id]?.[meetingTypeKey]
                                      : undefined;
                                    const currentTasks = candidateTasksMap[candidate.id] || [];
                                    const canApproveFinalReview = isFinalReviewTask && currentTasks.length > 0 && currentTasks
                                      .filter((t) => t.id !== task.id)
                                      .every((t) => normalizeTaskStatus(t.status) === 'completed');
                                    
                                    return (
                                      <motion.div 
                                        key={task.id} 
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className={`group/task flex items-center gap-4 p-5 rounded-[24px] border transition-all duration-300 shadow-sm
                                          ${isDone ? 'bg-emerald-50/50 border-emerald-100 hover:bg-emerald-50' : isSkipped ? 'bg-amber-50/30 border-amber-100/50 opacity-80' : isCurrent ? 'bg-white border-blue-200 shadow-xl shadow-blue-500/5 ring-1 ring-blue-100/50' : 'bg-white/50 border-slate-100 opacity-60'}`}
                                      >
                                        
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 font-black text-xs shadow-sm transition-all duration-300
                                          ${isDone ? 'bg-emerald-500 text-white' : isSkipped ? 'bg-amber-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 scale-105' : 'bg-slate-100 text-slate-400'}`}>
                                          {isDone ? <Check size={18} /> : (idx + 1)}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                          <div className="flex items-center gap-2">
                                            <p className={`text-xs font-black truncate tracking-tight transition-colors duration-300 ${isDone ? 'text-emerald-900' : isSkipped ? 'text-amber-900' : isCurrent ? 'text-blue-900' : 'text-slate-500'}`}>{taskTitle}</p>
                                            <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-lg uppercase tracking-widest transition-all duration-300
                                              ${taskOwner === 'HR' ? 'bg-violet-100 text-violet-600' : taskOwner === 'IT' ? 'bg-orange-100 text-orange-600' : taskOwner === 'Candidate' ? 'bg-teal-100 text-teal-600' : taskOwner === 'System' ? 'bg-slate-200 text-slate-600' : taskOwner === 'Delivery Head' ? 'bg-indigo-100 text-indigo-600' : 'bg-blue-100 text-blue-600'}`}>
                                              {taskOwner}
                                            </span>
                                          </div>
                                          
                                          {scheduled && (
                                            <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-blue-50 rounded-lg border border-blue-100">
                                              <Clock size={10} className="text-blue-500" />
                                              <span className="text-[10px] font-bold text-blue-600 truncate">{scheduled.slot} with {scheduled.interviewerName}</span>
                                            </div>
                                          )}

                                          {isCandidateAcknowledgedTask && (
                                            <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-slate-50 rounded-lg border border-slate-100">
                                              <Clock size={10} className="text-slate-500" />
                                              <span className="text-[10px] font-bold text-slate-600 truncate">
                                                {isDone ? 'Acknowledged ✓' : (isKarmaTask ? 'Waiting for candidate acknowledgment' : 'Waiting for candidate')}
                                              </span>
                                            </div>
                                          )}

                                          <div className={`mt-3 flex items-center gap-2 transition-all duration-300 ${(!isDone || isSkipped) ? 'opacity-100 h-auto translate-y-0' : 'opacity-0 h-0 pointer-events-none'}`}>
                                            {!isDone && !isSkipped && isMeetingTask && (
                                              <button 
                                                onClick={(e) => { e.stopPropagation(); setSchedulingTask({ candidateId: candidate.id, taskId: task.id }); }}
                                                className="px-3 py-1.5 bg-blue-600 text-white text-[9px] font-black uppercase tracking-widest rounded-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/20 flex items-center gap-1.5"
                                              >
                                                <Calendar size={12} /> {scheduled ? 'Reschedule' : 'Book Session'}
                                              </button>
                                            )}
                                            {!isDone && isCurrent && taskTitle.toLowerCase().includes('final review') && isHrOwnedTask && (
                                              <button 
                                                onClick={(e) => { e.stopPropagation(); handleCompleteTask(task.id, taskTitle, candidate.id); }}
                                                className="px-3 py-1.5 bg-slate-900 border-slate-900 text-white rounded-lg text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 hover:bg-blue-600 hover:border-blue-600 shadow-lg"
                                              >
                                                <Check size={12} /> Mark Complete
                                              </button>
                                            )}
                                            {!isDone && !taskTitle.toLowerCase().includes('final review') && !isCandidateOwnedTask && (
                                              <button 
                                                onClick={(e) => { e.stopPropagation(); toggleSkipTask(candidate.id, task.id, isSkipped); }}
                                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest border transition-all flex items-center gap-1.5
                                                  ${isSkipped ? 'bg-amber-100 border-amber-200 text-amber-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-amber-50 hover:text-amber-600 hover:border-amber-200'}`}
                                              >
                                                <Zap size={12} /> {isSkipped ? 'Recover' : 'Skip Step'}
                                              </button>
                                            )}
                                          </div>
                                        </div>

                                        <div className={`shrink-0 px-2 py-1 rounded-lg text-[8px] font-black uppercase tracking-widest self-start mt-0.5 shadow-sm
                                          ${isDone ? 'bg-emerald-500 text-white' : isSkipped ? 'bg-amber-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-blue-500/20' : 'bg-white border border-slate-100 text-slate-300'}`}>
                                          {isDone ? 'Done' : isSkipped ? 'Skip' : isCurrent ? 'Active' : 'Wait'}
                                        </div>
                                      </motion.div>
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
          </div>
        </motion.div>
      )}

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

  {/* CANDIDATE ONLY: My Dashboard Tab */}
  {activeTab === 'My Dashboard' && userRole === 'Candidate' && (
    <motion.div key="my-dashboard" variants={pageVariants} initial="initial" animate="animate" exit="exit">
      {(() => {
        // Find myself or fallback
        const myData = candidates.find(c => c.email === loggedInUser?.email) || 
                        candidates.find(c => c.name === loggedInUser?.name) || 
                        candidates[0] ||
                        { name: loggedInUser?.name, department: 'Engineering', date: '03/25/2026', manager: 'Kaustubh Vartak', tasksCompleted: 0, totalTasks: 9 };
        
        // Use real-time progress if available, fallback to candidate summary data
        const displayTasks = candidateProgress?.tasks || [];
        const completedCount = candidateProgress?.completed_tasks ?? myData.tasksCompleted;
        const totalCount = candidateProgress?.total_tasks ?? myData.totalTasks;
        
        const progressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
        const circumference = 2 * Math.PI * 54;
        const dashOffset = circumference - (progressPct / 100) * circumference;
        
        // Next pending task
        const nextTask = displayTasks.find((t: any) => t.status === 'pending');

        if (isRefreshingProgress && !candidateProgress) {
          return (
            <div className="flex flex-col items-center justify-center py-20">
              <Clock className="animate-spin text-blue-600 mb-4" size={48} />
              <p className="text-slate-500 font-bold">Synchronizing your onboarding journey...</p>
            </div>
          );
        }

        return (
          <div className="space-y-6">
            {/* Hero Section */}
            <div className="bg-white/70 backdrop-blur-md rounded-[32px] p-10 border border-white shadow-xl shadow-blue-500/5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-blue-100/20 to-indigo-100/20 rounded-bl-[160px] -z-0 opacity-60"></div>
              
              <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
                <div className="relative shrink-0">
                  <svg width="160" height="160" className="-rotate-90">
                    <circle cx="80" cy="80" r="64" fill="none" stroke="#f1f5f9" strokeWidth="12" />
                    <motion.circle 
                      cx="80" cy="80" r="64" fill="none" stroke="url(#progressGradCandidateLarge)" strokeWidth="12" strokeLinecap="round"
                      strokeDasharray={2 * Math.PI * 64}
                      initial={{ strokeDashoffset: 2 * Math.PI * 64 }}
                      animate={{ strokeDashoffset: 2 * Math.PI * 64 - (progressPct / 100) * (2 * Math.PI * 64) }}
                      transition={{ duration: 2, ease: "easeOut" }}
                    />
                    <defs>
                      <linearGradient id="progressGradCandidateLarge" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#6366f1" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-black text-slate-800">{progressPct}%</span>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Complete</span>
                  </div>
                </div>

                <div className="flex-1">
                  <div className="inline-block px-4 py-1.5 bg-blue-50 border border-blue-100 rounded-full text-blue-600 text-[10px] font-black mb-4 uppercase tracking-[0.2em]">Next-Gen Onboarding</div>
                  <h2 className="text-4xl font-black text-slate-800 mb-2 leading-tight">Welcome to the team, <br/>{loggedInUser?.name}! <span className="animate-pulse">👋</span></h2>
                  <p className="text-slate-500 font-medium mb-8 flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600 text-xs font-bold">{myData.department}</span>
                    &bull; Joined on {myData.date}
                  </p>
                  
                  <div className="grid grid-cols-3 gap-6">
                    <div className="bg-emerald-50 rounded-2xl p-5 border border-emerald-100 shadow-sm">
                      <div className="flex items-center gap-2 mb-2"><CheckCircle2 size={16} className="text-emerald-600" /><span className="text-[9px] font-black text-emerald-700 uppercase tracking-widest">Milestones</span></div>
                      <p className="text-2xl font-black text-emerald-800">{completedCount}<span className="text-sm font-bold text-emerald-500">/{totalCount}</span></p>
                    </div>
                    <div className="bg-blue-50 rounded-2xl p-5 border border-blue-100 shadow-sm relative overflow-hidden group">
                      <div className="flex items-center gap-2 mb-2"><Clock size={16} className="text-blue-600" /><span className="text-[9px] font-black text-blue-700 uppercase tracking-widest">Priority</span></div>
                      <p className="text-xs font-bold text-blue-800 leading-tight line-clamp-1">{nextTask ? nextTask.name : 'All Done!'}</p>
                      <div className="absolute top-0 right-0 p-1 opacity-10 group-hover:scale-110 transition-transform"><Bot size={32} /></div>
                    </div>
                    <div className="bg-violet-50 rounded-2xl p-5 border border-violet-100 shadow-sm">
                      <div className="flex items-center gap-2 mb-2"><Users size={16} className="text-violet-600" /><span className="text-[9px] font-black text-violet-700 uppercase tracking-widest">Guide</span></div>
                      <p className="text-xs font-bold text-violet-800 leading-tight">{myData.manager}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Checklist Section */}
            <div className="space-y-6 pt-6">
              <div className="flex items-center justify-between px-4">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.25em] flex items-center gap-3">
                  Your Journey Path
                  <div className="h-px w-20 bg-slate-100"></div>
                </h3>
                {isRefreshingProgress && <div className="flex items-center gap-2 text-[10px] font-bold text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full"><Clock size={12} className="animate-spin" /> Live Syncing...</div>}
              </div>
              
              <div className="space-y-4">
                {displayTasks.map((task: any, idx: number) => {
                  const isDone = task.status === 'completed';
                  const isCurrent = !isDone && (idx === 0 || displayTasks[idx-1].status === 'completed');
                  const normalizedOwner = (task.owner || '').toString().toUpperCase().replace(/\s+/g, '_');
                  const isCandidateOwnedTask = normalizedOwner === 'CANDIDATE';
                  const isActionableCurrent = isCurrent && isCandidateOwnedTask;
                  
                  return (
                    <motion.div 
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: idx * 0.05 }}
                      key={task.id} 
                      className={`flex items-center gap-6 p-6 rounded-[28px] border transition-all duration-500 group relative
                        ${isDone ? 'bg-emerald-50/30 border-emerald-100/50 grayscale-[0.2] opacity-70' : isCurrent ? 'bg-white border-blue-500/20 shadow-xl shadow-blue-500/5 ring-1 ring-blue-500/10' : 'bg-white/50 border-slate-100'}`}
                    >
                      {isCurrent && <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-blue-600 rounded-r-full shadow-lg shadow-blue-500/50"></div>}
                      
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 font-black shadow-sm transition-all duration-500
                        ${isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 scale-110' : 'bg-slate-100 text-slate-400'}`}>
                        {isDone ? <Check size={24} strokeWidth={3} /> : (idx + 1)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                          <h4 className={`text-md font-bold truncate transition-all duration-500 ${isDone ? 'text-slate-400 line-through' : isCurrent ? 'text-blue-900 text-lg' : 'text-slate-500 font-semibold'}`}>{task.name}</h4>
                          <span className={`text-[8px] font-black px-2 py-0.5 rounded-md uppercase tracking-wider transition-all duration-500
                            ${normalizedOwner === 'HR' ? 'bg-violet-100 text-violet-600' : normalizedOwner === 'IT' ? 'bg-orange-100 text-orange-600' : normalizedOwner === 'CANDIDATE' ? 'bg-teal-100 text-teal-600' : 'bg-blue-100 text-blue-600'}`}>
                            {task.owner}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 font-medium">
                          {isDone 
                            ? `Completed on ${new Date(task.completed_date || Date.now()).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}` 
                            : (isCurrent && isCandidateOwnedTask) ? 'Action required by you' : isCurrent ? 'Pending with task owner' : 'Pending previous steps'}
                        </p>
                      </div>
                      
                      <div className="shrink-0">
                        {!isDone && (() => {
                          const isFinalReview = task.name.toLowerCase().includes('final review');
                          const meetingTypeKey = task.name.toLowerCase().includes('meeting') ? getMeetingTypeFromTaskTitle(task.name) : '';
                          const isMeetingTask = !!meetingTypeKey;
                          const myId = candidateProgress?.candidate_id || myData?.id || candidates.find(c => c.name?.toLowerCase() === loggedInUser?.name?.toLowerCase())?.id;
                          const scheduled = isMeetingTask && myId ? scheduledMeetings[myId]?.[meetingTypeKey] : undefined;
                          const canAcknowledge = isCurrent && isCandidateOwnedTask && (!isMeetingTask || scheduled) && !isFinalReview;
                          const canAcknowledgeTask = canAcknowledge;
                          
                          let btnText = isCurrent ? (isCandidateOwnedTask ? 'Mark Done' : 'Waiting Owner') : 'Upcoming';
                          if (isFinalReview) btnText = 'Final Review Pending';
                          else if (isCurrent && isMeetingTask && !scheduled) btnText = 'Waiting Schedule';

                          return (
                            <button 
                              onClick={() => canAcknowledge && handleCompleteTask(task.id, task.name)}
                              disabled={!canAcknowledge || !canAcknowledgeTask}
                              className={`px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300
                                ${canAcknowledge && canAcknowledgeTask
                                  ? 'bg-slate-900 text-white hover:bg-blue-600 shadow-lg shadow-slate-900/10 active:scale-95 cursor-pointer' 
                                  : 'bg-slate-50 border border-slate-100 text-slate-400 cursor-not-allowed'}`}
                            >
                              Acknowledge
                            </button>
                          );
                        })()}
                        {isDone && (
                          <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 border border-emerald-100 shadow-inner">
                            <CheckCircle2 size={20} />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Floating Support Card */}
            <div className="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-[32px] p-8 mt-10 shadow-2xl flex flex-col md:flex-row items-center justify-between text-white relative overflow-hidden">
               <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
               <div className="flex items-center gap-6 relative z-10 w-full md:w-auto">
                 <div className="w-16 h-16 rounded-3xl bg-white/10 backdrop-blur-md flex items-center justify-center shadow-inner border border-white/10 group-hover:rotate-12 transition-transform">
                   <Bot size={32} className="text-blue-400" />
                 </div>
                 <div>
                   <h4 className="text-xl font-black tracking-tight">Need help navigating?</h4>
                   <p className="text-slate-400 text-xs font-semibold mt-1">Our Onboarding Concierge is available 24/7 to guide you.</p>
                 </div>
               </div>
               <div className="flex gap-4 mt-6 md:mt-0 relative z-10 w-full md:w-auto">
                 <button onClick={() => setIsChatOpen(true)} className="flex-1 md:flex-none px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-black text-[11px] uppercase tracking-widest rounded-2xl shadow-xl shadow-blue-500/20 transition-all active:scale-95">Open AI Chat</button>
                 <button onClick={() => setActiveTab('Help & Support')} className="flex-1 md:flex-none px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-black text-[11px] uppercase tracking-widest rounded-2xl border border-white/10 backdrop-blur-md transition-all">Support Desk</button>
               </div>
            </div>
          </div>
        );
      })()}
    </motion.div>
  )}

  {/* HELP & SUPPORT TAB (Candidate Only) */}
  {activeTab === 'Help & Support' && userRole === 'Candidate' && (
    <motion.div key="help" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="w-10 h-1 bg-blue-600 rounded-full"></span>
            <span className="text-[10px] font-black text-blue-600 uppercase tracking-[0.3em]">Resources</span>
          </div>
          <h1 className="text-4xl font-black text-slate-800 tracking-tight">Support Library</h1>
          <p className="text-slate-500 text-sm font-medium mt-2 max-w-lg leading-relaxed">Everything you need to know about your transition to Konverge.ai. We've compiled the most common questions from our new hires.</p>
        </div>
        <div className="flex gap-2">
          <button className="p-4 bg-white border border-slate-200 rounded-2xl text-slate-600 hover:bg-slate-50 transition-all shadow-sm"><Search size={20} /></button>
          <button onClick={() => setActiveTab('Chat')} className="px-6 py-4 bg-slate-900 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-xl shadow-slate-900/10 active:scale-95 transition-all">Live HR Support</button>
        </div>
      </div>

      {/* FAQ Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[
          { q: 'How do I access VPN?', a: 'After your IT Account Provisioning task is complete, you will receive VPN credentials via email. Install GlobalProtect and use your Keka credentials to connect.', color: 'blue' },
          { q: 'What is the leave policy?', a: 'New joinees are eligible for 18 Casual Leaves, 12 Sick Leaves, and 15 Earned Leaves per year (pro-rated). Leaves can be applied via the Keka portal.', color: 'violet' },
          { q: 'When do I get my laptop?', a: 'Laptops are assigned during the "Asset Assignment" step. IT typically ships within 1-2 business days of your joining date.', color: 'amber' },
          { q: 'How do I access Teams?', a: 'After Account Provisioning (Step 4), you will receive invitations to all relevant Teams channels and SharePoint sites via your newly created company email.', color: 'emerald' },
          { q: 'Who is my onboarding SPOC?', a: 'Your primary HR partner is Mohini Gode. For IT-specific issues, raise a ticket on our internal helpdesk.', color: 'rose' },
          { q: 'Is there a probation period?', a: 'The standard probation period is 6 months. Performance reviews are conducted quarterly to ensure you have the support needed to succeed.', color: 'indigo' },
        ].map((faq, i) => (
          <motion.div 
            whileHover={{ y: -5, borderColor: '#3b82f6' }}
            key={i} 
            className="bg-white rounded-[28px] border border-slate-100 p-8 shadow-sm transition-all duration-300 group"
          >
            <div className={`w-10 h-10 rounded-xl bg-${faq.color}-50 text-${faq.color}-600 flex items-center justify-center shrink-0 text-xs font-black mb-6 group-hover:scale-110 transition-transform`}>
              {i + 1}
            </div>
            <h3 className="text-lg font-black text-slate-800 mb-3">{faq.q}</h3>
            <p className="text-sm text-slate-500 font-medium leading-relaxed">{faq.a}</p>
          </motion.div>
        ))}
      </div>

      {/* Critical Help Card */}
      <div className="bg-white rounded-[32px] border border-slate-100 p-10 shadow-xl shadow-blue-500/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-full bg-blue-600 opacity-[0.03]"></div>
        <div className="relative z-10">
          <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Escalation Contacts</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center shadow-sm"><Mail size={24} /></div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">General HR</p>
                <p className="text-sm font-bold text-slate-800">hr@konverge.ai</p>
                <p className="text-[10px] text-violet-600 font-bold mt-1">Response: {'<'} 4 hrs</p>
              </div>
            </div>
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm"><MessageSquare size={24} /></div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Portal Support</p>
                <p className="text-sm font-bold text-slate-800">Support Chat</p>
                <p className="text-[10px] text-blue-600 font-bold mt-1">Available: 24/7</p>
              </div>
            </div>
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-sm"><PhoneCall size={24} /></div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">IT Hotline</p>
                <p className="text-sm font-bold text-slate-800">+91 (20) 6789 1234</p>
                <p className="text-[10px] text-emerald-600 font-bold mt-1">Immediate Resolution</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )}

  {activeTab === 'Employees' && userRole === 'HR' && (
    <motion.div key="employees" variants={pageVariants} initial="initial" animate="animate" exit="exit" className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between items-start mb-10 gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="w-10 h-1 bg-blue-600 rounded-full"></span>
            <span className="text-[10px] font-black text-blue-600 uppercase tracking-[0.3em]">Registry</span>
          </div>
          <h1 className="text-4xl font-black text-slate-800 tracking-tight">Employee Directory</h1>
          <p className="text-slate-500 text-sm font-medium mt-2">Active personnel and verified profiles within your organization.</p>
        </div>
        <div className="relative w-full md:w-96 group">
          <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          <input 
            type="text" 
            placeholder="Search by name, role or department..." 
            className="w-full bg-white border border-slate-200 rounded-[24px] pl-12 pr-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500 outline-none transition-all shadow-sm group-hover:border-slate-300"
            value={directorySearch}
            onChange={(e) => setDirectorySearch(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {candidates.filter(c => 
          c.name.toLowerCase().includes(directorySearch.toLowerCase()) || 
          c.position.toLowerCase().includes(directorySearch.toLowerCase())
        ).map(c => (
          <motion.div 
            whileHover={{ y: -8, boxShadow: "0px 20px 40px rgba(0,0,0,0.06)" }} 
            key={c.id} 
            className="group bg-white/70 backdrop-blur-md p-8 rounded-[32px] border border-white shadow-sm flex flex-col items-center transition-all duration-500 hover:border-blue-100"
          >
            <div className="relative mb-6">
              <div className="w-20 h-20 rounded-[28px] bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white text-2xl font-black shadow-xl shadow-blue-500/20 group-hover:scale-110 transition-transform duration-500">
                {c.name.split(' ').map((n: string) => n[0]).join('')}
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-emerald-500 rounded-full border-4 border-white shadow-sm"></div>
            </div>

            <h3 className="text-xl font-black text-slate-800 text-center tracking-tight group-hover:text-blue-600 transition-colors">{c.name}</h3>
            <p className="text-blue-500 font-black text-[10px] mb-6 uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full border border-blue-100/50">{c.position}</p>
            
            <div className="w-full grid grid-cols-2 gap-4 py-6 border-y border-slate-50/50 text-[11px] mb-6">
               <div className="flex flex-col gap-1">
                 <span className="text-slate-400 font-black uppercase tracking-widest text-[9px]">Department</span>
                 <span className="text-slate-800 font-bold truncate">{c.department.split('>').pop()?.trim()}</span>
               </div>
               <div className="flex flex-col gap-1">
                 <span className="text-slate-400 font-black uppercase tracking-widest text-[9px]">Reports To</span>
                 <span className="text-slate-800 font-bold truncate">{c.manager}</span>
               </div>
            </div>
            
            <button 
              onClick={() => handleGenericAction(`Viewing ${c.name}'s profile`)} 
              className="w-full py-3.5 bg-slate-900 group-hover:bg-blue-600 text-white rounded-[20px] text-xs font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-slate-900/10 group-hover:shadow-blue-500/20 active:scale-95"
            >
              View Full Profile
            </button>
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
                    <button onClick={() => showToast('Global logic settings are available in the System Settings tab.', 'info')} className="px-5 py-2.5 bg-white border border-slate-200 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all flex items-center gap-2 shadow-sm">
                      <Settings size={14} /> Global Logic
                    </button>
                    <button onClick={() => showToast('Rule creation wizard is available for Enterprise admins.', 'warning')} className="px-5 py-2.5 bg-blue-600 rounded-2xl text-xs font-bold text-white hover:bg-blue-700 transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20 active:scale-95">
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
              <motion.div key="chat" variants={pageVariants} initial="initial" animate="animate" exit="exit">
                <PolicyChatIntegrated 
                  userRole={userRole} 
                  messages={integratedMessages}
                  setMessages={setIntegratedMessages}
                  input={integratedInput}
                  setInput={setIntegratedInput}
                />
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
              {/* Header */}
              <div className="bg-gradient-to-r from-[#2b3553] to-indigo-900 p-4 shrink-0 flex justify-between items-center text-white shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20 shadow-inner">
                    <Bot size={20} className="text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-black leading-tight tracking-tight uppercase tracking-[0.05em]">AI Butler</h3>
                    <div className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      <p className="text-[9px] font-bold text-emerald-300 uppercase tracking-widest">Live Support Active</p>
                    </div>
                  </div>
                </div>
                <button onClick={() => setIsChatOpen(false)} className="hover:bg-white/20 p-2 rounded-xl transition-all active:scale-90 bg-white/5 border border-white/10"><X size={16} /></button>
              </div>
              
              {/* Chat Body */}
              <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-[#fafbfd] scrollbar-hide">
                {floatingMessages.map((msg, mIdx) => (
                  <motion.div 
                    initial={{ opacity: 0, x: msg.type === 'user' ? 20 : -20, scale: 0.95 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    key={msg.id} 
                    className={`flex gap-3 w-full ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <div className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center shadow-lg transition-transform hover:scale-110 
                      ${msg.type === 'bot' ? 'bg-[#2b3553] text-white' : 'bg-gradient-to-br from-blue-500 to-blue-700 text-white text-[10px] font-black'}`}>
                      {msg.type === 'bot' ? <Bot size={16} /> : (loggedInUser?.name.split(' ').map((n: string) => n[0]).join('') || 'TN')}
                    </div>
                    <div className={`p-4 rounded-2xl shadow-[0_4px_15px_rgba(0,0,0,0.03)] border transition-all hover:shadow-[0_8px_25px_rgba(0,0,0,0.05)] w-fit max-w-[85%] relative group
                      ${msg.type === 'bot' 
                        ? 'bg-white rounded-tl-sm border-slate-100 text-slate-700' 
                        : 'bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm border-blue-500/20'
                    }`}>
                      <p className="text-[13px] font-medium leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-100/50 flex flex-col gap-1.5">
                          <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                            <FileText size={10} className="text-blue-500" /> Source Found
                          </p>
                          <div className="px-2 py-1.5 bg-slate-50 rounded-lg border border-slate-100">
                             <p className="text-[10px] font-bold text-slate-600 truncate">{msg.sources[0].policy_name}</p>
                          </div>
                        </div>
                      )}
                      
                      <div className={`absolute bottom-[-18px] ${msg.type === 'user' ? 'right-0' : 'left-0'} opacity-0 group-hover:opacity-100 transition-opacity`}>
                        <p className="text-[9px] font-bold text-slate-400 uppercase">
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {isFloatingLoading && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3 w-full">
                    <div className="w-8 h-8 rounded-xl bg-[#2b3553] shrink-0 flex items-center justify-center text-white shadow-lg"><Bot size={16} /></div>
                    <div className="bg-white p-4 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100">
                      <div className="flex items-center gap-1.5 px-1">
                        <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-blue-500 rounded-full"></motion.span>
                        <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></motion.span>
                        <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-blue-700 rounded-full"></motion.span>
                      </div>
                    </div>
                  </motion.div>
                )}
                <div ref={(el) => el?.scrollIntoView({ behavior: 'smooth' })} />
              </div>

              {/* Input Area */}
              <div className="p-4 bg-white border-t border-slate-100/80 backdrop-blur-sm">
                <form onSubmit={handleFloatingSubmit} className="relative flex items-center group">
                  <input 
                    type="text" 
                    value={floatingInput}
                    onChange={(e) => setFloatingInput(e.target.value)}
                    placeholder="Ask me anything..." 
                    disabled={isFloatingLoading}
                    className="w-full bg-slate-50/50 border border-slate-200 rounded-2xl pl-5 pr-14 py-4 text-[13px] font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none text-slate-700 transition-all placeholder:text-slate-400 disabled:opacity-60 shadow-inner"
                  />
                  <button 
                    type="submit"
                    disabled={!floatingInput.trim() || isFloatingLoading}
                    className={`absolute right-2.5 w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center transition-all shadow-lg active:scale-95
                      ${(!floatingInput.trim() || isFloatingLoading) ? 'opacity-0 scale-75' : 'opacity-100 scale-100 shadow-blue-500/30'}`}
                  >
                    {isFloatingLoading ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      <Send size={18} className="translate-x-0.5 -translate-y-0.5" />
                    )}
                  </button>
                </form>
                <div className="flex items-center justify-center gap-2 mt-3 opacity-40">
                   <div className="w-1 h-1 rounded-full bg-slate-400"></div>
                   <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">AI Concierge v2.0</p>
                   <div className="w-1 h-1 rounded-full bg-slate-400"></div>
                </div>
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
          <div key="add-modal" className="fixed inset-0 z-50 flex items-center justify-center p-4">
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
                    <input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="e.g. First and Last Name" />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Email Address</label>
                    <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="name@company.com" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Joining Date</label>
                    <input required type="date" value={formData.joinDate} onChange={e => setFormData({...formData, joinDate: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase tracking-widest mb-1.5">Position</label>
                    <input required type="text" value={formData.position} onChange={e => setFormData({...formData, position: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-800" placeholder="e.g. Role" />
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



  {/* TOAST SYSTEM (Root Sibling to Main) */}
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

  {/* Candidate Detail View Modal */}
  <AnimatePresence>
    {selectedCandidateForDetail && (
      <CandidateDetailView
        candidate={selectedCandidateForDetail}
        onClose={() => setSelectedCandidateForDetail(null)}
        isHRAdmin={userRole === 'HR'}
      />
    )}
  </AnimatePresence>
</div>
);
}
