import React, { useState, useEffect } from 'react';
import type { User } from '../types';
import { api } from '../services/api';
import { 
  Server, 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Save, 
  User as UserIcon, 
  Mail, 
  GraduationCap, 
  BookOpen, 
  ShieldCheck,
  HardDrive,
  Bot
} from 'lucide-react';

interface SettingsPageProps {
  user?: User | null;
  onUpdateUser?: (user: User) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ user, onUpdateUser }) => {
  const [name, setName] = useState(user?.name || 'Local Developer');
  const [email, setEmail] = useState(user?.email || 'developer@localhost');
  const [institution, setInstitution] = useState(user?.institution || 'Local Engineering Workspace');
  const [role, setRole] = useState(user?.role || 'Software Engineer');

  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [healthChecking, setHealthChecking] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const checkHealth = async () => {
    setHealthChecking(true);
    try {
      const data = await api.getHealth();
      setBackendHealth(data);
    } catch (err: any) {
      setBackendHealth({ status: 'offline', error: err.message });
    } finally {
      setHealthChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    const updated: User = {
      id: user?.id || 'usr-local',
      name,
      email,
      role,
      institution,
    };
    localStorage.setItem('user_profile', JSON.stringify(updated));
    if (onUpdateUser) onUpdateUser(updated);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const isHealthy = backendHealth?.status === 'ok' || backendHealth?.status === 'healthy';
  const isOllamaOnline = Boolean(
    backendHealth?.ollama_reachable || backendHealth?.ai_configured
  );

  return (
    <div className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn space-y-6">
      {/* Page Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-9 h-9 rounded-xl bg-[#638BFF]/10 border border-[#638BFF]/20 flex items-center justify-center text-[#638BFF]">
            <Server className="w-5 h-5" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">System Settings & Profile</h1>
        </div>
        <p className="text-slate-400 text-sm">
          Manage your developer profile, verify the FastAPI local backend runtime, and monitor Ollama (qwen3:4b) AI status.
        </p>
      </div>

      <div className="space-y-6">
        {/* Backend & AI Health Inspector */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-5 pb-4 border-b border-[#26344A]/80">
            <div>
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-[#638BFF]" />
                <h2 className="text-base font-semibold text-white">Live Infrastructure & Runtime Monitor</h2>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Endpoint: <code className="text-slate-300 font-mono text-[11px]">http://127.0.0.1:8000/api/health</code></p>
            </div>
            <button
              onClick={checkHealth}
              disabled={healthChecking}
              className="inline-flex items-center space-x-2 text-xs bg-[#0D1422] hover:bg-[#1a283e] border border-[#26344A] px-3.5 py-2 rounded-xl text-slate-200 transition font-medium"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${healthChecking ? 'animate-spin text-[#638BFF]' : 'text-slate-400'}`} />
              <span>{healthChecking ? 'Checking...' : 'Refresh Status'}</span>
            </button>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div className="bg-[#090D18]/90 p-4 rounded-xl border border-[#26344A]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-xs font-medium">FastAPI Backend</span>
                <HardDrive className="w-3.5 h-3.5 text-slate-500" />
              </div>
              <div className="flex items-center space-x-2">
                <span className={`w-2.5 h-2.5 rounded-full ${isHealthy ? 'bg-[#27C995] shadow-[0_0_8px_#27C995]' : 'bg-rose-400'}`} />
                <span className="text-white font-bold text-sm">
                  {isHealthy ? 'Online (Port 8000)' : 'Disconnected'}
                </span>
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">Uvicorn ASGI Server</span>
            </div>

            <div className="bg-[#090D18]/90 p-4 rounded-xl border border-[#26344A]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-xs font-medium">Ollama Inference</span>
                <Bot className="w-3.5 h-3.5 text-[#9B7BFF]" />
              </div>
              <div className="flex items-center space-x-2">
                <span className={`w-2.5 h-2.5 rounded-full ${isOllamaOnline ? 'bg-[#27C995] shadow-[0_0_8px_#27C995]' : 'bg-[#F2B85B]'}`} />
                <span className="text-white font-bold text-sm truncate">
                  {isOllamaOnline ? 'Ollama Live (qwen3:4b)' : 'Ollama Offline'}
                </span>
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">http://localhost:11434</span>
            </div>

            <div className="bg-[#090D18]/90 p-4 rounded-xl border border-[#26344A]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-xs font-medium">Planning Agent</span>
                <Server className="w-3.5 h-3.5 text-[#638BFF]" />
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#638BFF] shadow-[0_0_8px_#638BFF]" />
                <span className="text-white font-bold text-sm">Single Planning Agent</span>
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">Structured Pydantic Pipeline</span>
            </div>
          </div>

          {!isOllamaOnline && (
            <div className="mt-4 p-4 rounded-xl bg-[#F2B85B]/10 border border-[#F2B85B]/20 text-xs text-[#F2B85B]">
              <div className="font-semibold flex items-center space-x-2 mb-1">
                <AlertCircle className="w-4 h-4 text-[#F2B85B]" />
                <span>Ollama Local Server Not Detected:</span>
              </div>
              <p className="text-slate-300 text-xs leading-relaxed">
                To enable live local AI generation, ensure the Ollama server is running in the background (`ollama serve`) and the model is downloaded (`ollama run qwen3:4b`).
              </p>
            </div>
          )}
        </div>

        {/* User Profile Form */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl">
          <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-[#26344A]/80">
            <UserIcon className="w-4 h-4 text-[#638BFF]" />
            <h2 className="text-base font-semibold text-white">Developer & Researcher Profile</h2>
          </div>

          {savedSuccess && (
            <div className="mb-5 p-3.5 rounded-xl bg-[#27C995]/15 border border-[#27C995]/30 text-[#27C995] text-xs font-medium flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-[#27C995] shrink-0" />
              <span>Profile settings saved successfully!</span>
            </div>
          )}

          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
                  <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                  <span>Full Name</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#638BFF] transition"
                  placeholder="e.g. Alex Rivera"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  <span>Email</span>
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#638BFF] transition"
                  placeholder="e.g. alex@localhost"
                />
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
                  <GraduationCap className="w-3.5 h-3.5 text-slate-400" />
                  <span>Role / Discipline</span>
                </label>
                <input
                  type="text"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#638BFF] transition"
                  placeholder="e.g. Software Engineer / Student"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  <span>Organization / Institution</span>
                </label>
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#638BFF] transition"
                  placeholder="e.g. Engineering Division"
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="inline-flex items-center space-x-2 py-2.5 px-6 rounded-xl bg-[#638BFF] hover:bg-[#5078ec] text-white font-semibold text-xs transition shadow-lg shadow-[#638BFF]/20"
              >
                <Save className="w-4 h-4" />
                <span>Save Profile Changes</span>
              </button>
            </div>
          </form>
        </div>

        {/* Security & Local Operation Guarantee */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl">
          <div className="flex items-center space-x-2 mb-3">
            <ShieldCheck className="w-4 h-4 text-[#27C995]" />
            <h2 className="text-base font-semibold text-white">Local Privacy & Architecture Guarantee</h2>
          </div>
          <div className="text-xs text-slate-400 space-y-2 leading-relaxed">
            <p>
              • <strong className="text-slate-200">100% Local Inference:</strong> AI generation runs on your local Ollama server with zero remote API telemetry or cloud data sharing.
            </p>
            <p>
              • <strong className="text-slate-200">Private SQLite Persistence:</strong> Workspaces, project drafts, and tasks are saved in your private local SQLite database (<code className="text-slate-300 font-mono text-[11px]">backend/data/copilot.db</code>) and browser storage.
            </p>
            <p>
              • <strong className="text-slate-200">Single-User Operation:</strong> No external authentication or cloud login required for local operation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
