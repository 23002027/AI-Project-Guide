import React, { useState, useEffect } from 'react';
import type { WorkspaceProject, WorkspaceTask } from '../types';
import { api } from '../services/api';
import {
  Briefcase,
  Plus,
  Search,
  Trash2,
  Download,
  FolderOpen,
  FileText,
  Check,
  Presentation,
} from 'lucide-react';

export const ProjectWorkspacePage: React.FC = () => {
  const [projects, setProjects] = useState<WorkspaceProject[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskCategory, setNewTaskCategory] = useState<'frontend' | 'backend' | 'ai' | 'docs' | 'pitch'>('backend');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState<string>('all');
  const [projectNotes, setProjectNotes] = useState<string>('');
  const [notesSaved, setNotesSaved] = useState<boolean>(false);
  const [exportingPptx, setExportingPptx] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  // Load projects from localStorage and backend
  useEffect(() => {
    const loadProjects = async () => {
      let localProjects: WorkspaceProject[] = [];
      const stored = localStorage.getItem('saved_projects');
      if (stored) {
        try {
          localProjects = JSON.parse(stored);
        } catch {}
      }

      // Fetch backend database projects directly
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
        console.warn('Could not fetch backend projects:', err);
      }

      setProjects(localProjects);
      const savedSelected = localStorage.getItem('selected_workspace_project_id');
      if (savedSelected && localProjects.some((p) => p.id === savedSelected)) {
        setSelectedProjectId(savedSelected);
      } else if (localProjects.length > 0) {
        setSelectedProjectId(localProjects[0].id);
      }
    };

    loadProjects();
  }, []);

  const currentProject = projects.find((p) => p.id === selectedProjectId) || projects[0];

  // Load project notes
  useEffect(() => {
    if (currentProject) {
      const notesKey = `notes_${currentProject.id}`;
      setProjectNotes(localStorage.getItem(notesKey) || (currentProject as any).notes || '');
    }
  }, [currentProject?.id]);

  const handleSaveNotes = () => {
    if (!currentProject) return;
    const notesKey = `notes_${currentProject.id}`;
    localStorage.setItem(notesKey, projectNotes);
    setNotesSaved(true);
    setTimeout(() => setNotesSaved(false), 2000);
  };

  const handleToggleTaskStatus = (taskId: string) => {
    if (!currentProject) return;
    const updatedTasks: WorkspaceTask[] = currentProject.tasks.map((t) => {
      if (t.id === taskId) {
        const nextStatus = t.status === 'completed' ? 'pending' : 'completed';
        return { ...t, status: nextStatus };
      }
      return t;
    });

    const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
    const newProgress = Math.round((completedCount / updatedTasks.length) * 100);

    const updatedProjects = projects.map((p) => {
      if (p.id === currentProject.id) {
        return { ...p, tasks: updatedTasks, progress: newProgress, updatedAt: new Date().toISOString() };
      }
      return p;
    });

    setProjects(updatedProjects);
    localStorage.setItem('saved_projects', JSON.stringify(updatedProjects));
  };

  const handleDeleteTask = (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!currentProject) return;
    const updatedTasks = currentProject.tasks.filter((t) => t.id !== taskId);
    const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
    const newProgress = updatedTasks.length > 0 ? Math.round((completedCount / updatedTasks.length) * 100) : 0;

    const updatedProjects = projects.map((p) => {
      if (p.id === currentProject.id) {
        return { ...p, tasks: updatedTasks, progress: newProgress, updatedAt: new Date().toISOString() };
      }
      return p;
    });

    setProjects(updatedProjects);
    localStorage.setItem('saved_projects', JSON.stringify(updatedProjects));
  };

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim() || !currentProject) return;

    const newTask: WorkspaceTask = {
      id: 't-' + Date.now(),
      title: newTaskTitle.trim(),
      category: newTaskCategory,
      status: 'pending',
    };

    const updatedTasks = [...currentProject.tasks, newTask];
    const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
    const newProgress = Math.round((completedCount / updatedTasks.length) * 100);

    const updatedProjects = projects.map((p) => {
      if (p.id === currentProject.id) {
        return { ...p, tasks: updatedTasks, progress: newProgress, updatedAt: new Date().toISOString() };
      }
      return p;
    });

    setProjects(updatedProjects);
    localStorage.setItem('saved_projects', JSON.stringify(updatedProjects));
    setNewTaskTitle('');
  };

  const handleExportDeliverable = (format: 'markdown' | 'json') => {
    if (!currentProject) return;
    let content = '';
    let filename = `${currentProject.title.toLowerCase().replace(/\s+/g, '-')}-workspace`;

    if (format === 'json') {
      content = JSON.stringify(currentProject, null, 2);
      filename += '.json';
    } else {
      content = `# ${currentProject.title}\n\n**Domain:** ${currentProject.domain}\n**Progress:** ${currentProject.progress}%\n\n## Tasks & Milestones\n\n`;
      currentProject.tasks.forEach((t) => {
        content += `- [${t.status === 'completed' ? 'x' : ' '}] (${t.category.toUpperCase()}) ${t.title}\n`;
      });
      if (projectNotes) {
        content += `\n\n## Project Notes\n\n${projectNotes}\n`;
      }
      filename += '.md';
    }

    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPptx = async () => {
    if (!currentProject) return;
    setExportingPptx(true);
    setExportMessage(null);
    try {
      const payload = {
        title: currentProject.title,
        description: currentProject.blueprint?.analysis?.problem_statement || currentProject.title,
        domain: currentProject.domain || 'AI / Engineering',
        problem_statement: currentProject.blueprint?.analysis?.problem_statement || 'Project engineering specification and architecture.',
        target_audience: 'Project Evaluators & Technical Reviewers',
        key_features: currentProject.tasks.slice(0, 5).map((t) => t.title),
        architecture_overview: currentProject.blueprint?.architecture?.high_level_overview || 'Multi-tier system architecture with local processing and modern UI.',
        frontend_stack: ['React 19', 'TypeScript', 'Tailwind CSS'],
        backend_stack: ['Python 3.11', 'FastAPI', 'Ollama (qwen3:4b)'],
        database_stack: ['SQLite'],
        deployment_target: 'Localhost / On-Premise',
        phases: [
          { name: 'Research & Feasibility', duration: 'Phase 1', deliverables: ['Requirements Analysis'] },
          { name: 'System Architecture', duration: 'Phase 2', deliverables: ['System Design', 'API Specs'] },
          { name: 'Implementation', duration: 'Phase 3', deliverables: ['Core Engine', 'UI Integration'] },
          { name: 'Verification & Viva', duration: 'Phase 4', deliverables: ['Final Testing', 'Presentation'] },
        ],
      };
      const blob = await api.generatePptxBlob(payload);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentProject.title.replace(/\s+/g, '_')}_Presentation.pptx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setExportMessage('Presentation (.pptx) downloaded successfully!');
      setTimeout(() => setExportMessage(null), 3000);
    } catch (err: any) {
      setExportMessage('Failed to generate presentation deck: ' + (err.message || 'Error'));
    } finally {
      setExportingPptx(false);
    }
  };

  // Filter tasks based on search & category
  const filteredTasks = (currentProject?.tasks || []).filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategoryFilter === 'all' || task.category === selectedCategoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-[#26344A] gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-[#27C995] uppercase tracking-wider mb-1">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Execution Workspace</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Project Workspace</h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-xl">
            Manage your engineering milestones, maintain implementation notes, filter tasks, and export deliverables.
          </p>
        </div>

        {currentProject && (
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              onClick={() => handleExportDeliverable('markdown')}
              className="bg-[#131D2E] hover:bg-[#18253a] text-slate-300 hover:text-white border border-[#26344A] text-xs px-3 py-2 rounded-xl font-medium transition flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .md</span>
            </button>
            <button
              onClick={() => handleExportDeliverable('json')}
              className="bg-[#131D2E] hover:bg-[#18253a] text-slate-300 hover:text-white border border-[#26344A] text-xs px-3 py-2 rounded-xl font-medium transition flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={handleExportPptx}
              disabled={exportingPptx}
              className="bg-[#638BFF] hover:bg-[#4d77f5] text-white text-xs px-3.5 py-2 rounded-xl font-semibold transition shadow-md shadow-[#638BFF]/20 flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Presentation className="w-3.5 h-3.5" />
              <span>{exportingPptx ? 'Generating PPTX...' : 'Export PPTX'}</span>
            </button>
          </div>
        )}
      </div>

      {exportMessage && (
        <div className="p-3 bg-[#638BFF]/15 border border-[#638BFF]/30 rounded-xl text-xs text-[#638BFF] flex items-center justify-between">
          <span>{exportMessage}</span>
          <button onClick={() => setExportMessage(null)} className="text-slate-400 hover:text-white text-xs ml-3">✕</button>
        </div>
      )}

      {currentProject ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Project Overview, Progress & Notes (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            {/* Project Picker Card */}
            <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 space-y-4">
              <div>
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Active Workspace</span>
                {projects.length > 1 ? (
                  <select
                    value={selectedProjectId}
                    onChange={(e) => {
                      setSelectedProjectId(e.target.value);
                      localStorage.setItem('selected_workspace_project_id', e.target.value);
                    }}
                    className="w-full mt-1.5 bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-sm text-white font-bold focus:outline-none focus:border-[#638BFF] cursor-pointer"
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id} className="bg-[#131D2E] text-white">
                        {p.title}
                      </option>
                    ))}
                  </select>
                ) : (
                  <h2 className="text-base font-bold text-white mt-1 leading-snug">{currentProject.title}</h2>
                )}

                <div className="flex items-center space-x-2 mt-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/15 text-[#638BFF] border border-blue-500/30">
                    Project
                  </span>
                  <span className="text-xs text-slate-400 truncate">{currentProject.domain}</span>
                </div>
              </div>

              {/* Progress Tracker */}
              <div className="pt-2 border-t border-[#26344A]/80">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="text-slate-300 font-medium">Milestone Progress</span>
                  <span className="text-white font-bold">{currentProject.progress}%</span>
                </div>
                <div className="w-full bg-[#090D18] rounded-full h-2 border border-[#26344A] overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-[#638BFF] to-[#27C995] h-full rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(currentProject.progress, 5)}%` }}
                  />
                </div>
                <div className="text-[11px] text-slate-400 mt-1.5">
                  {currentProject.tasks.filter((t) => t.status === 'completed').length} of {currentProject.tasks.length} tasks completed
                </div>
              </div>
            </div>

            {/* Quick Add Task Card */}
            <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 space-y-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                <Plus className="w-3.5 h-3.5 mr-1 text-[#27C995]" /> Add New Task
              </h3>
              <form onSubmit={handleAddTask} className="space-y-3">
                <input
                  type="text"
                  required
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Implement JWT authentication..."
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                />

                <select
                  value={newTaskCategory}
                  onChange={(e) => setNewTaskCategory(e.target.value as any)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-[#638BFF]"
                >
                  <option value="backend">Backend & API</option>
                  <option value="frontend">Frontend & UI</option>
                  <option value="ai">AI Model & Data</option>
                  <option value="docs">Documentation & Viva</option>
                  <option value="pitch">Demo & Pitch</option>
                </select>

                <button
                  type="submit"
                  className="w-full py-2 rounded-xl bg-[#27C995] hover:bg-[#20b284] text-slate-950 font-bold text-xs transition shadow-sm"
                >
                  Add Milestone Task
                </button>
              </form>
            </div>

            {/* Project Implementation Notes */}
            <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                  <FileText className="w-3.5 h-3.5 mr-1 text-[#638BFF]" /> Workspace Notes
                </h3>
                <button
                  onClick={handleSaveNotes}
                  className="text-[10px] bg-[#638BFF]/15 text-[#638BFF] hover:bg-[#638BFF]/25 px-2 py-0.5 rounded font-semibold transition"
                >
                  {notesSaved ? '✓ Saved!' : 'Save Notes'}
                </button>
              </div>
              <textarea
                rows={5}
                value={projectNotes}
                onChange={(e) => setProjectNotes(e.target.value)}
                placeholder="Log architecture decisions, API keys or meeting notes..."
                className="w-full bg-[#090D18] border border-[#26344A] rounded-xl p-3 text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-[#638BFF] leading-relaxed"
              />
            </div>
          </div>

          {/* Right Column: Task Management & Filtering (8 cols) */}
          <div className="lg:col-span-8 bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 space-y-5">
            {/* Search & Category Filter Bar */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-4 border-b border-[#26344A]">
              {/* Search input */}
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search tasks..."
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                />
              </div>

              {/* Category Pills */}
              <div className="flex items-center space-x-1.5 overflow-x-auto text-[11px]">
                {['all', 'frontend', 'backend', 'ai', 'docs', 'pitch'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategoryFilter(cat)}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-colors capitalize ${
                      selectedCategoryFilter === cat
                        ? 'bg-[#638BFF]/15 text-[#638BFF] border border-[#638BFF]/30 font-semibold'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Task Checklist Items */}
            <div className="space-y-2.5">
              {filteredTasks.length > 0 ? (
                filteredTasks.map((task) => {
                  const isDone = task.status === 'completed';
                  return (
                    <div
                      key={task.id}
                      onClick={() => handleToggleTaskStatus(task.id)}
                      className={`flex items-center justify-between p-3.5 rounded-xl border transition-all cursor-pointer group ${
                        isDone
                          ? 'bg-[#090D18]/50 border-[#26344A]/60 text-slate-500'
                          : 'bg-[#090D18] border-[#26344A] hover:border-[#384d6d] text-slate-200'
                      }`}
                    >
                      <div className="flex items-center space-x-3 min-w-0 pr-3">
                        <div
                          className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 transition-colors ${
                            isDone
                              ? 'bg-[#27C995] text-slate-950 font-bold text-xs'
                              : 'border border-[#26344A] bg-[#131D2E] group-hover:border-slate-500'
                          }`}
                        >
                          {isDone && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                        </div>
                        <span className={`text-xs truncate ${isDone ? 'line-through text-slate-500' : 'text-slate-200 font-medium'}`}>
                          {task.title}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0">
                        <span
                          className={`text-[9px] px-2 py-0.5 rounded font-mono uppercase font-semibold ${
                            task.category === 'ai'
                              ? 'bg-purple-500/15 text-[#9B7BFF] border border-purple-500/30'
                              : task.category === 'backend'
                              ? 'bg-blue-500/15 text-[#638BFF] border border-blue-500/30'
                              : task.category === 'frontend'
                              ? 'bg-emerald-500/15 text-[#27C995] border border-emerald-500/30'
                              : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}
                        >
                          {task.category}
                        </span>

                        <button
                          onClick={(e) => handleDeleteTask(task.id, e)}
                          title="Delete task"
                          className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 transition-opacity"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-8 text-center text-slate-400 text-xs border border-dashed border-[#26344A] rounded-xl">
                  No tasks found matching your filter.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#131D2E] border border-dashed border-[#26344A] rounded-2xl p-12 text-center space-y-3">
          <FolderOpen className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-base font-semibold text-white">No Projects in Workspace</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Generate a blueprint in Project Guide and save it to your workspace to track tasks.
          </p>
        </div>
      )}
    </div>
  );
};
