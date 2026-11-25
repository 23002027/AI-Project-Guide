import React, { useState } from 'react';
import { api, ApiError } from '../services/api';
import type { FullProjectBlueprint } from '../types';

export const ProjectGuidancePage: React.FC = () => {
  const [title, setTitle] = useState('AI Construction Safety Monitoring');
  const [description, setDescription] = useState(
    'Real-time computer vision system that monitors safety helmet and reflective vest compliance on construction sites using surveillance video feeds, raising instant alerts for violations.'
  );
  const [domain, setDomain] = useState('AI / Machine Learning');
  const [skills, setSkills] = useState('Python, React, SQL, OpenCV');
  const [experienceLevel, setExperienceLevel] = useState('Intermediate (3rd/4th Year B.Tech Student)');
  const [deadline, setDeadline] = useState('3 months');
  const [teamSize, setTeamSize] = useState(3);
  const [budget, setBudget] = useState('Free / Open Source tier only');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [blueprint, setBlueprint] = useState<FullProjectBlueprint | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'tech' | 'arch' | 'roadmap' | 'prompts' | 'docs'>('analysis');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleLoadSample = () => {
    setTitle('AI Construction Safety Monitoring');
    setDescription(
      'Real-time computer vision system that monitors safety helmet and reflective vest compliance on construction sites using surveillance video feeds, raising instant alerts for violations.'
    );
    setDomain('AI / Machine Learning');
    setSkills('Python, React, SQL, OpenCV');
    setExperienceLevel('Intermediate (3rd/4th Year B.Tech Student)');
    setDeadline('3 months');
    setTeamSize(3);
    setBudget('Free / Open Source tier only');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSaveSuccess(false);

    const payload = {
      title,
      description,
      domain,
      skills: skills.split(',').map((s) => s.trim()).filter(Boolean),
      experience_level: experienceLevel,
      deadline,
      is_team: teamSize > 1,
      team_size: Number(teamSize),
      budget,
    };

    const startTime = Date.now();
    console.log('[PROJECT-GUIDE] >>> Initiating full blueprint generation request to LLM...', {
      title,
      domain,
      skillsCount: payload.skills.length,
    });

    try {
      const data = await api.getFullBlueprint(payload);
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      console.log(`[PROJECT-GUIDE] ✅ LLM IS WORKING PROPERLY | Full blueprint generated in ${elapsed}s`, data);
      setBlueprint(data);
      setActiveTab('analysis');
    } catch (err: any) {
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      console.error(`[PROJECT-GUIDE] ❌ LLM NOT WORKING | Blueprint generation failed after ${elapsed}s:`, err);
      if (err instanceof ApiError) {
        if (err.status === 503) {
          setError('Local Ollama AI engine is not reachable or model qwen3:4b is not responding. Please verify that Ollama is running (`ollama serve`) at http://localhost:11434.');
        } else {
          const detail = typeof err.message === 'string' ? err.message : JSON.stringify(err.message);
          setError(detail || 'Failed to generate project guidance.');
        }
      } else {
        setError(err?.message ? String(err.message) : 'Failed to connect to local AI service.');
      }
    } finally {
      setLoading(false);
    }
  };

  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSaveToWorkspace = () => {
    if (!blueprint) return;
    const existing = JSON.parse(localStorage.getItem('saved_projects') || '[]');
    const firstPhase = blueprint.roadmap?.phases?.[0];
    const initialTasks = (firstPhase?.tasks || firstPhase?.key_milestones || []).slice(0, 5);
    const newProject = {
      id: 'proj-' + Date.now(),
      title,
      domain,
      mode: 'project',
      progress: 25,
      tasks: initialTasks.map((m, idx) => ({
        id: 't-' + idx,
        title: typeof m === 'string' ? m : 'Task ' + (idx + 1),
        category: 'backend',
        status: 'pending',
      })),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      blueprint,
    };
    existing.unshift(newProject);
    localStorage.setItem('saved_projects', JSON.stringify(existing));
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="pb-6 border-b border-[#26344A]">
        <div className="flex items-center space-x-2 text-xs font-semibold text-[#638BFF] uppercase tracking-wider mb-1">
          <span>AI Project Guide • Local Ollama Planning Engine</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Project Guide</h1>
        <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-3xl leading-relaxed">
          Complete engineering specification generator: Feasibility Analysis,
          Free-First Tech Stack, Architecture Diagrams, 9-Phase Roadmap, Copy-Ready Prompts, and IEEE Documentation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form */}
        <div className="lg:col-span-5 bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 h-fit shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Project Specification</h2>
            <button
              type="button"
              onClick={handleLoadSample}
              className="text-xs text-[#638BFF] hover:text-[#4d77f5] font-semibold transition"
            >
              Load Sample Data
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Project Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                placeholder="e.g. AI Construction Safety Monitoring"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Concept Description / Problem</label>
              <textarea
                rows={3}
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF] leading-relaxed"
                placeholder="Describe what your system will do, who uses it, and the engineering challenge..."
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Domain</label>
                <select
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-[#638BFF]"
                >
                  <option value="AI / Machine Learning">AI / Machine Learning</option>
                  <option value="Full-Stack Web Development">Full-Stack Web Development</option>
                  <option value="Healthcare & Biomedical">Healthcare & Biomedical</option>
                  <option value="AgriTech & Smart Farming">AgriTech & Smart Farming</option>
                  <option value="FinTech & Blockchain">FinTech & Blockchain</option>
                  <option value="IoT & Smart Devices">IoT & Smart Devices</option>
                  <option value="Cybersecurity & Privacy">Cybersecurity & Privacy</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Experience Level</label>
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-[#638BFF]"
                >
                  <option value="Beginner (1st/2nd Year Student)">Beginner (1st/2nd Year)</option>
                  <option value="Intermediate (3rd/4th Year B.Tech Student)">Intermediate (3rd/4th Year)</option>
                  <option value="Advanced (Experienced Developer)">Advanced (Experienced)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-slate-300 mb-1">Known Skills</label>
                <input
                  type="text"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                  placeholder="Python, React, SQL"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Team Size</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={teamSize}
                  onChange={(e) => setTeamSize(Number(e.target.value))}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#638BFF]"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Timeframe</label>
                <input
                  type="text"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                  placeholder="3 months"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Budget Limit</label>
                <input
                  type="text"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full bg-[#090D18] border border-[#26344A] rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#638BFF]"
                  placeholder="Free tier only"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-[#638BFF] hover:bg-[#4d77f5] disabled:bg-blue-900 text-white font-bold text-xs transition shadow-lg shadow-[#638BFF]/20 flex items-center justify-center space-x-2 mt-2"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Generating Blueprint with Ollama (qwen3:4b)...</span>
                </>
              ) : (
                <span>Generate Project Blueprint</span>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs leading-relaxed space-y-2">
              <div className="font-semibold flex items-center justify-between">
                <span>Guidance Generation Note:</span>
                <button
                  type="button"
                  onClick={(e) => handleSubmit(e as any)}
                  disabled={loading}
                  className="px-2 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-medium text-[11px] transition"
                >
                  Retry Generation
                </button>
              </div>
              <div>{typeof error === 'string' ? error : JSON.stringify(error)}</div>
            </div>
          )}
        </div>

        {/* Right Column: Output Blueprint Viewer */}
        <div className="lg:col-span-7 space-y-4">
          {blueprint ? (
            <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#26344A] gap-3">
                <div>
                  <h3 className="text-lg font-bold text-white">{blueprint.analysis?.project_title || title}</h3>
                  <div className="text-xs text-[#638BFF] font-medium mt-0.5">
                    Complexity: {blueprint.analysis?.project_complexity || 'High'} • Domain: {blueprint.analysis?.domain || domain}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleSaveToWorkspace}
                    className="bg-[#27C995] hover:bg-[#20b284] text-slate-950 text-xs px-3.5 py-1.5 rounded-xl font-bold transition shadow-sm"
                  >
                    {saveSuccess ? '✓ Saved to Workspace!' : 'Save to Workspace'}
                  </button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex flex-wrap gap-1.5 pt-2 pb-3 border-b border-[#26344A]/60 text-xs font-medium">
                {[
                  { id: 'analysis', label: '1. Problem & USP' },
                  { id: 'tech', label: '2. Tech Stack' },
                  { id: 'arch', label: '3. Architecture' },
                  { id: 'roadmap', label: '4. 9-Phase Roadmap' },
                  { id: 'prompts', label: '5. Coding Prompts' },
                  { id: 'docs', label: '6. IEEE Paper Outline' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setActiveTab(t.id as any)}
                    className={`px-3 py-1.5 rounded-xl transition-all font-semibold ${
                      activeTab === t.id
                        ? 'bg-[#638BFF] text-white shadow-md shadow-[#638BFF]/20'
                        : 'bg-[#090D18] text-slate-400 hover:text-white border border-[#26344A]'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab Content Panels */}
              <div className="pt-4 text-sm">
                {/* 1. Problem Statement & USP */}
                {activeTab === 'analysis' && blueprint.analysis && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Problem Statement</h4>
                      <p className="text-slate-200 mt-1 text-xs leading-relaxed">{blueprint.analysis.problem_statement}</p>
                    </div>

                    {blueprint.analysis.existing_limitations?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Limitations of Existing Work</h4>
                        <ul className="list-disc list-inside text-xs text-slate-300 mt-1 space-y-1">
                          {blueprint.analysis.existing_limitations.map((lim, i) => (
                            <li key={i}>{lim}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Proposed Solution</h4>
                      <p className="text-slate-200 mt-1 text-xs leading-relaxed">{blueprint.analysis.proposed_solution}</p>
                    </div>

                    <div className="bg-blue-900/20 border border-blue-500/30 p-3 rounded-xl">
                      <div className="flex items-center space-x-1.5 text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">
                        <span>⭐ Unique Selling Proposition (USP)</span>
                      </div>
                      <p className="text-blue-200 text-xs leading-relaxed">{blueprint.analysis.unique_selling_proposition}</p>
                    </div>

                    {blueprint.analysis.target_users?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Target Users & Stakeholders</h4>
                        <div className="flex flex-wrap gap-1.5">
                          {blueprint.analysis.target_users.map((user, i) => (
                            <span key={i} className="text-[11px] bg-slate-900 border border-slate-700 text-slate-300 px-2 py-0.5 rounded-md">
                              {user}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Core Measurable Objectives</h4>
                      <ul className="list-disc list-inside text-xs text-slate-300 mt-1 space-y-1">
                        {blueprint.analysis.main_objectives?.map((obj, i) => (
                          <li key={i}>{obj}</li>
                        ))}
                      </ul>
                    </div>

                    {blueprint.analysis.expected_outcomes?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Concrete Deliverables & Outcomes</h4>
                        <ul className="list-disc list-inside text-xs text-slate-300 mt-1 space-y-1">
                          {blueprint.analysis.expected_outcomes.map((out, i) => (
                            <li key={i}>{out}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="grid sm:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                        <span className="font-semibold text-slate-400 block mb-1">Feasibility Assessment</span>
                        <p className="text-slate-300 text-[11px] leading-relaxed">{blueprint.analysis.feasibility_assessment}</p>
                      </div>
                      <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                        <span className="font-semibold text-indigo-400 block mb-1">Innovation Opportunities</span>
                        <ul className="list-disc list-inside text-slate-300 text-[11px] space-y-1">
                          {(blueprint.analysis.innovation_opportunities || []).slice(0, 3).map((inn, i) => (
                            <li key={i}>{inn}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. Technology Stack */}
                {activeTab === 'tech' && blueprint.technology_stack && (
                  <div className="space-y-4">
                    <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-700/80 text-xs">
                      <div className="font-semibold text-white mb-1">Architecture Synergy & Stack Rationale</div>
                      <p className="text-slate-300 leading-relaxed">
                        {blueprint.technology_stack.rationale_summary || blueprint.technology_stack.summary}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Recommended Technologies & Frameworks</h4>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {(blueprint.technology_stack.technology_recommendations || blueprint.technology_stack.technologies || []).map((tech, i) => {
                          const techName = tech.technology_name || tech.tech_name;
                          const role = tech.role_in_project || tech.role;
                          const why = tech.why_suitable || tech.why_recommended;
                          const cost = tech.cost_tier || tech.license_type || 'Free Tier';
                          const guide = tech.implementation_guide;
                          const alts = tech.alternatives || (tech.free_alternative ? [tech.free_alternative] : []);

                          return (
                            <div key={i} className="bg-slate-900/60 border border-slate-700/60 p-3.5 rounded-xl text-xs space-y-2">
                              <div className="flex justify-between items-start gap-2">
                                <div>
                                  <span className="font-bold text-white text-sm block">{techName}</span>
                                  <span className="text-[10px] text-blue-400 font-medium">{role}</span>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">{tech.category}</span>
                                  <span className="text-[9px] bg-emerald-950 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded font-mono">{cost}</span>
                                </div>
                              </div>
                              <p className="text-slate-300 text-[11px] leading-relaxed">{why}</p>
                              {guide && (
                                <div className="text-[11px] bg-slate-950/70 p-2 rounded border border-slate-800/80 text-slate-400">
                                  <span className="text-slate-300 font-medium">Quickstart: </span>{guide}
                                </div>
                              )}
                              {alts.length > 0 && (
                                <div className="text-[10px] text-slate-400">
                                  <span className="text-slate-500">Alternatives: </span>{alts.join(', ')}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {(blueprint.technology_stack.ai_tool_advisors || []).length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2">AI Developer Tools & Assistance</h4>
                        <div className="grid sm:grid-cols-2 gap-3">
                          {blueprint.technology_stack.ai_tool_advisors!.map((tool, i) => (
                            <div key={i} className="bg-slate-900/40 border border-slate-800 p-3 rounded-lg text-xs space-y-1">
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-white">{tool.tool_name}</span>
                                <span className="text-[10px] bg-purple-950 text-purple-300 px-1.5 py-0.5 rounded">{tool.development_activity}</span>
                              </div>
                              <p className="text-slate-300 text-[11px]">{tool.how_to_use}</p>
                              <div className="text-[10px] text-slate-400">
                                <span className="text-slate-500">When: </span>{tool.when_to_use} • <span className="text-emerald-400">Free: </span>{tool.free_alternative}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 3. System Architecture */}
                {activeTab === 'arch' && blueprint.architecture && (
                  <div className="space-y-4">
                    <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-700">
                      <div className="text-xs text-slate-400 font-semibold mb-1">Architecture Overview & Topology</div>
                      <div className="text-xs text-slate-200 leading-relaxed">
                        {blueprint.architecture.high_level_overview || blueprint.architecture.architecture_pattern}
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mermaid System Topology</h4>
                        <button
                          type="button"
                          onClick={() => handleCopyText(blueprint.architecture.mermaid_diagram, 'mermaid')}
                          className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded border border-slate-700"
                        >
                          {copiedId === 'mermaid' ? '✓ Copied Syntax!' : 'Copy Mermaid Code'}
                        </button>
                      </div>
                      <pre className="bg-slate-950 p-4 rounded-xl text-xs font-mono text-emerald-400 overflow-x-auto border border-slate-800">
                        {blueprint.architecture.mermaid_diagram}
                      </pre>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900/40 p-3 rounded-lg border border-slate-800">
                        <span className="font-semibold text-blue-400 block mb-1">Frontend Layer & Flow</span>
                        <span className="text-slate-300 text-[11px] leading-relaxed">
                          {blueprint.architecture.frontend_backend_flow || blueprint.architecture.frontend_layer}
                        </span>
                      </div>
                      <div className="bg-slate-900/40 p-3 rounded-lg border border-slate-800">
                        <span className="font-semibold text-indigo-400 block mb-1">Data & Backend Layer</span>
                        <span className="text-slate-300 text-[11px] leading-relaxed">
                          {blueprint.architecture.database_architecture || blueprint.architecture.backend_layer}
                        </span>
                      </div>
                    </div>

                    {blueprint.architecture.data_flow_explanation && (
                      <div className="bg-slate-900/40 p-3 rounded-lg border border-slate-800 text-xs">
                        <span className="font-semibold text-slate-300 block mb-1">End-to-End Data Flow</span>
                        <p className="text-slate-400 text-[11px] leading-relaxed">{blueprint.architecture.data_flow_explanation}</p>
                      </div>
                    )}

                    {(blueprint.architecture.module_breakdown || []).length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Subsystem Module Breakdown</h4>
                        <div className="space-y-2">
                          {blueprint.architecture.module_breakdown!.map((mod, i) => (
                            <div key={i} className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs">
                              <div className="flex justify-between items-center mb-1">
                                <span className="font-bold text-white">{mod.module_name}</span>
                                <span className="text-[10px] text-slate-400">{mod.technologies_used?.join(', ')}</span>
                              </div>
                              <p className="text-slate-300 text-[11px] mb-1">{mod.responsibility}</p>
                              <div className="text-[10px] text-slate-400 flex gap-4">
                                <span><span className="text-slate-500">In:</span> {mod.inputs}</span>
                                <span><span className="text-slate-500">Out:</span> {mod.outputs}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {(blueprint.architecture.api_endpoint_suggestions || []).length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Suggested REST Endpoints</h4>
                        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 divide-y divide-slate-800/60 font-mono text-[11px]">
                          {blueprint.architecture.api_endpoint_suggestions!.map((ep, i) => (
                            <div key={i} className="py-1.5 flex items-start gap-2 first:pt-0 last:pb-0">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                ep.method === 'GET' ? 'bg-blue-950 text-blue-400' :
                                ep.method === 'POST' ? 'bg-emerald-950 text-emerald-400' :
                                ep.method === 'DELETE' ? 'bg-rose-950 text-rose-400' : 'bg-amber-950 text-amber-400'
                              }`}>{ep.method}</span>
                              <span className="text-white font-semibold">{ep.path}</span>
                              <span className="text-slate-400 font-sans ml-auto text-[10px]">{ep.description}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 4. 9-Phase Roadmap */}
                {activeTab === 'roadmap' && blueprint.roadmap && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center text-xs bg-slate-900/80 p-3 rounded-xl border border-slate-700">
                      <span className="font-semibold text-white">Project Development Roadmap</span>
                      <span className="text-blue-400 font-bold">
                        Total Duration: {blueprint.roadmap.total_estimated_duration || blueprint.roadmap.total_duration || '3 months'}
                      </span>
                    </div>

                    <div className="space-y-3">
                      {(blueprint.roadmap.phases || []).map((phase) => {
                        const phaseTitle = phase.phase_title || phase.phase_name || `Phase ${phase.phase_number}`;
                        const duration = phase.estimated_duration || phase.duration || '2 weeks';
                        const tasks = phase.tasks || phase.key_milestones || [];
                        const checklist = phase.completion_checklist || [];
                        const deliverable = phase.expected_output || phase.deliverables?.join(', ');

                        return (
                          <div key={phase.phase_number} className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl text-xs space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-white text-sm">Phase {phase.phase_number}: {phaseTitle}</span>
                              <span className="text-[11px] bg-slate-800 text-blue-400 px-2 py-0.5 rounded border border-slate-700">{duration}</span>
                            </div>

                            {tasks.length > 0 && (
                              <div>
                                <span className="text-slate-400 font-medium block mb-1">Objectives & Action Items:</span>
                                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                                  {tasks.map((task, tidx) => (
                                    <li key={tidx}>{task}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {checklist.length > 0 && (
                              <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                                <span className="text-emerald-400 font-semibold block mb-1 text-[11px]">Verification Milestones:</span>
                                <div className="space-y-1">
                                  {checklist.map((chk, cidx) => (
                                    <div key={cidx} className="flex items-center space-x-1.5 text-slate-300 text-[11px]">
                                      <span className="text-emerald-500">✓</span>
                                      <span>{chk}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {deliverable && (
                              <div className="text-[11px] text-slate-400">
                                <span className="text-slate-500 font-medium">Deliverable: </span>
                                <span className="text-slate-200">{deliverable}</span>
                              </div>
                            )}

                            {(phase.required_tools || []).length > 0 && (
                              <div className="text-[10px] text-slate-500">
                                Tools: {(phase.required_tools || []).join(', ')}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {blueprint.roadmap.deployment_and_testing && (
                      <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-700/80 text-xs space-y-3">
                        <h4 className="font-bold text-white text-sm">Deployment & Production Readiness Guide</h4>
                        <div className="text-blue-400 text-[11px]">Hosting Target: {blueprint.roadmap.deployment_and_testing.hosting_platform}</div>
                        
                        {blueprint.roadmap.deployment_and_testing.step_by_step_deployment?.length > 0 && (
                          <div>
                            <span className="text-slate-400 font-medium block mb-1">Step-by-Step Deployment:</span>
                            <ol className="list-decimal list-inside space-y-1 text-slate-300 text-[11px]">
                              {blueprint.roadmap.deployment_and_testing.step_by_step_deployment.map((step, idx) => (
                                <li key={idx}>{step}</li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {blueprint.roadmap.deployment_and_testing.testing_strategy?.length > 0 && (
                          <div>
                            <span className="text-slate-400 font-medium block mb-1">Testing Strategy:</span>
                            <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                              {blueprint.roadmap.deployment_and_testing.testing_strategy.map((t, idx) => (
                                <li key={idx}>{t}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Coding Prompts */}
                {activeTab === 'prompts' && (
                  <div className="space-y-4">
                    <p className="text-xs text-slate-400">
                      Copy-ready implementation walkthroughs and prompts tailored for Gemini, Claude, Cursor, and Antigravity IDE:
                    </p>

                    {/* Module Walkthroughs */}
                    {((blueprint.coding_prompts || (blueprint as any).coding_and_prompts)?.module_walkthroughs || []).map((mod: any, i: number) => (
                      <div key={i} className="bg-slate-900/80 border border-slate-700/80 rounded-xl p-4 text-xs space-y-2">
                        <div className="flex justify-between items-center">
                          <h4 className="font-bold text-white text-sm">{mod.module_name}</h4>
                          <span className="text-[10px] text-blue-400 font-mono">{mod.folder_structure}</span>
                        </div>
                        <p className="text-slate-400 text-xs">{mod.purpose}</p>

                        {mod.implementation_steps?.length > 0 && (
                          <div className="space-y-1 py-1">
                            <span className="text-slate-300 font-medium text-[11px]">Implementation Steps:</span>
                            <ol className="list-decimal list-inside text-slate-400 text-[11px] space-y-0.5">
                              {mod.implementation_steps.map((st: string, idx: number) => (
                                <li key={idx}>{st}</li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {mod.example_code_snippet && (
                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-slate-400 text-[10px] font-mono">Example Starter Code</span>
                              <button
                                type="button"
                                onClick={() => handleCopyText(mod.example_code_snippet, `mod-code-${i}`)}
                                className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded border border-slate-700"
                              >
                                {copiedId === `mod-code-${i}` ? '✓ Copied!' : 'Copy Code'}
                              </button>
                            </div>
                            <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-emerald-400 text-[11px] overflow-x-auto">
                              {mod.example_code_snippet}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}

                    {/* Copy-Ready Prompts */}
                    {((blueprint.coding_prompts || (blueprint as any).coding_and_prompts)?.copy_ready_prompts || []).map((prompt: any, i: number) => (
                      <div key={i} className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-xs space-y-2">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/40">{prompt.target_tool}</span>
                            <span className="text-white font-medium">{prompt.use_case}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleCopyText(prompt.prompt_text, `prompt-${i}`)}
                            className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded border border-slate-700 transition"
                          >
                            {copiedId === `prompt-${i}` ? '✓ Copied Prompt!' : 'Copy Full Prompt'}
                          </button>
                        </div>
                        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 font-mono text-slate-300 text-[11px] whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
                          {prompt.prompt_text}
                        </div>
                      </div>
                    ))}

                    {/* Fallback to legacy modules if walkthroughs are empty */}
                    {!((blueprint.coding_prompts || (blueprint as any).coding_and_prompts)?.module_walkthroughs?.length) &&
                      !((blueprint.coding_prompts || (blueprint as any).coding_and_prompts)?.copy_ready_prompts?.length) &&
                      ((blueprint.coding_prompts || (blueprint as any).coding_and_prompts)?.modules || []).map((mod: any, i: number) => (
                        <div key={i} className="bg-slate-900/80 border border-slate-700/80 rounded-xl p-4 text-xs">
                          <h4 className="font-bold text-white text-sm mb-1">{mod.module_name}</h4>
                          <p className="text-slate-400 text-xs mb-3">{mod.description}</p>
                          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-slate-300 text-[11px] whitespace-pre-wrap">
                            {mod.claude_coding_prompt || mod.example_code_snippet || mod.prompt_text}
                          </div>
                        </div>
                      ))}
                  </div>
                )}

                {/* 6. IEEE Paper Outline */}
                {activeTab === 'docs' && blueprint.documentation && (
                  <div className="space-y-4 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-slate-400 text-xs">Final-Year Research Synopsis & Defense Blueprint</span>
                      <button
                        type="button"
                        onClick={() => {
                          const doc = blueprint.documentation;
                          const fullText = `# ${doc.project_title || title}\n\n## Abstract\n${doc.abstract}\n\n## Introduction\n${doc.introduction}\n\n## Problem Statement\n${doc.problem_statement || ''}\n\n## Methodology\n${doc.methodology || doc.system_methodology || ''}\n\n## Conclusion\n${doc.conclusion || doc.conclusion_and_future_work || ''}`;
                          handleCopyText(fullText, 'full-doc');
                        }}
                        className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded border border-slate-700"
                      >
                        {copiedId === 'full-doc' ? '✓ Copied Synopsis!' : 'Copy Full Synopsis'}
                      </button>
                    </div>

                    <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                      <h4 className="font-bold text-white text-sm">Abstract</h4>
                      <p className="text-slate-300 leading-relaxed text-[11px]">{blueprint.documentation.abstract}</p>
                    </div>

                    <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                      <h4 className="font-bold text-white text-sm">Introduction & Problem Domain</h4>
                      <p className="text-slate-300 leading-relaxed text-[11px]">{blueprint.documentation.introduction}</p>
                    </div>

                    {blueprint.documentation.problem_statement && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Academic Problem Formulation</h4>
                        <p className="text-slate-300 leading-relaxed text-[11px]">{blueprint.documentation.problem_statement}</p>
                      </div>
                    )}

                    {(blueprint.documentation.literature_review_outline || []).length > 0 && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
                        <h4 className="font-bold text-white text-sm">Literature Review Framework</h4>
                        <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                          {blueprint.documentation.literature_review_outline!.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {(blueprint.documentation.objectives || []).length > 0 && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Research & Engineering Objectives</h4>
                        <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                          {blueprint.documentation.objectives!.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                      <h4 className="font-bold text-white text-sm">Proposed Methodology</h4>
                      <p className="text-slate-300 leading-relaxed text-[11px]">
                        {blueprint.documentation.methodology || blueprint.documentation.system_methodology}
                      </p>
                    </div>

                    {blueprint.documentation.proposed_architecture_summary && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Proposed Architecture Summary</h4>
                        <p className="text-slate-300 leading-relaxed text-[11px]">{blueprint.documentation.proposed_architecture_summary}</p>
                      </div>
                    )}

                    {blueprint.documentation.testing_methodology && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Testing & Experimental Evaluation Plan</h4>
                        <p className="text-slate-300 leading-relaxed text-[11px]">{blueprint.documentation.testing_methodology}</p>
                      </div>
                    )}

                    {(blueprint.documentation.results_section_template || blueprint.documentation.experimental_results_plan) && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Results Section Template</h4>
                        <p className="text-slate-300 leading-relaxed text-[11px]">
                          {blueprint.documentation.results_section_template || blueprint.documentation.experimental_results_plan}
                        </p>
                      </div>
                    )}

                    {(blueprint.documentation.conclusion || blueprint.documentation.conclusion_and_future_work) && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Conclusion</h4>
                        <p className="text-slate-300 leading-relaxed text-[11px]">
                          {blueprint.documentation.conclusion || blueprint.documentation.conclusion_and_future_work}
                        </p>
                      </div>
                    )}

                    {(blueprint.documentation.future_scope || []).length > 0 && (
                      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                        <h4 className="font-bold text-white text-sm">Future Research Scope</h4>
                        <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                          {blueprint.documentation.future_scope!.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-[#131D2E] border border-dashed border-[#26344A] rounded-2xl p-12 text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-[#638BFF] flex items-center justify-center mx-auto text-xl">
                📘
              </div>
              <h3 className="text-base font-bold text-white">No Capstone Blueprint Generated Yet</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                Fill out the project specification on the left or click "Load Sample Data" and hit "Generate Full Capstone Blueprint" to initiate the multi-agent planning chain.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
