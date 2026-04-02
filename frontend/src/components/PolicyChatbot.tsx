"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, FileText, Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

interface PolicyChatbotProps {
  className?: string;
}

export default function PolicyChatbot({ className = '' }: PolicyChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'bot',
      content: "👋 Hi! I'm your Company Policy Assistant. Ask me anything about our policies - password requirements, remote work, security, BYOD, and more!",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          top_k: 5,
          include_sources: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

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
      console.error('Error querying RAG:', err);
      setError('Failed to get answer. Please ensure the backend is running.');
      
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm having trouble connecting to the policy database. Please make sure the backend server is running and try again.",
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
      high: <CheckCircle2 size={12} />,
      medium: <Info size={12} />,
      low: <AlertCircle size={12} />,
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${styles[confidence as keyof typeof styles]}`}>
        {icons[confidence as keyof typeof icons]}
        {confidence.toUpperCase()} CONFIDENCE
      </span>
    );
  };

  const suggestedQuestions = [
    "What is the password policy?",
    "Can I work remotely?",
    "What is the BYOD policy?",
    "How do I report a security incident?",
  ];

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">Policy Assistant</h2>
            <p className="text-xs text-slate-500">Powered by RAG & AI</p>
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
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {message.confidence && (
                    <div className="mt-2">
                      {getConfidenceBadge(message.confidence)}
                    </div>
                  )}
                </div>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 space-y-2">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-2">Sources:</p>
                    {message.sources.slice(0, 3).map((source, idx) => (
                      <div key={idx} className="bg-white border border-gray-200 rounded-lg p-3 text-xs">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="flex items-center gap-1.5">
                            <FileText size={12} className="text-blue-600 shrink-0" />
                            <span className="font-semibold text-blue-600 text-[11px]">{source.policy_name}</span>
                          </div>
                          <span className="text-[10px] text-slate-500 shrink-0">
                            {(source.similarity_score * 100).toFixed(0)}% match
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 line-clamp-2">{source.excerpt}</p>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-[10px] text-slate-400 mt-1 px-2">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>

              {message.type === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center shrink-0 shadow-md">
                  <User size={16} className="text-slate-600" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 size={16} className="animate-spin text-blue-600" />
                <span className="text-sm text-slate-600">Searching policies...</span>
              </div>
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2"
          >
            <AlertCircle size={16} className="text-red-600 shrink-0" />
            <p className="text-xs text-red-700">{error}</p>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="px-6 pb-4 space-y-2">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInput(question)}
                className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs text-slate-600 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
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
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
