import React, { useState, useEffect } from 'react';
import type { PageView, User, WorkspaceProject } from '../types';
import { api } from '../services/api';
import {
  GraduationCap,
  CheckCircle2,
  Bot,
  FolderOpen,
  ChevronRight,
  Plus,
  Briefcase,
  ListTodo,
} from 'lucide-react';

interface DashboardPageProps {
  user?: User | null;
  onNavigate: (page: PageView) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ user, onNavigate }) => {
  const [projects, setProjects] = useState<WorkspaceProject[]>([]);
  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [greeting, setGreeting] = useState('Welcome back');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Time-based personalized greeting
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');

    const loadRealData = async () => {
      setLoading(true);
      let localProjects: WorkspaceProject[] = [];
      const stored = localStorage.getItem('saved_projects');
      if (stored) {
        try {
          localProjects = JSON.parse(stored);
        } catch {}
      }

      // Fetch backend database projects directly (unauthenticated local backend)
      try {
        const remoteProjects = await api.listProjects();
        if (Array.isArray(remoteProjects) && remoteProjects.length > 0) {
          const mapped: WorkspaceProject[] = remoteProjects.map((rp: any) => ({
            id: rp.id,
            title: rp.title,
            domain: rp.domain || 'AI / Machine Learning',
            mode: 'project',
            progress: rp.progress || 0,
            tasks: (rp.tasks || []).map((t: any) => ({
              id: t.id,
              title: t.title,
              category: t.category || 'backend',
              status: t.status || 'pending',
            })),
            createdAt: rp.created_at || new Date().toISOString(),
            updatedAt: rp.updated_at || new Date().toISOString(),
          }));

          const combined = [...mapped];
          localProjects.forEach((lp) => {
            if (!combined.some((cp) => cp.id === lp.id || cp.title === lp.title)) {
              combined.push(lp);
            }
          });
          localProjects = combined;
          localStorage.setItem('saved_projects', JSON.stringify(combined));
        }
      } catch (err) {
        console.warn('Could not fetch projects from backend:', err);
      }

      setProjects(localProjects);

      try {
        const health = await api.getHealth();
        setBackendHealth(health);
      } catch {}
      setLoading(false);
    };

    loadRealData();
  }, [user]);

  // Derive genuine metrics from real projects
  const totalProjects = projects.length;
  const totalTasks = projects.reduce((acc, p) => acc + (p.tasks?.length || 0), 0);
  const completedTasks = projects.reduce(
    (acc, p) => acc + (p.tasks?.filter((t) => t.status === 'completed').length || 0),
    0
  );
  const overallProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const handleOpenProjectInWorkspace = (projectId: string) => {
    localStorage.setItem('selected_workspace_project_id', projectId);
    onNavigate('workspace');
  };

  const isOllamaOnline = Boolean(
    backendHealth?.ollama_reachable || backendHealth?.ai_configured
  );

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-200">
      {/* Welcome Hero Banner */}
      <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-full bg-gradient-to-l from-[#638BFF]/10 to-transparent pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full bg-[#638BFF]/15 text-[#638BFF] text-[11px] font-semibold border border-[#638BFF]/30">
                AI Project Guide
              </span>
              <span className="text-slate-400 text-xs">
                Local Single-User Workspace
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              {greeting}, {user ? user.name : 'Developer'}
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl leading-relaxed">
              Design complete engineering specifications, Mermaid system architectures, and development roadmaps with the local Ollama AI planning engine.
            </p>
          </div>

          {/* Quick Action Button */}
          <div className="flex flex-wrap gap-3 shrink-0">
            <button
              onClick={() => onNavigate('project-guidance')}
              className="bg-[#638BFF] hover:bg-[#4d77f5] text-white px-5 py-2.5 rounded-xl text-xs font-semibold transition-all shadow-md shadow-[#638BFF]/20 flex items-center space-x-2 hover:scale-[1.02]"
            >
              <Plus className="w-4 h-4" />
              <span>Create New Project</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real Statistics Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Total Projects */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 hover:border-[#384d6d] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Projects</span>
            <div className="w-8 h-8 rounded-xl bg-blue-500/10 text-[#638BFF] flex items-center justify-center border border-blue-500/20">
              <GraduationCap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2">
            {totalProjects}
          </div>
          <div className="text-xs text-[#638BFF] mt-1 font-medium">
            {totalProjects === 1 ? '1 saved project' : `${totalProjects} saved projects`}
          </div>
        </div>

        {/* Metric 2: Milestones & Tasks */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 hover:border-[#384d6d] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Milestones & Tasks</span>
            <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-[#9B7BFF] flex items-center justify-center border border-purple-500/20">
              <ListTodo className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2">
            {totalTasks}
          </div>
          <div className="text-xs text-[#9B7BFF] mt-1 font-medium">
            Across all workspace projects
          </div>
        </div>

        {/* Metric 3: Task Completion */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 hover:border-[#384d6d] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Task Completion</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-[#27C995] flex items-center justify-center border border-emerald-500/20">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#27C995] mt-2">
            {totalTasks > 0 ? `${overallProgress}%` : '0%'}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {completedTasks} of {totalTasks} milestones done
          </div>
        </div>

        {/* Metric 4: AI Planning Engine */}
        <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 hover:border-[#384d6d] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">AI Planning Engine</span>
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white mt-2 truncate">
            {backendHealth?.ai_model || 'qwen3:4b'}
          </div>
          <div className="text-xs text-[#27C995] mt-1 flex items-center space-x-1.5 font-medium">
            <span className={`w-2 h-2 rounded-full ${isOllamaOnline ? 'bg-[#27C995] animate-pulse' : 'bg-[#F2B85B]'}`} />
            <span>{isOllamaOnline ? 'Ollama Local Active' : 'Ollama Offline'}</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Active Workspaces & Quick Action Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (8 cols): Real Projects Feed */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6">
            <div className="flex items-center justify-between pb-4 border-b border-[#26344A] mb-5">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">Saved Projects</h3>
                <p className="text-xs text-slate-400 mt-0.5">Manage and view engineering project blueprints</p>
              </div>
              <button
                onClick={() => onNavigate('workspace')}
                className="text-xs text-[#638BFF] hover:text-[#4d77f5] font-semibold transition flex items-center"
              >
                <span>Open Workspace</span>
                <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </button>
            </div>

            {loading ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                Loading saved projects...
              </div>
            ) : projects.length > 0 ? (
              <div className="space-y-3">
                {projects.slice(0, 6).map((project) => {
                  const tasks = project.tasks || [];
                  const compCount = tasks.filter((t) => t.status === 'completed').length;
                  const pct = tasks.length > 0 ? Math.round((compCount / tasks.length) * 100) : project.progress || 0;

                  return (
                    <div
                      key={project.id}
                      onClick={() => handleOpenProjectInWorkspace(project.id)}
                      className="bg-[#090D18] hover:bg-[#0D1422] border border-[#26344A] hover:border-[#638BFF]/40 rounded-xl p-4 transition-all cursor-pointer group space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/15 text-[#638BFF] border border-blue-500/30">
                              Project
                            </span>
                            <span className="text-xs text-slate-400">{project.domain}</span>
                          </div>
                          <h4 className="text-sm font-bold text-white mt-1 group-hover:text-[#638BFF] transition-colors">
                            {project.title}
                          </h4>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-bold text-white">{pct}%</span>
                          <span className="text-[10px] text-slate-400 block">completed</span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full bg-[#131D2E] h-1.5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-300 bg-[#638BFF]"
                          style={{ width: `${Math.max(pct, 5)}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                        <span className="flex items-center space-x-1">
                          <CheckCircle2 className="w-3 h-3 text-[#27C995]" />
                          <span>{compCount} of {tasks.length} milestones complete</span>
                        </span>
                        <span className="text-slate-400">
                          {new Date(project.updatedAt || project.createdAt).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              /* Helpful Empty State */
              <div className="bg-[#090D18] border border-dashed border-[#26344A] rounded-2xl p-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-[#638BFF] flex items-center justify-center mx-auto">
                  <FolderOpen className="w-6 h-6" />
                </div>
                <h4 className="text-sm font-bold text-white">No active projects yet</h4>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Generate your first engineering project specification and architecture roadmap using the AI Project Guide.
                </p>
                <div className="flex justify-center pt-2">
                  <button
                    onClick={() => onNavigate('project-guidance')}
                    className="bg-[#638BFF] hover:bg-[#4d77f5] text-white px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Create New Project</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (4 cols): Quick Launchpads */}
        <div className="lg:col-span-4 space-y-6">
          {/* Action Card 1: Workspace */}
          <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 space-y-3 hover:border-[#384d6d] transition-all">
            <div className="flex items-center justify-between">
              <div className="w-8 h-8 rounded-xl bg-blue-500/15 text-[#638BFF] flex items-center justify-center">
                <Briefcase className="w-4 h-4" />
              </div>
              <span className="text-[10px] bg-blue-500/10 text-[#638BFF] border border-blue-500/20 px-2 py-0.5 rounded font-medium">
                Workspace
              </span>
            </div>
            <h4 className="text-sm font-bold text-white">Project Workspace</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Track tasks and milestones, record technical notes, and export project deliverables in Markdown or JSON.
            </p>
            <button
              onClick={() => onNavigate('workspace')}
              className="w-full flex items-center justify-center space-x-1.5 bg-[#172439] hover:bg-[#1f304d] text-white text-xs font-semibold py-2 px-3 rounded-xl border border-[#26344A] transition"
            >
              <span>Open Workspace</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Action Card 2: AI Planning Agent */}
          <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 space-y-3 hover:border-[#384d6d] transition-all">
            <div className="flex items-center justify-between">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/15 text-[#27C995] flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <span className="text-[10px] bg-emerald-500/10 text-[#27C995] border border-emerald-500/20 px-2 py-0.5 rounded font-medium">
                Ollama Engine
              </span>
            </div>
            <h4 className="text-sm font-bold text-white">AI Planning Agent</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Inspect the local Ollama planning engine, model connectivity, system status, and structured generation pipeline.
            </p>
            <button
              onClick={() => onNavigate('ai-agents')}
              className="w-full flex items-center justify-center space-x-1.5 bg-[#172439] hover:bg-[#1f304d] text-white text-xs font-semibold py-2 px-3 rounded-xl border border-[#26344A] transition"
            >
              <span>View AI Agent</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
