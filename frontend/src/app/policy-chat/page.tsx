"use client";

import PolicyChatbot from '@/components/PolicyChatbot';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function PolicyChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/"
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>
            <div className="w-[1px] h-6 bg-gray-200"></div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">Company Policy Assistant</h1>
              <p className="text-xs text-slate-500">Ask questions about company policies</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <img src="/konverge-logo.png" alt="Konverge AI" className="h-8 w-auto object-contain" />
            <span className="text-lg font-black text-slate-800">OnboardIQ</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden" style={{ height: 'calc(100vh - 180px)' }}>
          <PolicyChatbot />
        </div>

        {/* Info Cards */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-4 border border-gray-200">
            <div className="text-2xl font-bold text-blue-600 mb-1">10</div>
            <div className="text-xs text-slate-600">Policy Documents</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-200">
            <div className="text-2xl font-bold text-green-600 mb-1">~150</div>
            <div className="text-xs text-slate-600">Searchable Chunks</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-200">
            <div className="text-2xl font-bold text-purple-600 mb-1">&lt;500ms</div>
            <div className="text-xs text-slate-600">Response Time</div>
          </div>
        </div>
      </div>
    </div>
  );
}
