export interface EmployeeProfile {
  id: string;
  document_id?: string | null;
  full_name?: string | null;
  email?: string | null;
  phone?: string | null;
  summary?: string | null;
  experience_years?: number | null;
  skills?: string[] | null;
  certifications?: string[] | null;
  education?: Array<Record<string, unknown>> | null;
  experience?: Array<Record<string, unknown>> | null;
  preferred_roles?: string[] | null;
  profile_completeness_score?: number | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeDocument {
  id: string;
  file_name?: string | null;
  mime_type?: string | null;
  raw_text?: string | null;
  source?: string | null;
  employee_profile_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeConversationStartResponse {
  conversation_id: string;
  employee_profile_id?: string | null;
  greeting_message: string;
  audio_url?: string | null;
}

export interface EmployeeMessageResponse {
  conversation_id: string;
  message_id: string;
  assistant_message: string;
  audio_url?: string | null;
  profile_completeness: number;
  missing_fields: string[];
  can_complete: boolean;
}

export interface EmployeeAgentUploadResponse {
  output: string;
  intermediate_steps: Array<{
    step: string;
    action?: string;
    details?: Record<string, unknown>;
  }>;
  employee_profile_id?: string;
  document_id?: string;
  completeness_score?: number;
}

const EMPLOYEE_API_BASE =
  (import.meta as ImportMeta).env?.VITE_EMPLOYEE_API_URL ?? "http://localhost:8001";

function buildUrl(path: string, params?: Record<string, string | number | undefined | null>) {
  const url = new URL(path, EMPLOYEE_API_BASE);
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

export async function startEmployeeConversation(params: {
  employee_name?: string;
  employee_email?: string;
  employee_phone?: string;
  source_channel?: string;
  initial_context?: Record<string, unknown>;
}) {
  const url = buildUrl("/api/v1/conversation/start");
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handleResponse<EmployeeConversationStartResponse>(response);
}

export async function sendEmployeeMessage(
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
  return handleResponse<EmployeeMessageResponse>(response);
}

export async function getEmployeeProfile(profileId: string) {
  const url = buildUrl(`/api/v1/employee-profiles/${profileId}`);
  const response = await fetch(url);
  return handleResponse<EmployeeProfile>(response);
}

export async function updateEmployeeProfile(profileId: string, payload: Partial<EmployeeProfile>) {
  const url = buildUrl(`/api/v1/employee-profiles/${profileId}`);
  const response = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<EmployeeProfile>(response);
}

export async function listEmployeeDocuments(params?: {
  employee_profile_id?: string;
  limit?: number;
  offset?: number;
}) {
  const url = buildUrl("/api/v1/employee-documents", params);
  const response = await fetch(url);
  return handleResponse<EmployeeDocument[]>(response);
}

export async function deleteEmployeeDocument(documentId: string) {
  const url = buildUrl(`/api/v1/employee-documents/${documentId}`);
  const response = await fetch(url, { method: "DELETE" });
  return handleResponse<{ deleted: boolean }>(response);
}

export async function processEmployeeUpload(params: {
  file: File;
  employeeProfileId?: string | null;
  conversationId?: string | null;
}) {
  const url = buildUrl("/api/v1/agent/process-upload");
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.employeeProfileId) {
    formData.append("employee_profile_id", params.employeeProfileId);
  }
  if (params.conversationId) {
    formData.append("conversation_id", params.conversationId);
  }
  const response = await fetch(url, { method: "POST", body: formData });
  return handleResponse<EmployeeAgentUploadResponse>(response);
}
