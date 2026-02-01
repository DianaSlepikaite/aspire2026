import { useMutation, useQueryClient } from "@tanstack/react-query";
import { processIntake, uploadIntakeFile, uploadIntakeText } from "@/lib/clientNeedApi";

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
