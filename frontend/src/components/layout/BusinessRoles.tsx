import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useClientNeed } from "@/hooks/useClientNeeds";
import type { AgentResponse } from "@/lib/clientNeedApi";
import { findMatchingCandidates } from "@/lib/clientNeedApi";
import { useQuery } from "@tanstack/react-query";
import { Eye, UserCircle2 } from "lucide-react";

interface BusinessRolesProps {
  clientNeedId?: string | null;
  agentRuns: AgentResponse[];
}

export default function BusinessRoles({ clientNeedId, agentRuns }: BusinessRolesProps) {
  const selectedRun = agentRuns.find((run) => run.client_need_id === clientNeedId);
  const { data: clientNeed, isLoading } = useClientNeed(clientNeedId);
  const { data: matchData, isLoading: isMatching } = useQuery({
    queryKey: ["client-need-matches", clientNeedId],
    queryFn: () =>
      findMatchingCandidates({
        client_need_id: clientNeedId ?? "",
        max_results: 6,
        min_match_score: 0,
      }),
    enabled: Boolean(clientNeedId),
  });

  // API data is source of truth; agentRuns supplements fields the backend doesn't store
  const apiCompleteness = clientNeed?.profile_completeness_score ?? clientNeed?.profile_completeness;
  const runCompleteness = selectedRun?.completeness_score;
  const completeness =
    typeof apiCompleteness === "number" && apiCompleteness > 0
      ? apiCompleteness
      : typeof runCompleteness === "number"
        ? runCompleteness
        : apiCompleteness ?? 0;
  const missingFields =
    clientNeed?.missing_information && clientNeed.missing_information.length > 0
      ? clientNeed.missing_information
      : selectedRun?.missing_fields ?? [];
  const criticalMissing = selectedRun?.critical_missing_fields ?? [];
  const clarifyingQuestions = selectedRun?.clarifying_questions;
  const summary =
    clientNeed?.needs_summary ?? clientNeed?.project_description ?? selectedRun?.output ?? "";

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Roles & Requirements</h3>
          <p className="text-muted-foreground text-sm mt-2">
            Review the agent summary and any missing details.
          </p>
        </div>
        <Button variant="secondary" className="font-bold">
          Export Summary
        </Button>
      </div>

      {!clientNeedId && (
        <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
          Select a client need from Staffing to view the agent summary.
        </div>
      )}

      {clientNeedId && !selectedRun && !clientNeed && !isLoading && (
        <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
          This client need does not have an agent summary yet. Run the agent to generate a summary.
        </div>
      )}

      {(selectedRun || clientNeed) && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-border bg-card p-6 space-y-3 lg:col-span-2">
              <div className="flex items-center gap-3">
                <h4 className="text-xl font-semibold">
                  Client Need {clientNeedId ? `#${clientNeedId.slice(0, 8)}` : ""}
                </h4>
                <Badge variant="secondary">Agent Summary</Badge>
              </div>
              <p className="text-sm text-muted-foreground whitespace-pre-line">
                {summary || "Summary not available yet."}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Completeness</p>
                <p className="text-2xl font-bold">{completeness}%</p>
              </div>
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>Missing fields: {missingFields.length}</p>
                <p>Critical missing: {criticalMissing.length}</p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Missing Fields</h4>
              <Badge variant="secondary">{missingFields.length}</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              {missingFields.length === 0 && (
                <p className="text-sm text-muted-foreground">No missing fields detected.</p>
              )}
              {missingFields.map((field) => (
                <Badge key={field} variant="outline">
                  {field}
                </Badge>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Critical Missing Fields</h4>
              <Badge variant="destructive">{criticalMissing.length}</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              {criticalMissing.length === 0 && (
                <p className="text-sm text-muted-foreground">No critical gaps reported.</p>
              )}
              {criticalMissing.map((field) => (
                <Badge key={field} variant="outline">
                  {field}
                </Badge>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Clarifying Questions</h4>
              <Badge variant="secondary">{clarifyingQuestions ? "AI" : "None"}</Badge>
            </div>
            {clarifyingQuestions ? (
              <p className="text-sm text-muted-foreground whitespace-pre-line">{clarifyingQuestions}</p>
            ) : (
              <p className="text-sm text-muted-foreground">No clarifying questions were generated yet.</p>
            )}
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Potential Matches</h4>
              <Badge variant="secondary">{matchData?.matches?.length ?? 0}</Badge>
            </div>
            {isMatching && (
              <p className="text-sm text-muted-foreground">Evaluating employee matches...</p>
            )}
            {!isMatching && (!matchData || matchData.matches.length === 0) && (
              <p className="text-sm text-muted-foreground">No matching candidates yet.</p>
            )}
            {!isMatching && matchData && matchData.matches.length > 0 && (
              <div className="space-y-3">
                {matchData.matches.map((match) => {
                  const highlight =
                    match.explanation?.strengths?.[0]
                    ?? match.explanation?.additional_notes
                    ?? "Strong alignment with project requirements.";
                  return (
                    <div
                      key={match.employee_profile_id}
                      className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 rounded-xl border border-border/80 bg-background/40 p-4"
                    >
                      <div className="flex items-center gap-4">
                        <div className="size-12 rounded-full bg-secondary flex items-center justify-center text-muted-foreground">
                          <UserCircle2 className="size-6" />
                        </div>
                        <div className="space-y-1">
                          <p className="font-semibold">{match.employee_name}</p>
                          <p className="text-xs text-muted-foreground">
                            {match.employee_email ?? "Email not provided"}
                          </p>
                          <p className="text-xs italic text-muted-foreground">"{highlight}"</p>
                          {match.key_skills?.length > 0 && (
                            <div className="flex flex-wrap gap-2 pt-2">
                              {match.key_skills.slice(0, 6).map((skill) => (
                                <Badge key={skill} variant="outline">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-center">
                          <div className="size-14 rounded-full border border-primary/40 bg-primary/10 flex items-center justify-center">
                            <span className="text-lg font-bold text-primary">{match.match_score}%</span>
                          </div>
                          <p className="text-[10px] font-semibold text-muted-foreground mt-1 uppercase">Match</p>
                        </div>
                        <Button variant="outline" size="icon">
                          <Eye className="size-4" />
                        </Button>
                        <Button className="font-semibold">Staff Role</Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
