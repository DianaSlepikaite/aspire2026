import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useClientNeeds } from "@/hooks/useClientNeeds";

export default function BusinessReports() {
  const { data, isLoading } = useClientNeeds({ limit: 100, offset: 0 });
  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const avgCompleteness =
    items.length > 0
      ? Math.round(items.reduce((acc, item) => acc + item.profile_completeness_score, 0) / items.length)
      : 0;
  const urgencyCounts = items.reduce<Record<string, number>>((acc, item) => {
    const key = item.urgency_level ?? "unknown";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const statusCounts = items.reduce<Record<string, number>>((acc, item) => {
    acc[item.conversation_status] = (acc[item.conversation_status] || 0) + 1;
    return acc;
  }, {});

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
          <p className="text-xs uppercase tracking-wide text-muted-foreground">In Progress</p>
          <p className="text-3xl font-bold">{statusCounts.in_progress || 0}</p>
          <p className="text-sm text-muted-foreground">Active conversations</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Urgency Breakdown</h4>
          {isLoading && <Badge variant="secondary">Loading</Badge>}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground">
          {["critical", "high", "medium", "low", "unknown"].map((level) => (
            <div key={level} className="rounded-xl border border-border p-4">
              <p className="uppercase text-xs tracking-wide">{level}</p>
              <p className="text-2xl font-semibold text-foreground">{urgencyCounts[level] || 0}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
