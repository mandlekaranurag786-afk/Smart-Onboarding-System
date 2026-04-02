"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Bot, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  RefreshCw,
  TrendingUp,
  FileText
} from 'lucide-react';

interface Activity {
  id: number;
  user_name: string;
  user_role?: string;
  action_text: string;
  target_object?: string;
  activity_type: string;
  icon_type?: string;
  created_at: string;
}

const API_BASE_URL = 'http://localhost:8000';

export default function LiveActivityStream() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchActivities = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/activities/`);
      if (response.ok) {
        const data = await response.json();
        setActivities(data);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error("Failed to fetch activities:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
    const interval = setInterval(fetchActivities, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getIcon = (iconType?: string, activityType?: string) => {
    if (activityType === 'ai') return <Bot className="w-5 h-5 text-cyan-400" />;
    
    switch (iconType) {
      case 'check': return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      case 'alert': return <AlertCircle className="w-5 h-5 text-amber-400" />;
      case 'user': return <User className="w-5 h-5 text-blue-400" />;
      case 'bot': return <Bot className="w-5 h-5 text-cyan-400" />;
      case 'file': return <FileText className="w-5 h-5 text-purple-400" />;
      default: return <User className="w-5 h-5 text-blue-400" />;
    }
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const past = new Date(dateString);
    const diffInMs = now.getTime() - past.getTime();
    const diffInMins = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMins < 1) return 'JUST NOW';
    if (diffInMins < 60) return `${diffInMins} MINUTE${diffInMins === 1 ? '' : 'S'} AGO`;
    if (diffInHours < 24) return `${diffInHours} HOUR${diffInHours === 1 ? '' : 'S'} AGO`;
    return `${diffInDays} DAY${diffInDays === 1 ? '' : 'S'} AGO`;
  };

  return (
    <div className="bg-white/80 backdrop-blur-xl border border-slate-200 rounded-3xl overflow-hidden flex flex-col h-full shadow-xl">
      {/* Header */}
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-xl">
            <TrendingUp className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Live Activity Stream</h2>
            <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">
              Updated {getTimeAgo(lastUpdated.toISOString())}
            </p>
          </div>
        </div>
        <button 
          onClick={() => { setLoading(true); fetchActivities(); }}
          className="p-2 hover:bg-slate-100 rounded-full transition-colors group"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 group-hover:text-blue-600 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {activities.length === 0 && !loading ? (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-12 text-slate-300"
            >
              <Clock className="w-12 h-12 mb-4 opacity-20" />
              <p className="font-medium">No recent activity</p>
            </motion.div>
          ) : (
            activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                className="mb-4 group"
              >
                <div className="bg-slate-50/50 group-hover:bg-white group-hover:shadow-lg group-hover:shadow-blue-500/5 border border-slate-100 group-hover:border-blue-100 p-5 rounded-2xl transition-all duration-300 relative overflow-hidden">
                  {/* Subtle Gradient Glow */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-3xl rounded-full -mr-16 -mt-16 pointer-events-none" />
                  
                  <div className="flex gap-4 items-start relative z-10">
                    <div className={`p-3 rounded-2xl bg-white border border-slate-100 shadow-sm shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                      {getIcon(activity.icon_type, activity.activity_type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap gap-x-2 items-baseline">
                        <span className="text-slate-900 font-bold group-hover:text-blue-600 transition-colors">
                          {activity.user_name}
                        </span>
                        <span className="text-slate-500 text-sm font-medium">
                          {activity.action_text}
                        </span>
                        {activity.target_object && (
                          <span className="text-blue-600 font-bold text-sm">
                            {activity.target_object}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-[10px] text-slate-400 font-black uppercase tracking-wider">
                          {getTimeAgo(activity.created_at)}
                        </span>
                        <div className="w-1 h-1 rounded-full bg-slate-200" />
                        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">
                          {activity.user_role || 'System'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Footer / Stats */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/30">
        <div className="flex items-center justify-between text-[10px] font-black text-slate-400 uppercase tracking-widest px-2">
          <span>{activities.length} Recent Events</span>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-emerald-600">Live Sync Active</span>
          </div>
        </div>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 0, 0, 0.1);
        }
      `}</style>
    </div>
  );
}
