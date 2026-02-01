import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ConversationStatus,
  UrgencyLevel,
  getClientNeed,
  listClientNeeds,
  processIntake,
  uploadIntakeFile,
  uploadIntakeText,
} from "@/lib/clientNeedApi";

export function useClientNeedsList(params: {
  status?: ConversationStatus;
  urgency?: UrgencyLevel;
  min_completeness?: number;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["client-needs", params],
    queryFn: () => listClientNeeds(params),
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchOnMount: "always",
    placeholderData: keepPreviousData,
  });
}

export function useClientNeed(clientNeedId?: string | null) {
  return useQuery({
    queryKey: ["client-need", clientNeedId],
    queryFn: () => getClientNeed(clientNeedId ?? ""),
    enabled: Boolean(clientNeedId),
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchOnMount: "always",
  });
}

export function useUploadIntakeText() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadIntakeText,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-needs"] });
    },
  });
}

export function useUploadIntakeFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadIntakeFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-needs"] });
    },
  });
}

export function useProcessIntake() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ intakeId, userQuery }: { intakeId: string; userQuery?: string }) =>
      processIntake(intakeId, userQuery),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-needs"] });
    },
  });
}
