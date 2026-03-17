const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export interface Inspiration {
  id: string;
  url: string;
  title: string;
  content_markdown: string;
  note: string;
  category: string;
  source_type: string;
  captured_at: string;
  created_at: string;
}

export interface Insight {
  id: string;
  source_type: string;
  insight_text: string;
  tags: string[];
  relevance_score: number;
  suggested_angles: string[];
  week_number: number;
}

export interface WeeklyDigest {
  id: string;
  week_number: number;
  year: number;
  summary: string;
  total_sources: number;
  total_insights: number;
  insights: Insight[];
}

export interface ContentHook {
  id: string;
  hook_text: string;
  rank: number;
  is_selected: boolean;
}

export interface ContentPiece {
  id: string;
  channel: string;
  category: string;
  body: string;
  selected_hook: string;
  status: string;
  suggested_post_time: string;
  week_number: number;
  published_url: string;
  created_at: string;
  hooks: ContentHook[];
}

export const api = {
  getInspirations: (category?: string) =>
    fetchApi<Inspiration[]>(
      `/api/inspirations${category ? `?category=${category}` : ""}`
    ),

  getInsights: (week?: number, minRelevance?: number) =>
    fetchApi<Insight[]>(
      `/api/insights?${week ? `week=${week}&` : ""}${minRelevance ? `min_relevance=${minRelevance}` : ""}`
    ),

  getDigests: () => fetchApi<WeeklyDigest[]>("/api/insights/digests"),

  getContent: (channel?: string, status?: string) => {
    const params = new URLSearchParams();
    if (channel) params.set("channel", channel);
    if (status) params.set("status", status);
    const qs = params.toString();
    return fetchApi<ContentPiece[]>(`/api/content${qs ? `?${qs}` : ""}`);
  },

  getContentById: (id: string) => fetchApi<ContentPiece>(`/api/content/${id}`),

  updateContent: (id: string, data: { body?: string; selected_hook?: string; status?: string }) =>
    fetchApi<ContentPiece>(`/api/content/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  selectHook: (contentId: string, hookId: string) =>
    fetchApi<{ status: string }>(`/api/content/${contentId}/hooks/${hookId}/select`, {
      method: "POST",
    }),

  triggerInsightExtraction: () =>
    fetchApi<{ status: string; total_insights: number }>("/api/jobs/extract-insights", {
      method: "POST",
    }),

  triggerContentGeneration: () =>
    fetchApi<{ status: string; pieces_generated: number }>("/api/jobs/generate-content", {
      method: "POST",
    }),
};
