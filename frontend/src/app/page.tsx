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

const updateTaskStatus = async (taskId: number, status: string) => {
  return apiRequest(`/api/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
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

const INTERVIEWERS = [
  { id: 'mohini', name: 'Mohini Moghe', role: 'Senior HR Manager', dept: 'HR', onLeaveUntil: '2026-03-26' },
  { id: 'kalpit', name: 'Kalpit', role: 'Practice Head', dept: 'AI' },
  { id: 'sumit', name: 'Sumit Patil', role: 'Engineering Manager', dept: 'AI' },
  { id: 'ambar', name: 'Ambar Gosavi', role: 'Sales Manager', dept: 'Sales' },
  { id: 'infrastructure', name: 'Infrastructure Team', role: 'Support', dept: 'IT' },
];

const SLOTS = ['09:00 AM', '11:30 AM', '02:00 PM', '04:30 PM'];

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

  // Candidate Progress State
  const [candidateProgress, setCandidateProgress] = useState<any>(null);
  const [isRefreshingProgress, setIsRefreshingProgress] = useState(false);
  const [candidateTasksMap, setCandidateTasksMap] = useState<Record<number, any[]>>({});

  // Smart Onboarding States
  const [skippedTasks, setSkippedTasks] = useState<Record<number, number[]>>({});
  const [scheduledMeetings, setScheduledMeetings] = useState<Record<number, Record<number, { slot: string, interviewerId: string }>>>({});
  const [schedulingTask, setSchedulingTask] = useState<{ candidateId: number, taskId: number } | null>(null);

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
      setCandidates(transformedCandidates);
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

  // Load progress for candidate when logged in
  useEffect(() => {
    if (isLoggedIn && loggedInUser?.role === 'Candidate' && !candidateProgress && !isRefreshingProgress && candidates.length > 0) {
      // Try to find candidate by email first, then name
      const cand = candidates.find(c => c.email?.toLowerCase() === loggedInUser?.email?.toLowerCase()) || 
                   candidates.find(c => c.name?.toLowerCase() === loggedInUser?.name?.toLowerCase());
      
      if (cand) {
        loadCandidateProgress(cand.id);
      } else if (candidates.length > 0) {
        // Fallback for demo/mock users if not in real DB
        // If we're logged in as a candidate but not found, use the first one as a backup
        // This helps during development/testing if emails don't match exactly
        console.warn(`[Dashboard] Candidate ${loggedInUser?.email} not found in DB, using fallback ID: ${candidates[0].id}`);
        loadCandidateProgress(candidates[0].id);
      }
    }
  }, [isLoggedIn, loggedInUser, candidates, candidateProgress, isRefreshingProgress]);

  const loadCandidateProgress = async (id: number) => {
    if (isRefreshingProgress) return;
    setIsRefreshingProgress(true);
    console.log(`[Dashboard] Fetching progress for candidate ID: ${id}`);
    
    try {
      const data = await fetchCandidateProgress(id);
      console.log(`[Dashboard] Received progress data:`, data);
      
      if (!data || !data.tasks || data.tasks.length === 0) {
        console.warn(`[Dashboard] No tasks found in progress data for ID: ${id}`);
      }
      
      setCandidateProgress(data || { tasks: [] });
    } catch (error) {
      console.error(`[Dashboard] Error loading candidate progress (ID: ${id}):`, error);
      showToast('Failed to load your onboarding progress.', 'warning');
      // Set an empty object with error to prevent infinite retries
      setCandidateProgress({ tasks: [], error: true });
    } finally {
      setIsRefreshingProgress(false);
    }
  };

  const handleCompleteTask = async (taskId: number, taskName: string) => {
    try {
      await updateTaskStatus(taskId, 'completed');
      showToast(`"${taskName}" marked as complete!`, 'success');
      
      // Refresh data
      if (loggedInUser?.role === 'Candidate') {
        const candidate = candidates.find(c => c.name === loggedInUser.name);
        if (candidate) {
          await loadCandidateProgress(candidate.id);
        }
      }
      await loadCandidates();
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
    }, 1200);
  };

  const handleLogout = () => {
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
                          onClick={() => handleExpandCandidate(isExpanded ? null : candidate.id)}
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
                                  {(candidateTasksMap[candidate.id] || candidateTasks).map((task, idx) => {
                                    const isSkipped = (skippedTasks[candidate.id] || []).includes(task.id);
                                    const isDone = task.status === 'completed' || idx < (candidate.tasksCompleted || 0);
                                    const scheduled = scheduledMeetings[candidate.id]?.[task.id];
                                    const currentTaskIdx = candidateTasksMap[candidate.id] 
                                      ? candidateTasksMap[candidate.id].findIndex(t => t.status === 'pending')
                                      : (candidate.tasksCompleted || 0);
                                    const isCurrent = candidateTasksMap[candidate.id]
                                      ? (task.status === 'pending' && idx === currentTaskIdx)
                                      : (idx === (candidate.tasksCompleted || 0) && !isSkipped);
                                    
                                    const taskTitle = task.name || task.title;
                                    const taskDesc = task.description || task.desc;
                                    const taskOwner = task.owner;
                                    
                                    return (
                                      <div key={task.id} className={`group flex items-start gap-4 p-4 rounded-2xl border transition-all duration-200 
                                        ${isDone ? 'bg-white border-emerald-100' : isSkipped ? 'bg-amber-50/50 border-amber-100 opacity-80' : isCurrent ? 'bg-white border-blue-200 shadow-lg ring-2 ring-blue-50' : 'bg-white/50 border-gray-100 opacity-60'}`}>
                                        
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 font-extrabold text-sm shadow-sm
                                          ${isDone ? 'bg-emerald-500 text-white' : isSkipped ? 'bg-amber-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-blue-500/20' : 'bg-slate-100 text-slate-400'}`}>
                                          {isDone ? <Check size={18} /> : (idx + 1)}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                          <div className="flex items-center flex-wrap gap-2">
                                            <p className={`text-sm font-bold truncate ${isDone ? 'text-emerald-800' : isSkipped ? 'text-amber-800' : isCurrent ? 'text-blue-900' : 'text-slate-400'}`}>{taskTitle}</p>
                                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter
                                              ${taskOwner === 'HR' ? 'bg-violet-100 text-violet-600' : taskOwner === 'IT' ? 'bg-orange-100 text-orange-600' : taskOwner === 'Candidate' ? 'bg-teal-100 text-teal-600' : taskOwner === 'System' ? 'bg-slate-200 text-slate-600' : 'bg-blue-100 text-blue-600'}`}>
                                              {taskOwner}
                                            </span>
                                          </div>
                                          <p className="text-[11px] text-slate-400 mt-1 leading-tight line-clamp-1">{taskDesc}</p>
                                          
                                          {scheduled && (
                                            <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-blue-50 rounded-lg border border-blue-100">
                                              <Clock size={10} className="text-blue-500" />
                                              <span className="text-[10px] font-bold text-blue-600 truncate">{scheduled.slot} with {INTERVIEWERS.find(i => i.id === scheduled.interviewerId)?.name}</span>
                                            </div>
                                          )}

                                          {/* Action Buttons (Visible on Hover or for Next Step) */}
                                          <div className={`mt-3 flex items-center gap-2 transition-opacity duration-200 ${isCurrent ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                                            {!isDone && !isSkipped && taskTitle.toLowerCase().includes('meeting') && (
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
                            {(() => {
                              const candidate = candidates.find(c => c.id === schedulingTask.candidateId);
                              const task = TASKS_DETAIL.find(t => t.id === schedulingTask.taskId);
                              let suggestedId = 'mohini';
                              if (task?.title.toLowerCase().includes('hr')) suggestedId = 'mohini';
                              else if (task?.title.toLowerCase().includes('infrastructure')) suggestedId = 'infrastructure';
                              else if (task?.title.toLowerCase().includes('practice head')) suggestedId = 'kalpit';
                              else if (task?.title.toLowerCase().includes('reporting manager')) suggestedId = INTERVIEWERS.find(i => i.name === candidate?.manager)?.id || 'mohini';
                              
                              const interviewer = INTERVIEWERS.find(i => i.id === suggestedId);
                              const isOnLeave = interviewer?.onLeaveUntil && new Date(interviewer.onLeaveUntil) > new Date();
                              
                              return (
                                <div className="space-y-4">
                                  <div className={`p-5 rounded-2xl text-white shadow-lg relative overflow-hidden ${isOnLeave ? 'bg-amber-500 shadow-amber-500/20' : 'bg-blue-600 shadow-blue-500/20'}`}>
                                    <div className="relative z-10">
                                      <div className="flex items-center gap-2 mb-3">
                                        {isOnLeave ? <AlertTriangle size={18} className="text-amber-100" /> : <Bot size={18} className="text-blue-200" />}
                                        <span className="text-xs font-bold uppercase tracking-widest text-white/80">{isOnLeave ? 'Interviewer on Leave' : 'Smart Suggestion'}</span>
                                      </div>
                                      
                                      <div className="flex items-center justify-between">
                                        <div>
                                          <p className="text-lg font-bold">{interviewer?.name}</p>
                                          <p className="text-xs text-white/70">{interviewer?.role}</p>
                                          {isOnLeave && <p className="text-[10px] font-bold mt-1 bg-white/20 inline-block px-2 py-0.5 rounded">Back on {interviewer.onLeaveUntil}</p>}
                                        </div>
                                        {!isOnLeave && (
                                          <button 
                                            onClick={() => {
                                              setScheduledMeetings(prev => ({
                                                ...prev,
                                                [schedulingTask.candidateId]: {
                                                  ...(prev[schedulingTask.candidateId] || {}),
                                                  [schedulingTask.taskId]: { slot: SLOTS[1], interviewerId: suggestedId }
                                                }
                                              }));
                                              showToast(`Meeting scheduled with ${interviewer?.name} at ${SLOTS[1]}`, 'success');
                                              setSchedulingTask(null);
                                            }}
                                            className="px-4 py-2 bg-white text-blue-600 rounded-xl font-bold text-xs hover:bg-blue-50 transition-colors shadow-sm"
                                          >
                                            Quick Book
                                          </button>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {isOnLeave && (
                                    <div className="bg-white border-2 border-amber-100 p-4 rounded-2xl animate-pulse">
                                      <button 
                                        onClick={() => {
                                          setScheduledMeetings(prev => ({
                                            ...prev,
                                            [schedulingTask.candidateId]: {
                                              ...(prev[schedulingTask.candidateId] || {}),
                                              [schedulingTask.taskId]: { slot: SLOTS[0], interviewerId: 'sumit' }
                                            }
                                          }));
                                          showToast(`Switched to Sumit Patil (Fallback) and booked for ${SLOTS[0]}`, 'info');
                                          setSchedulingTask(null);
                                        }}
                                        className="mt-3 w-full py-2 bg-amber-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-amber-600 transition-colors"
                                      >
                                        Confirm Fallback
                                      </button>
                                    </div>
                                  )}
                                </div>
                              );
                            })()}

                          <div className="space-y-4">
                            <div>
                              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Manual Selection</label>
                              <select className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium focus:ring-2 focus:ring-blue-500/20 outline-none" defaultValue="...">
                                {INTERVIEWERS.map(int => (
                                  <option key={int.id} value={int.id}>{int.name} ({int.role})</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Available Slots</label>
                              <div className="grid grid-cols-2 gap-2">
                                {SLOTS.map(slot => (
                                  <button key={slot} className="px-4 py-2 border border-slate-100 rounded-xl text-xs font-bold text-slate-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition-all">
                                    {slot}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-3">
                          <button onClick={() => setSchedulingTask(null)} className="flex-1 py-3 text-sm font-bold text-slate-500 hover:text-slate-700 transition-colors">Cancel</button>
                          <button onClick={() => { showToast('Meeting request sent!', 'success'); setSchedulingTask(null); }} className="flex-[2] py-3 bg-[#2b3553] text-white rounded-xl text-sm font-bold shadow-lg shadow-slate-900/10 hover:bg-slate-700 transition-all">Confirm Booking</button>
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
                                <div className="flex items-center gap-2 mb-1"><Clock size={16} className="text-blue-600" /><span className="text-xs font-bold text-blue-700 uppercase tracking-wider">Next Up</span></div>
                                <p className="text-sm font-bold text-blue-800 leading-tight">{nextTask ? nextTask.name : 'All Done!'}</p>
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
                      <div className="space-y-4">
                        <div className="flex items-center justify-between px-2">
                          <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Onboarding Roadmap</h3>
                          {isRefreshingProgress && <div className="flex items-center gap-2 text-[10px] font-bold text-blue-600"><Clock size={12} className="animate-spin" /> Syncing...</div>}
                        </div>
                        
                        <div className="space-y-3">
                          {displayTasks.map((task: any, idx: number) => {
                            const isDone = task.status === 'completed';
                            const isCurrent = !isDone && (idx === 0 || displayTasks[idx-1].status === 'completed');
                            
                            return (
                              <div 
                                key={task.id} 
                                className={`flex items-center gap-4 p-5 rounded-2xl border transition-all duration-300
                                  ${isDone ? 'bg-emerald-50/50 border-emerald-100' : isCurrent ? 'bg-white border-blue-200 shadow-md ring-1 ring-blue-50' : 'bg-white/50 opacity-60 border-gray-100'}`}
                              >
                                <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 font-black shadow-sm transition-all
                                  ${isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 scale-110' : 'bg-slate-100 text-slate-400'}`}>
                                  {isDone ? <Check size={20} /> : (idx + 1)}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2">
                                    <h4 className={`text-sm font-bold truncate ${isDone ? 'text-emerald-800' : isCurrent ? 'text-blue-800' : 'text-slate-500'}`}>{task.name}</h4>
                                    <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter
                                      ${task.owner === 'HR' ? 'bg-violet-100 text-violet-600' : task.owner === 'IT' ? 'bg-orange-100 text-orange-600' : task.owner === 'Candidate' ? 'bg-teal-100 text-teal-600' : 'bg-blue-100 text-blue-600'}`}>
                                      {task.owner}
                                    </span>
                                  </div>
                                  <p className="text-[11px] text-slate-400 mt-0.5 truncate">{isDone ? `Verified as complete on ${new Date(task.completed_date).toLocaleDateString()}` : `Assigned to ${task.assigned_to || task.owner}`}</p>
                                </div>
                                
                                <div className="shrink-0 flex items-center gap-2">
                                  {!isDone && (
                                    <button 
                                      onClick={() => handleCompleteTask(task.id, task.name)}
                                      className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all
                                        ${isCurrent 
                                          ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-500/20 active:scale-95' 
                                          : 'bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200'}`}
                                    >
                                      {task.owner === 'Candidate' ? 'Complete' : 'Acknowledge'}
                                    </button>
                                  )}
                                  {isDone && (
                                    <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 shadow-inner">
                                      <CheckCircle2 size={16} />
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
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
              <PolicyChatIntegrated 
                userRole={userRole} 
                messages={integratedMessages}
                setMessages={setIntegratedMessages}
                input={integratedInput}
                setInput={setIntegratedInput}
              />
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
