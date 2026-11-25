/**
 * API Service for interacting with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('auth_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const isAiEndpoint = endpoint.includes('/api/project/') || endpoint.includes('/api/ai/') || endpoint.includes('/api/health');
  
  if (isAiEndpoint) {
    console.log(`[LLM-CLIENT] >>> Outgoing request: ${endpoint}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    if (isAiEndpoint) {
      console.error(`[LLM-CLIENT] ❌ LLM NOT WORKING | ${endpoint} returned HTTP ${response.status}:`, data);
    }
    let errorDetail = 'API request failed';
    if (typeof data === 'object' && data !== null) {
      if (typeof data.detail === 'string') {
        errorDetail = data.detail;
      } else if (typeof data.detail === 'object' && data.detail !== null) {
        if (data.detail.message) {
          errorDetail = String(data.detail.message);
        } else if (Array.isArray(data.detail)) {
          errorDetail = data.detail
            .map((item: any) => {
              if (typeof item === 'string') return item;
              const field = item.loc ? item.loc[item.loc.length - 1] : '';
              return field ? `${field}: ${item.msg || 'invalid'}` : (item.msg || JSON.stringify(item));
            })
            .join('; ');
        } else {
          errorDetail = JSON.stringify(data.detail);
        }
      } else if (typeof data.message === 'string') {
        errorDetail = data.message;
      } else {
        errorDetail = JSON.stringify(data);
      }
    } else if (typeof data === 'string' && data.trim()) {
      errorDetail = data;
    }
    throw new ApiError(errorDetail, response.status, data);
  }

  if (isAiEndpoint) {
    console.log(`[LLM-CLIENT] ✅ LLM IS WORKING | ${endpoint} responded successfully:`, data);
  }

  return data as T;
}

export const api = {
  // System Health
  getHealth: () => request<{
    status: string;
    timestamp: string;
    version: string;
    ai_configured: boolean;
    ai_provider?: string;
    ai_model?: string;
    anthropic_configured?: boolean;
    ollama_reachable?: boolean;
    ollama_model_available?: boolean;
    ollama_gpu_info?: any;
  }>('/api/health'),

  // Project Guidance
  analyzeProject: (data: any) => request<any>('/api/project/analyze', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getTechStack: (data: any) => request<any>('/api/project/tech-stack', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getArchitecture: (data: any) => request<any>('/api/project/architecture', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getRoadmap: (data: any) => request<any>('/api/project/roadmap', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getCodingPrompts: (data: any) => request<any>('/api/project/coding-prompts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getDocumentation: (data: any) => request<any>('/api/project/documentation', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getFullBlueprint: (data: any) => request<any>('/api/project/full-blueprint', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Projects & Task Persistence (Local Single-User Workspace)
  listProjects: async () => {
    const res = await request<any>('/api/projects');
    if (res && Array.isArray(res.projects)) {
      return res.projects;
    }
    return Array.isArray(res) ? res : [];
  },

  createProject: (data: any) =>
    request<any>('/api/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getProject: (id: string) =>
    request<any>(`/api/projects/${id}`),

  updateProject: (id: string, data: any) =>
    request<any>(`/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteProject: (id: string) =>
    request<{ success: boolean; message: string }>(`/api/projects/${id}`, {
      method: 'DELETE',
    }),

  addTask: (projectId: string, data: { title: string; category?: string }) =>
    request<any>(`/api/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTaskStatus: (projectId: string, taskId: string, status: 'pending' | 'in_progress' | 'completed') =>
    request<any>(`/api/projects/${projectId}/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  deleteTask: (projectId: string, taskId: string) =>
    request<{ success: boolean; message: string }>(`/api/projects/${projectId}/tasks/${taskId}`, {
      method: 'DELETE',
    }),

  // Automated Presentation & Report Generators
  generatePptxBlob: async (payload: any): Promise<Blob> => {
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const url = `${API_BASE_URL}/api/presentation/generate-pptx`;
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const errText = await response.text();
      throw new ApiError(errText || 'Failed to generate PowerPoint', response.status, errText);
    }
    return await response.blob();
  },

  generateReportText: async (payload: any): Promise<string> => {
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const url = `${API_BASE_URL}/api/presentation/generate-report`;
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const errText = await response.text();
      throw new ApiError(errText || 'Failed to generate IEEE Report', response.status, errText);
    }
    return await response.text();
  },

  // GitHub Scaffolding & Status
  getGithubScaffold: (data: any) =>
    request<any>('/api/github/scaffold', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getGithubStatus: () =>
    request<{ configured: boolean; user_profile?: any; message: string }>('/api/github/status'),

  // Coding Assistance
  generateCode: (data: { project_title: string; language: string; framework?: string; component_name: string; specifications: string }) =>
    request<any>('/api/coding/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  debugCode: (data: { error_message: string; language: string; code_snippet: string; context?: string }) =>
    request<any>('/api/coding/debug', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
