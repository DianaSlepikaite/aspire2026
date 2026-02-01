import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useClientNeedsList } from "@/hooks/useClientNeeds";

interface BusinessReportsProps {
  agentRuns: Array<{
    client_need_id?: string;
    completeness_score?: number;
    missing_fields?: string[];
    critical_missing_fields?: string[];
  }>;
}

export default function BusinessReports({ agentRuns }: BusinessReportsProps) {
  const { data } = useClientNeedsList({ limit: 100, offset: 0 });
  const items = data?.items ?? [];
  const total = data?.total ?? items.length;
  const avgCompleteness =
    items.length > 0
      ? Math.round(items.reduce((acc, item) => acc + (item.profile_completeness_score ?? 0), 0) / items.length)
      : 0;
  const criticalMissingCount = items.reduce(
    (acc, item) => acc + (item.missing_information?.length ?? 0),
    0,
  );

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Business Reports</h3>
          <p className="text-muted-foreground text-sm mt-2">
            Monitor staffing health, pipeline velocity, and project utilization.
          </p>
        </div>
        <Button variant="secondary" className="font-bold">
          Export Report
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-2xl border border-border bg-card p-6 space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Client Needs</p>
          <p className="text-3xl font-bold">{total}</p>
          <p className="text-sm text-muted-foreground">Total captured briefs</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-6 space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Avg Completeness</p>
          <p className="text-3xl font-bold">{avgCompleteness}%</p>
          <p className="text-sm text-muted-foreground">Across ingested needs</p>
        </div>
        <div className="rounded-2xl border border-border bg-card p-6 space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Critical Gaps</p>
          <p className="text-3xl font-bold">{criticalMissingCount}</p>
          <p className="text-sm text-muted-foreground">Fields missing across briefs</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Completeness Range</h4>
        </div>
        <div className="flex flex-wrap gap-3">
          {items.map((need) => (
            <div key={need.id} className="rounded-xl border border-border p-4">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">
                {need.id.slice(0, 8)}
              </p>
              <p className="text-2xl font-semibold text-foreground">{need.profile_completeness_score ?? 0}%</p>
              <p className="text-xs text-muted-foreground">
                Missing {need.missing_information?.length ?? 0} fields
              </p>
            </div>
          ))}
          {items.length === 0 && (
            <p className="text-sm text-muted-foreground">No agent runs yet.</p>
          )}
        </div>
      </div>
    </section>
  );
}
