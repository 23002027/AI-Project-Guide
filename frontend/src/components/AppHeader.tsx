import React, { useEffect, useState } from 'react';
import type { PageView, User } from '../types';
import { api } from '../services/api';
import {
  Menu,
  Plus,
  Briefcase,
} from 'lucide-react';

interface AppHeaderProps {
  currentPage: PageView;
  onNavigate: (page: PageView) => void;
  onOpenMobileMenu: () => void;
  user?: User | null;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  currentPage,
  onNavigate,
  onOpenMobileMenu,
}) => {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [aiConfigured, setAiConfigured] = useState<boolean>(false);
  const [aiModel, setAiModel] = useState<string>('qwen3:4b');

  useEffect(() => {
    let isMounted = true;
    const fetchStatus = () => {
      api
        .getHealth()
        .then((data) => {
          if (!isMounted) return;
          const online = data.status === 'ok' || data.status === 'healthy';
          setBackendOnline(online);
          const hasOllama = Boolean(
            data.ollama_reachable || data.ai_configured || data.ollama_model_available
          );
          setAiConfigured(hasOllama);
          if (data.ai_model) setAiModel(data.ai_model);
          console.debug(`[APP-HEADER: LLM-STATUS] Backend online: ${online} | LLM ready: ${hasOllama} | Model: ${data.ai_model || 'qwen3:4b'}`);
        })
        .catch(() => {
          if (!isMounted) return;
          setBackendOnline(false);
          setAiConfigured(false);
        });
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const getPageTitle = (page: PageView) => {
    switch (page) {
      case 'dashboard':
        return { title: 'Project Overview', section: 'Workspace' };
      case 'project-guidance':
        return { title: 'Project Guide', section: 'Planning & Specification' };
      case 'workspace':
        return { title: 'Project Workspace', section: 'Execution' };
      case 'ai-agents':
        return { title: 'AI Planning Agent', section: 'Local Intelligence' };
      case 'settings':
        return { title: 'System Settings', section: 'Configuration' };
      default:
        return { title: 'Workspace', section: 'AI Project Guide' };
    }
  };

  const { title, section } = getPageTitle(currentPage);

  return (
    <header className="sticky top-0 z-20 h-14 bg-[#090D18]/90 backdrop-blur-md border-b border-[#26344A] px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Mobile trigger & Breadcrumbs */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenMobileMenu}
          className="md:hidden text-slate-300 hover:text-white p-1.5 rounded-lg hover:bg-[#131D2E] transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400 font-medium hidden sm:inline">{section}</span>
          <span className="text-slate-600 hidden sm:inline">/</span>
          <h2 className="text-white font-semibold tracking-tight">{title}</h2>
        </div>
      </div>

      {/* Right: Live AI Health & Quick Actions */}
      <div className="flex items-center space-x-3">
        {/* Ollama Live Status Pill */}
        <div className="hidden sm:flex items-center space-x-2 bg-[#131D2E] px-2.5 py-1 rounded-full border border-[#26344A] text-[11px]">
          <span
            className={`w-2 h-2 rounded-full ${
              backendOnline && aiConfigured
                ? 'bg-[#27C995] animate-pulse'
                : backendOnline
                ? 'bg-[#F2B85B]'
                : 'bg-rose-500'
            }`}
          />
          <span className="text-slate-300 font-medium">
            {backendOnline && aiConfigured
              ? 'Ollama Live'
              : backendOnline
              ? 'Ollama Offline'
              : 'Backend Offline'}
          </span>
          <span className="text-slate-400 font-mono text-[10px]">({aiModel})</span>
        </div>

        {/* Quick Action Button */}
        {currentPage !== 'project-guidance' ? (
          <button
            onClick={() => onNavigate('project-guidance')}
            className="flex items-center space-x-1.5 bg-[#638BFF] hover:bg-[#4d77f5] text-white px-3 py-1.5 rounded-xl text-xs font-semibold shadow-sm shadow-[#638BFF]/20 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Project Guide</span>
            <span className="sm:hidden">New</span>
          </button>
        ) : (
          <button
            onClick={() => onNavigate('workspace')}
            className="flex items-center space-x-1.5 bg-[#131D2E] hover:bg-[#18253a] text-slate-200 border border-[#26344A] px-3 py-1.5 rounded-xl text-xs font-semibold transition-all hover:scale-[1.02]"
          >
            <Briefcase className="w-3.5 h-3.5 text-[#638BFF]" />
            <span className="hidden sm:inline">Open Workspace</span>
            <span className="sm:hidden">Workspace</span>
          </button>
        )}
      </div>
    </header>
  );
};
