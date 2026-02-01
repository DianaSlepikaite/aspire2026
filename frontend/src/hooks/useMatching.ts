import { useQuery, useQueries } from "@tanstack/react-query";
import {
  evaluateCandidateForNeed,
  findMatchingCandidates,
} from "@/lib/clientNeedApi";

export function useClientNeedMatches(params?: {
  clientNeedId?: string | null;
  maxResults?: number;
  minMatchScore?: number;
}) {
  return useQuery({
    queryKey: ["client-need-matches", params?.clientNeedId, params?.maxResults, params?.minMatchScore],
    queryFn: () =>
      findMatchingCandidates({
        client_need_id: params?.clientNeedId ?? "",
        max_results: params?.maxResults ?? 5,
        min_match_score: params?.minMatchScore ?? 0,
      }),
    enabled: Boolean(params?.clientNeedId),
  });
}

export function useEmployeeOpportunityMatches(params: {
  employeeProfileId?: string | null;
  clientNeedIds: string[];
}) {
  return useQueries({
    queries: params.clientNeedIds.map((clientNeedId) => ({
      queryKey: ["candidate-match", params.employeeProfileId, clientNeedId],
      queryFn: () =>
        evaluateCandidateForNeed({
          employee_profile_id: params.employeeProfileId ?? "",
          client_need_id: clientNeedId,
        }),
      enabled: Boolean(params.employeeProfileId) && Boolean(clientNeedId),
    })),
  });
}
