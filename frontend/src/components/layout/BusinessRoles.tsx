import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AgentResponse } from "@/lib/clientNeedApi";

interface BusinessRolesProps {
  clientNeedId?: string | null;
  agentRuns: AgentResponse[];
}

export default function BusinessRoles({ clientNeedId, agentRuns }: BusinessRolesProps) {
  const selectedRun = agentRuns.find((run) => run.client_need_id === clientNeedId) ?? agentRuns[0];
  const completeness = selectedRun?.completeness_score ?? 0;
  const missingFields = selectedRun?.missing_fields ?? [];
  const criticalMissing = selectedRun?.critical_missing_fields ?? [];

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

      {selectedRun && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-border bg-card p-6 space-y-3 lg:col-span-2">
              <div className="flex items-center gap-3">
                <h4 className="text-xl font-semibold">
                  Client Need {selectedRun.client_need_id ? `#${selectedRun.client_need_id.slice(0, 8)}` : ""}
                </h4>
                <Badge variant="secondary">Agent Summary</Badge>
              </div>
              <p className="text-sm text-muted-foreground whitespace-pre-line">{selectedRun.output}</p>
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
        </>
      )}
    </section>
  );
}
