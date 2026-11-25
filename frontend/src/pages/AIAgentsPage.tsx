import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Bot,
  Sparkles,
  Play,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Workflow,
} from 'lucide-react';

interface StageInfo {
  id: string;
  name: string;
  category: string;
  role: string;
  outputDescription: string;
}

const PLANNING_STAGES: StageInfo[] = [
  {
    id: 'problem_analysis',
    name: '1. Problem Statement & USP',
    category: 'Analysis',
    role: 'Deconstructs project ideas into formal academic problem statements, core novelty drivers, and feasibility criteria.',
    outputDescription: 'Formal problem statement, existing limitations, proposed solution, target audience, and unique selling proposition.',
  },
  {
    id: 'tech_advisor',
    name: '2. Technology Stack Advisor',
    category: 'Architecture',
    role: 'Recommends 100% free-tier-first open-source libraries, frontend/backend frameworks, and developer tooling.',
    outputDescription: 'Frontend, backend, database, AI tooling recommendations with licensing and zero-cost constraints.',
  },
  {
    id: 'system_architecture',
    name: '3. System Topology & Diagrams',
    category: 'Architecture',
    role: 'Synthesizes multi-tier component topologies with valid Mermaid.js flowcharts and REST API contracts.',
    outputDescription: 'Mermaid flowchart syntax, tier breakdown, data flow, and REST endpoint definitions.',
  },
  {
    id: 'roadmap_planning',
    name: '4. Development Roadmap',
    category: 'Execution',
    role: 'Schedules semester milestones into phased delivery sprints with weekly targets and production deliverables.',
    outputDescription: 'Sequential development phases from feasibility analysis to final viva defense.',
  },
  {
    id: 'coding_prompts',
    name: '5. Coding Prompts & Boilerplate',
    category: 'Implementation',
    role: 'Generates module walkthroughs, starter boilerplate, and copy-ready AI prompts for modern IDEs.',
    outputDescription: 'Module-by-module implementation steps, setup instructions, and testing guidelines.',
  },
  {
    id: 'documentation',
    name: '6. IEEE Documentation & Synopsis',
    category: 'Documentation',
    role: 'Outlines IEEE academic synopsis, methodology framework, and defense questions.',
    outputDescription: 'Abstract, introduction, methodology, conclusion, and viva defense answers.',
  },
];

export const AIAgentsPage: React.FC = () => {
  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [healthChecking, setHealthChecking] = useState<boolean>(false);
  const [selectedStage, setSelectedStage] = useState<StageInfo>(PLANNING_STAGES[0]);
  
  // Test generation states
  const [testRunning, setTestRunning] = useState<boolean>(false);
  const [testSuccess, setTestSuccess] = useState<boolean | null>(null);
  const [testError, setTestError] = useState<string | null>(null);
  const [testDuration, setTestDuration] = useState<number | null>(null);
  const [testResultPreview, setTestResultPreview] = useState<any>(null);

  const fetchHealth = async () => {
    setHealthChecking(true);
    try {
      console.log('[AI-AGENT-PAGE] Checking LLM health and configuration...');
      const data = await api.getHealth();
      setBackendHealth(data);
      if (data.ollama_reachable && data.ollama_model_available) {
        console.log(`[AI-AGENT-PAGE] ✅ LLM IS WORKING: Provider=${data.ai_provider}, Model=${data.ai_model}`);
      } else {
        console.warn(`[AI-AGENT-PAGE] ⚠️ LLM STATUS: Reachable=${data.ollama_reachable}, ModelAvailable=${data.ollama_model_available}`);
      }
    } catch (err: any) {
      console.error('[AI-AGENT-PAGE] ❌ Backend health check failed:', err);
      setBackendHealth({ status: 'offline', error: err.message });
    } finally {
      setHealthChecking(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleRunDiagnosticTest = async () => {
    setTestRunning(true);
    setTestSuccess(null);
    setTestError(null);
    setTestResultPreview(null);
    const startTime = Date.now();
    console.log('[AI-AGENT-PAGE] >>> Starting LLM diagnostic test request...');

    try {
      const payload = {
        title: 'AI Smart Traffic Congestion Management',
        description: 'Edge-computed computer vision system for adaptive traffic light timing and emergency vehicle prioritization.',
        domain: 'AI / Machine Learning',
        skills: ['Python', 'OpenCV', 'FastAPI', 'React'],
        experience_level: 'Intermediate (3rd/4th Year B.Tech Student)',
        deadline: '3 months',
        is_team: true,
        team_size: 3,
        budget: 'Free tier only',
      };

      const result = await api.analyzeProject(payload);
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      console.log(`[AI-AGENT-PAGE] ✅ LLM IS WORKING PROPERLY: Diagnostic test completed in ${elapsed}s`, result);
      setTestDuration(elapsed);
      setTestResultPreview(result);
      setTestSuccess(true);
    } catch (err: any) {
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      console.error(`[AI-AGENT-PAGE] ❌ LLM NOT WORKING: Diagnostic test failed after ${elapsed}s:`, err);
      setTestDuration(elapsed);
      setTestError(err.message || 'Diagnostic generation failed.');
      setTestSuccess(false);
    } finally {
      setTestRunning(false);
    }
  };

  const isOllamaReachable = Boolean(
    backendHealth?.ollama_reachable || backendHealth?.ai_configured
  );
  const isModelAvailable = Boolean(
    backendHealth?.ollama_model_available || backendHealth?.ai_configured
  );

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#26344A]">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-[#638BFF] uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Local AI Planning Agent</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            AI Planning Agent
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
            Single autonomous project planning agent powered by Ollama and qwen3:4b. Routes structured engineering blueprints across 6 core planning dimensions.
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={fetchHealth}
            disabled={healthChecking}
            className="flex items-center space-x-1.5 bg-[#131D2E] hover:bg-[#18253a] border border-[#26344A] text-slate-300 hover:text-white px-3.5 py-2 rounded-xl text-xs font-semibold transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${healthChecking ? 'animate-spin text-[#638BFF]' : ''}`} />
            <span>{healthChecking ? 'Checking...' : 'Check Status'}</span>
          </button>
        </div>
      </div>

      {/* Ollama Connection & Telemetry Card (Zero Fake Metrics) */}
      <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#26344A]/80 gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-[#638BFF]">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Local Ollama Runtime & Engine Configuration</h2>
              <p className="text-xs text-slate-400">Endpoint: <code className="text-slate-300 font-mono text-[11px]">http://localhost:11434</code></p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`w-2.5 h-2.5 rounded-full ${isOllamaReachable ? 'bg-[#27C995] animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-xs font-semibold text-white">
              {isOllamaReachable ? 'Ollama Online' : 'Ollama Unreachable'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#090D18] p-4 rounded-xl border border-[#26344A]">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Target Model</span>
            <span className="text-base font-bold text-white mt-1 block truncate">
              {backendHealth?.ai_model || 'qwen3:4b'}
            </span>
            <span className="text-[11px] text-[#27C995] mt-1 block font-medium">
              {isModelAvailable ? '✓ Model Loaded & Available' : 'Model Not Detected'}
            </span>
          </div>

          <div className="bg-[#090D18] p-4 rounded-xl border border-[#26344A]">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Context Window</span>
            <span className="text-base font-bold text-white mt-1 block">8,192 Tokens</span>
            <span className="text-[11px] text-slate-400 mt-1 block">Configured Context Limit</span>
          </div>

          <div className="bg-[#090D18] p-4 rounded-xl border border-[#26344A]">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Sampling Temperature</span>
            <span className="text-base font-bold text-white mt-1 block">0.2</span>
            <span className="text-[11px] text-slate-400 mt-1 block">Deterministic JSON Mode</span>
          </div>

          <div className="bg-[#090D18] p-4 rounded-xl border border-[#26344A]">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Output Schema</span>
            <span className="text-base font-bold text-white mt-1 block truncate">Pydantic PlanResponse</span>
            <span className="text-[11px] text-[#638BFF] mt-1 block font-medium">Strict JSON Validation</span>
          </div>
        </div>
      </div>

      {/* 6-Stage Planning Pipeline */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Structured Planning Lifecycle</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            The planning agent guides your project across 6 structured engineering stages:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {PLANNING_STAGES.map((stage) => {
            const isSelected = selectedStage.id === stage.id;
            return (
              <div
                key={stage.id}
                onClick={() => setSelectedStage(stage)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer space-y-3 ${
                  isSelected
                    ? 'bg-[#131D2E] border-[#638BFF] shadow-lg shadow-[#638BFF]/10'
                    : 'bg-[#0D1422] border-[#26344A] hover:border-[#384d6d]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-[#638BFF]/15 text-[#638BFF] border border-[#638BFF]/30">
                    {stage.category}
                  </span>
                  <Workflow className={`w-4 h-4 ${isSelected ? 'text-[#638BFF]' : 'text-slate-500'}`} />
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white">{stage.name}</h3>
                  <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                    {stage.role}
                  </p>
                </div>

                <div className="pt-2 border-t border-[#26344A]/80 text-[11px] text-slate-400">
                  <span className="font-semibold text-slate-300">Deliverable: </span>
                  <span>{stage.outputDescription}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Diagnostic Generation Tester */}
      <div className="bg-[#131D2E] border border-[#26344A] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#26344A] gap-3">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Diagnostic Generation Test</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Verify local Ollama inference and Pydantic validation by running a live analysis test request.
            </p>
          </div>

          <button
            onClick={handleRunDiagnosticTest}
            disabled={testRunning || !isOllamaReachable}
            className="flex items-center space-x-2 bg-[#638BFF] hover:bg-[#4d77f5] disabled:bg-slate-800 text-white px-4 py-2 rounded-xl text-xs font-bold transition shadow-md shadow-[#638BFF]/20"
          >
            {testRunning ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating with Ollama...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                <span>Run Diagnostic Test</span>
              </>
            )}
          </button>
        </div>

        {testRunning && (
          <div className="p-4 rounded-xl bg-[#090D18] border border-[#26344A] text-xs text-slate-300 flex items-center space-x-3">
            <span className="w-4 h-4 border-2 border-[#638BFF]/30 border-t-[#638BFF] rounded-full animate-spin shrink-0" />
            <div>
              <span className="font-semibold text-white">Local Inference Active: </span>
              <span>Model qwen3:4b is generating structured JSON response without thinking tags. This typically takes 60–150 seconds depending on GPU/RAM offload.</span>
            </div>
          </div>
        )}

        {testSuccess === true && (
          <div className="p-4 rounded-xl bg-[#27C995]/15 border border-[#27C995]/30 text-xs text-[#27C995] space-y-2">
            <div className="flex items-center space-x-2 font-bold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Diagnostic Test Passed in {testDuration} seconds!</span>
            </div>
            <p className="text-slate-200">
              Ollama generated valid JSON conforming to the Pydantic specification.
            </p>
            {testResultPreview && (
              <div className="bg-[#090D18] p-3 rounded-lg border border-[#26344A] text-slate-300 font-mono text-[11px] max-h-48 overflow-y-auto">
                <div className="font-semibold text-white mb-1">
                  Project: {testResultPreview.project_title || testResultPreview.title || 'Diagnostic Project'}
                </div>
                <div>{testResultPreview.problem_statement || testResultPreview.proposed_solution}</div>
              </div>
            )}
          </div>
        )}

        {testSuccess === false && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 space-y-1">
            <div className="flex items-center space-x-2 font-bold">
              <AlertCircle className="w-4 h-4" />
              <span>Diagnostic Test Failed ({testDuration}s)</span>
            </div>
            <p>{testError}</p>
          </div>
        )}
      </div>
    </div>
  );
};
