export type UrgencyLevel = "low" | "medium" | "high" | "critical";
export type ConversationStatus = "in_progress" | "completed" | "abandoned";

export interface ClientNeed {
  id: string;
  client_name?: string | null;
  client_company?: string | null;
  project_title?: string | null;
  project_description?: string | null;
  required_skills?: string[] | null;
  urgency_level?: UrgencyLevel | null;
  profile_completeness_score?: number | null;
  missing_information?: string[] | null;
  conversation_status: ConversationStatus;
  created_at: string;
  needs_summary?: string | null;
}

export interface ClientNeedListResponse {
  items: ClientNeed[];
  total: number;
  limit: number;
  offset: number;
}

export interface IntakePackage {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  source_type: string;
  client_need_id?: string | null;
}

export interface AgentResponse {
  output: string;
  intermediate_steps: Array<{
    step: string;
    action?: string;
    details?: Record<string, unknown>;
  }>;
  client_need_id?: string;
  completeness_score?: number;
  missing_fields?: string[];
  critical_missing_fields?: string[];
  clarifying_questions?: string;
}

export interface ConversationStartResponse {
  conversation_id: string;
  client_need_id: string;
  greeting_message: string;
  audio_url?: string | null;
}

export interface MessageResponse {
  conversation_id: string;
  message_id: string;
  assistant_message: string;
  audio_url?: string | null;
  extraction_updates?: Array<{
    field_name: string;
    field_value: unknown;
    confidence: number;
  }> | null;
  profile_completeness: number;
  missing_fields: string[];
  can_complete: boolean;
}

export interface ConversationCompleteResponse {
  conversation_id: string;
  client_need_id: string;
  status: "in_progress" | "completed" | "abandoned";
  profile_completeness: number;
  summary: string;
}

const API_BASE = (import.meta as ImportMeta).env?.VITE_CLIENT_NEED_API_URL ?? "http://localhost:8000";

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, API_BASE);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let details: unknown = null;
    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }
    throw new Error(typeof details === "string" ? details : JSON.stringify(details));
  }
  return response.json() as Promise<T>;
}

export async function uploadIntakeText(params: {
  text_content: string;
  client_name?: string;
  client_email?: string;
  source_label?: string;
  tags?: string;
}) {
  const url = buildUrl("/api/v1/intake/upload/text");
  const formData = new FormData();
  formData.append("text_content", params.text_content);
  if (params.client_name) formData.append("client_name", params.client_name);
  if (params.client_email) formData.append("client_email", params.client_email);
  if (params.source_label) formData.append("source_label", params.source_label);
  if (params.tags) formData.append("tags", params.tags);
  const response = await fetch(url, { method: "POST", body: formData });
  return handleResponse<IntakePackage>(response);
}

export async function uploadIntakeFile(params: {
  file: File;
  client_name?: string;
  client_email?: string;
  tags?: string;
}) {
  const file = params.file;
  const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  const isAudio = [
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a",
  ].includes(file.type) || /\.(wav|mp3|ogg|m4a)$/i.test(file.name);

  const endpoint = isPdf ? "/api/v1/intake/upload/pdf" : isAudio ? "/api/v1/intake/upload/audio" : null;
  if (!endpoint) {
    throw new Error("Unsupported file type. Please upload a PDF or audio file.");
  }

  const url = buildUrl(endpoint);
  const formData = new FormData();
  formData.append("file", file);
  if (params.client_name) formData.append("client_name", params.client_name);
  if (params.client_email) formData.append("client_email", params.client_email);
  if (params.tags) formData.append("tags", params.tags);
  const response = await fetch(url, { method: "POST", body: formData });
  return handleResponse<IntakePackage>(response);
}

export async function processIntake(intakeId: string, userQuery?: string) {
  const url = buildUrl("/api/v1/agent/process-intake");
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ intake_id: intakeId, user_query: userQuery }),
  });
  return handleResponse<AgentResponse>(response);
}

export async function startConversation(params: {
  client_name?: string;
  client_email?: string;
  client_phone?: string;
  source_channel?: string;
  initial_context?: Record<string, unknown>;
}) {
  const url = buildUrl("/api/v1/conversation/start");
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handleResponse<ConversationStartResponse>(response);
}

export async function sendConversationMessage(
  conversationId: string,
  params: { message: string; message_type?: "text" | "speech" }
) {
  const url = buildUrl(`/api/v1/conversation/${conversationId}/message`);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: params.message,
      message_type: params.message_type ?? "text",
    }),
  });
  return handleResponse<MessageResponse>(response);
}

export async function completeConversation(conversationId: string) {
  const url = buildUrl(`/api/v1/conversation/${conversationId}/complete`);
  const response = await fetch(url, { method: "POST" });
  return handleResponse<ConversationCompleteResponse>(response);
}

export async function getClarifyingQuestions(params: {
  client_need_id: string;
  context?: string;
}) {
  const url = buildUrl("/api/v1/agent/clarifying-questions");
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handleResponse<{ client_need_id: string; questions: string }>(response);
}

export async function updateClientNeedFromMessage(params: {
  client_need_id: string;
  message: string;
}) {
  const url = buildUrl(`/api/v1/client-needs/${params.client_need_id}/message`);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: params.message }),
  });
  return handleResponse<{
    client_need: ClientNeed;
    profile_completeness: number;
    missing_fields: string[];
    critical_missing_fields: string[];
  }>(response);
}

export async function listClientNeeds(params: {
  status?: ConversationStatus;
  urgency?: UrgencyLevel;
  min_completeness?: number;
  limit?: number;
  offset?: number;
}) {
  const url = buildUrl("/api/v1/client-needs", params);
  const response = await fetch(url);
  return handleResponse<ClientNeedListResponse>(response);
}

export async function getClientNeed(id: string) {
  const url = buildUrl(`/api/v1/client-needs/${id}`);
  const response = await fetch(url);
  return handleResponse<ClientNeed>(response);
}

export function extractClientNeedId(steps: AgentResponse["intermediate_steps"]) {
  const saved = steps.find((step) => step.step === "save_client_need");
  const id = saved?.details?.client_need_id;
  return typeof id === "string" ? id : null;
}

export function extractCompletenessScore(steps: AgentResponse["intermediate_steps"]) {
  const saved = steps.find((step) => step.step === "save_client_need");
  const extract = steps.find((step) => step.step === "extract_needs");
  const score = (saved?.details?.completeness_score ?? extract?.details?.completeness_score) as
    | number
    | undefined;
  return typeof score === "number" ? score : null;
}
