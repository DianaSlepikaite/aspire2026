import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ClientNeed,
  ClientNeedListParams,
  getClientNeed,
  listClientNeeds,
  processIntake,
  updateClientNeed,
  uploadIntakeFile,
  uploadIntakeText,
} from "@/lib/clientNeedApi";

export function useClientNeeds(params: ClientNeedListParams = {}) {
  return useQuery({
    queryKey: ["client-needs", params],
    queryFn: () => listClientNeeds(params),
  });
}

export function useClientNeed(clientNeedId?: string | null) {
  return useQuery({
    queryKey: ["client-need", clientNeedId],
    queryFn: () => getClientNeed(clientNeedId as string),
    enabled: Boolean(clientNeedId),
  });
}

export function useUpdateClientNeed(clientNeedId?: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: Partial<ClientNeed>) => updateClientNeed(clientNeedId as string, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-need", clientNeedId] });
      queryClient.invalidateQueries({ queryKey: ["client-needs"] });
    },
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
