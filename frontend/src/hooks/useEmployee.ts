import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";
import {
  getEmployeeProfile,
  listEmployeeDocuments,
  updateEmployeeProfile,
  deleteEmployeeDocument,
  processEmployeeUpload,
  sendEmployeeMessage,
  startEmployeeConversation,
  type EmployeeProfile,
} from "@/lib/employeeApi";

export function useEmployeeProfile(profileId?: string | null) {
  return useQuery({
    queryKey: ["employee-profile", profileId],
    queryFn: () => getEmployeeProfile(profileId ?? ""),
    enabled: Boolean(profileId),
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchOnMount: true,
  });
}

export function useEmployeeDocuments(profileId?: string | null) {
  return useQuery({
    queryKey: ["employee-documents", profileId],
    queryFn: () => listEmployeeDocuments({ employee_profile_id: profileId ?? undefined }),
    enabled: Boolean(profileId),
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchOnMount: true,
    placeholderData: keepPreviousData,
  });
}

export function useEmployeeUpload() {
  return useMutation({
    mutationFn: processEmployeeUpload,
  });
}

export function useEmployeeProfileUpdate() {
  return useMutation({
    mutationFn: ({ profileId, payload }: { profileId: string; payload: Partial<EmployeeProfile> }) =>
      updateEmployeeProfile(profileId, payload),
  });
}

export function useEmployeeDocumentDelete() {
  return useMutation({
    mutationFn: ({ documentId }: { documentId: string }) => deleteEmployeeDocument(documentId),
  });
}

export function useEmployeeConversationStart() {
  return useMutation({
    mutationFn: startEmployeeConversation,
  });
}

export function useEmployeeMessage() {
  return useMutation({
    mutationFn: ({ conversationId, message }: { conversationId: string; message: string }) =>
      sendEmployeeMessage(conversationId, { message, message_type: "text" }),
  });
}
