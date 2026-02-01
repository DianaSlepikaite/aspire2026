import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Calendar, ChevronDown, Filter, PlusCircle, Zap } from "lucide-react";
import { AgentResponse } from "@/lib/clientNeedApi";

const filterChips = [
  { label: "All Departments", active: true, hasDropdown: true },
  { label: "Urgent Only", active: false, icon: AlertTriangle },
  { label: "Match > 85%", active: false, hasDropdown: true },
  { label: "Q3-Q4 Availability", active: false, icon: Calendar },
];

interface BusinessStaffingProps {
  selectedClientNeedId?: string | null;
  onSelectNeed?: (id: string) => void;
  onViewRoles?: () => void;
  agentRuns: AgentResponse[];
}

export default function BusinessStaffing({
  selectedClientNeedId,
  onSelectNeed,
  onViewRoles,
  agentRuns,
}: BusinessStaffingProps) {
  const items = agentRuns;

  return (
    <section className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex flex-col gap-1">
          <h3 className="text-2xl font-bold leading-tight tracking-tight">Match Orchestration</h3>
          <p className="text-muted-foreground text-sm">12 Active Projects, 48 Optimal Matches Found</p>
        </div>
        <div className="flex gap-3">
          <Button className="font-bold">
            <PlusCircle className="size-4 mr-2" />
            New Project Request
          </Button>
          <Button variant="outline" className="font-bold">
            <Filter className="size-4 mr-2" />
            Advanced Filters
          </Button>
        </div>
      </div>

      <div className="flex gap-3 flex-wrap">
        {filterChips.map((chip, idx) => (
          <button
            key={idx}
            className={`flex h-9 items-center justify-center gap-2 rounded-full px-4 text-sm font-medium transition-colors ${
              chip.active
                ? "bg-primary/10 border border-primary/30 text-primary font-semibold"
                : "bg-card border border-border text-muted-foreground hover:bg-secondary"
            }`}
          >
            {chip.icon && <chip.icon className="size-4 text-primary" />}
            <span>{chip.label}</span>
            {chip.hasDropdown && <ChevronDown className="size-4" />}
          </button>
        ))}
      </div>

      <div className="space-y-6">
        <h4 className="text-lg font-bold tracking-tight flex items-center gap-2">
          <Zap className="size-5 text-primary" />
          Client Needs Intake
        </h4>

        {items.length === 0 && (
          <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No client needs processed yet. Send a brief to the agent to get started.
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {items.map((need) => {
            const id = need.client_need_id || "";
            const isSelected = id === selectedClientNeedId;
            const completeness = need.completeness_score ?? 0;
            return (
              <button
                key={id || need.output}
                type="button"
                onClick={() => id && onSelectNeed?.(id)}
                className={`text-left rounded-2xl border p-5 transition-colors ${
                  isSelected ? "border-primary bg-primary/5" : "border-border bg-card hover:bg-secondary/30"
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <h5 className="text-lg font-semibold">
                        Client Need #{id ? id.slice(0, 8) : "Pending"}
                      </h5>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {need.output.slice(0, 120)}{need.output.length > 120 ? "..." : ""}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {(need.missing_fields || []).slice(0, 3).map((field) => (
                        <Badge key={field} variant="outline">
                          {field}
                        </Badge>
                      ))}
                      {need.missing_fields && need.missing_fields.length > 3 && (
                        <Badge variant="outline">+{need.missing_fields.length - 3} missing</Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-wide">Completeness</p>
                      <p className="text-lg font-semibold text-foreground">{completeness}%</p>
                    </div>
                    <Button
                      variant={isSelected ? "default" : "outline"}
                      className="font-semibold"
                      onClick={(event) => {
                        event.stopPropagation();
                        if (id) {
                          onSelectNeed?.(id);
                        }
                        onViewRoles?.();
                      }}
                    >
                      View Roles
                    </Button>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-6 flex flex-col items-center gap-3">
        <Button variant="outline" size="lg" className="font-bold">
          <ChevronDown className="size-4 mr-2" />
          Load More Projects
        </Button>
        <p className="text-sm text-muted-foreground">Showing 2 of 12 projects</p>
      </div>
    </section>
  );
}
