export type UrgencyLevel = "low" | "medium" | "high" | "critical";

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
