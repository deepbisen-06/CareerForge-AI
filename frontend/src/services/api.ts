import {
  AuthResponse,
  Profile,
  ResumeAnalysis,
  ResumeVersion,
  Internship,
  SavedJob,
  MatchExplanation,
  SkillGapReport,
  GeneratedDocument,
  InterviewSession,
  InterviewQuestion,
  PrepPlan,
  InterviewProgress,
  Application,
  ChatMessage,
  NotificationItem,
  DashboardOverview,
  AdminStats,
  AgentRun,
  AgentEvent
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token');
  const headers = new Headers(options.headers || {});
  
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorMsg = 'An error occurred';
    try {
      const err = await response.json();
      errorMsg = err.detail || err.message || errorMsg;
    } catch {
      // keep fallback
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // Auth
  auth: {
    register: (data: { email: string; password: string; full_name?: string; role?: string }) =>
      request<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
      request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    me: () => request<any>('/auth/me')
  },

  // Profile
  profile: {
    get: () => request<Profile>('/profile/'),
    update: (data: Partial<Profile>) =>
      request<Profile>('/profile/', { method: 'PUT', body: JSON.stringify(data) })
  },

  // Resume & Versions
  resume: {
    upload: (formData: FormData) =>
      request<ResumeAnalysis>('/resume/upload', { method: 'POST', body: formData }),
    getLatest: () => request<ResumeAnalysis>('/resume/latest'),
    getVersions: () => request<ResumeVersion[]>('/resume/versions'),
    saveVersion: (data: { target_internship_id?: number; title: string; document_type: string; content_markdown: string; metadata_json?: Record<string, any> }) =>
      request<ResumeVersion>('/resume/versions', { method: 'POST', body: JSON.stringify(data) }),
    deleteVersion: (versionId: number) =>
      request<{ status: string; message: string }>(`/resume/versions/${versionId}`, { method: 'DELETE' })
  },

  // Internships & Saved Jobs
  internships: {
    list: (params?: { q?: string; domain?: string; location?: string; work_mode?: string; source_type?: string; limit?: number }) => {
      const query = new URLSearchParams();
      if (params?.q) query.set('q', params.q);
      if (params?.domain && params.domain !== 'All') query.set('domain', params.domain);
      if (params?.location && params.location !== 'All') query.set('location', params.location);
      if (params?.work_mode && params.work_mode !== 'All') query.set('work_mode', params.work_mode);
      if (params?.source_type && params.source_type !== 'All') query.set('source_type', params.source_type);
      if (params?.limit) query.set('limit', params.limit.toString());
      return request<Internship[]>(`/internships/?${query.toString()}`);
    },
    get: (id: number) => request<Internship>(`/internships/${id}`),
    getSaved: () => request<SavedJob[]>('/internships/saved'),
    save: (id: number) => request<{ status: string; saved: boolean; message: string }>(`/internships/${id}/save`, { method: 'POST' }),
    unsave: (id: number) => request<{ status: string; saved: boolean; message: string }>(`/internships/${id}/save`, { method: 'DELETE' })
  },

  // Matching & Feedback
  matching: {
    getExplanation: (internshipId: number) =>
      request<MatchExplanation>(`/matching/${internshipId}`),
    submitFeedback: (data: { internship_id: number; is_positive: boolean; reason_category?: string; notes?: string }) =>
      request<{ status: string; message: string }>('/matching/feedback', { method: 'POST', body: JSON.stringify(data) })
  },

  // Skill Gaps
  skillGaps: {
    analyze: (internshipId: number) =>
      request<SkillGapReport>(`/skill-gaps/analyze/${internshipId}`),
    userSummary: () => request<any>('/skill-gaps/user-summary')
  },

  // Documents
  documents: {
    generate: (data: { internship_id: number; document_type: string; tone?: string; additional_notes?: string }) =>
      request<GeneratedDocument>('/documents/generate', { method: 'POST', body: JSON.stringify(data) }),
    list: () => request<GeneratedDocument[]>('/documents/list')
  },

  // Interview
  interview: {
    generateQuestions: (data: { internship_id: number; categories?: string[]; count?: number }) =>
      request<InterviewSession>('/interview/generate-questions', { method: 'POST', body: JSON.stringify(data) }),
    getPrepPlan: (internshipId: number) =>
      request<PrepPlan>(`/interview/prep-plan/${internshipId}`),
    submitAnswer: (data: { question_id: number; user_answer: string }) =>
      request<InterviewQuestion>('/interview/submit-answer', { method: 'POST', body: JSON.stringify(data) }),
    getSession: (id: number) => request<InterviewSession>(`/interview/session/${id}`),
    getProgress: () => request<InterviewProgress>('/interview/progress')
  },

  // Applications
  applications: {
    list: () => request<Application[]>('/applications/'),
    create: (data: { internship_id: number; status?: string; deadline?: string; notes?: string }) =>
      request<Application>('/applications/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: { status?: string; deadline?: string; notes?: string }) =>
      request<Application>(`/applications/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: number) =>
      request<{ success: boolean; message: string }>(`/applications/${id}`, { method: 'DELETE' })
  },

  // Chat
  chat: {
    sendMessage: (data: { message: string; session_id?: number }) =>
      request<ChatMessage>('/chat/message', { method: 'POST', body: JSON.stringify(data) }),
    getHistory: () => request<any>('/chat/history')
  },

  // Notifications
  notifications: {
    list: () => request<NotificationItem[]>('/notifications/'),
    markRead: (id: number) =>
      request<NotificationItem>(`/notifications/${id}/read`, { method: 'PUT' }),
    markAllRead: () =>
      request<{ status: string }>('/notifications/mark-all-read', { method: 'PUT' })
  },

  // Dashboard
  dashboard: {
    getOverview: () => request<DashboardOverview>('/dashboard/overview')
  },

  // Admin Portal
  admin: {
    getStats: () => request<AdminStats>('/admin/stats'),
    listInternships: (params?: { skip?: number; limit?: number; domain?: string }) => {
      const query = new URLSearchParams();
      if (params?.skip) query.set('skip', params.skip.toString());
      if (params?.limit) query.set('limit', params.limit.toString());
      if (params?.domain) query.set('domain', params.domain);
      return request<Internship[]>(`/admin/internships?${query.toString()}`);
    },
    createInternship: (data: any) =>
      request<Internship>('/admin/internships', { method: 'POST', body: JSON.stringify(data) }),
    updateInternship: (id: number, data: any) =>
      request<Internship>(`/admin/internships/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    deleteInternship: (id: number) =>
      request<{ status: string; message: string }>(`/admin/internships/${id}`, { method: 'DELETE' }),
    triggerIngestion: (data: { source_name?: string; refresh_vectors?: boolean; limit?: number }) =>
      request<any>('/admin/ingest', { method: 'POST', body: JSON.stringify(data) }),
    reindexRAG: () =>
      request<{ status: string; indexed_documents: number }>('/admin/rag/reindex', { method: 'POST' })
  },

  // CareerForge Autonomous Agent
  agent: {
    createRun: (goal: string) =>
      request<AgentRun>('/agent/runs', { method: 'POST', body: JSON.stringify({ goal }) }),
    listRuns: (limit: number = 20) =>
      request<AgentRun[]>(`/agent/runs?limit=${limit}`),
    getRun: (runId: number) =>
      request<AgentRun>(`/agent/runs/${runId}`),
    getEvents: (runId: number) =>
      request<AgentEvent[]>(`/agent/runs/${runId}/events`),
    approveRun: (runId: number, notes?: string) =>
      request<AgentRun>(`/agent/runs/${runId}/approve`, { method: 'POST', body: JSON.stringify({ notes }) }),
    cancelRun: (runId: number) =>
      request<AgentRun>(`/agent/runs/${runId}/cancel`, { method: 'POST' })
  }
};
