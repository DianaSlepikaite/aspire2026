import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, ChevronDown, PlusCircle, Zap } from "lucide-react";
import type { AgentResponse, ClientNeed } from "@/lib/clientNeedApi";
import { useClientNeedsList } from "@/hooks/useClientNeeds";
import { useQueries } from "@tanstack/react-query";
import { findMatchingCandidates } from "@/lib/clientNeedApi";

const PAGE_SIZE = 5;

type FilterKey = "status" | "urgency" | "min_completeness";

const filterChips = [
  { id: "all", label: "All Projects", key: "reset" as const },
  { id: "urgent", label: "Urgent Only", key: "urgency" as const, value: "high", icon: AlertTriangle },
  { id: "match", label: "Match > 85%", key: "min_completeness" as const, value: 85, icon: Zap },
  { id: "active", label: "Active Only", key: "status" as const, value: "in_progress", hasDropdown: true },
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
  const [filters, setFilters] = useState<{
    status?: "in_progress" | "completed" | "abandoned";
    urgency?: "low" | "medium" | "high" | "critical";
    min_completeness?: number;
  }>({});
  const [pageSize, setPageSize] = useState(PAGE_SIZE);

  const { data, isLoading, isError } = useClientNeedsList({
    status: filters.status,
    urgency: filters.urgency,
    min_completeness: filters.min_completeness,
    limit: pageSize,
    offset: 0,
  });

  const items = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;
  const runMap = new Map(agentRuns.filter((run) => run.client_need_id).map((run) => [run.client_need_id!, run]));

  const matchQueries = useQueries({
    queries: items.map((need) => ({
      queryKey: ["client-need-matches", need.id],
      queryFn: () =>
        findMatchingCandidates({
          client_need_id: need.id,
          max_results: 3,
          min_match_score: 60,
        }),
      enabled: Boolean(need.id),
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    })),
  });

  const matchByNeedId = useMemo(() => {
    const map = new Map<string, { count: number; topScore: number; loading: boolean }>();
    items.forEach((need, idx) => {
      const query = matchQueries[idx];
      const matches = query?.data?.matches ?? [];
      map.set(need.id, {
        count: matches.length,
        topScore: matches[0]?.match_score ?? 0,
        loading: query?.isLoading ?? false,
      });
    });
    return map;
  }, [items, matchQueries]);

  const handleFilterToggle = (key: FilterKey, value: string | number) => {
    setPageSize(PAGE_SIZE);
    setFilters((prev) => ({
      ...prev,
      [key]: prev[key] === value ? undefined : value,
    }));
  };

  const handleResetFilters = () => {
    setPageSize(PAGE_SIZE);
    setFilters({});
  };

  const hasFilters = Boolean(filters.status || filters.urgency || filters.min_completeness);
  const showLoadMore = total > PAGE_SIZE && total > items.length;
  const visibleCount = items.length;

  return (
    <section className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex flex-col gap-1">
          <h3 className="text-2xl font-bold leading-tight tracking-tight">Match Orchestration</h3>
          <p className="text-muted-foreground text-sm">
            {total} Projects in Pipeline, {visibleCount} Loaded
          </p>
        </div>
        <div className="flex gap-3">
          <Button className="font-bold">
            <PlusCircle className="size-4 mr-2" />
            New Project Request
          </Button>
        </div>
      </div>

      <div className="flex gap-3 flex-wrap">
        {filterChips.map((chip) => {
          const isActive =
            chip.key === "reset"
              ? !hasFilters
              : filters[chip.key as FilterKey] === chip.value;
          return (
          <button
            key={chip.id}
            type="button"
            onClick={() => {
              if (chip.key === "reset") {
                handleResetFilters();
              } else {
                handleFilterToggle(chip.key, chip.value);
              }
            }}
            className={`flex h-9 items-center justify-center gap-2 rounded-full px-4 text-sm font-medium transition-colors ${
              isActive
                ? "bg-primary/10 border border-primary/30 text-primary font-semibold"
                : "bg-card border border-border text-muted-foreground hover:bg-secondary"
            }`}
          >
            {chip.icon && <chip.icon className="size-4 text-primary" />}
            <span>{chip.label}</span>
            {chip.hasDropdown && <ChevronDown className="size-4" />}
          </button>
          );
        })}
      </div>

      <div className="space-y-6">
        <h4 className="text-lg font-bold tracking-tight flex items-center gap-2">
          <Zap className="size-5 text-primary" />
          Client Needs Intake
        </h4>

        {isLoading && (
          <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
            Loading client needs...
          </div>
        )}

        {isError && (
          <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
            Unable to load client needs right now. Please try again shortly.
          </div>
        )}

        {!isLoading && !isError && items.length === 0 && (
          <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No client needs processed yet. Send a brief to the agent to get started.
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {items.map((need: ClientNeed) => {
            const id = need.id;
            const isSelected = id === selectedClientNeedId;
            const run = runMap.get(id);
            const apiCompleteness = need.profile_completeness_score ?? need.profile_completeness;
            const runCompleteness = run?.completeness_score;
            const completeness =
              typeof apiCompleteness === "number" && apiCompleteness > 0
                ? apiCompleteness
                : typeof runCompleteness === "number"
                  ? runCompleteness
                  : apiCompleteness ?? 0;
            const missingFields =
              need.missing_information && need.missing_information.length > 0
                ? need.missing_information
                : run?.missing_fields ?? [];
            const summary = need.needs_summary ?? need.project_description ?? run?.output ?? "No summary available.";
            const matchSummary = matchByNeedId.get(id);
            const matchCount = matchSummary?.count ?? 0;
            const topScore = matchSummary?.topScore ?? 0;
            const isMatching = matchSummary?.loading ?? false;
            return (
              <button
                key={id}
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
                        {need.project_title ?? `Client Need #${id.slice(0, 8)}`}
                      </h5>
                      {isMatching ? (
                        <Badge variant="outline">Matching...</Badge>
                      ) : (
                        <Badge variant="secondary">
                          {matchCount} matches{topScore ? ` · Top ${topScore}%` : ""}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {summary.slice(0, 120)}
                      {summary.length > 120 ? "..." : ""}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {missingFields.slice(0, 3).map((field) => (
                        <Badge key={field} variant="outline">
                          {field}
                        </Badge>
                      ))}
                      {missingFields.length > 3 && (
                        <Badge variant="outline">+{missingFields.length - 3} missing</Badge>
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

      {showLoadMore && (
        <div className="mt-6 flex flex-col items-center gap-3">
          <Button
            variant="outline"
            size="lg"
            className="font-bold"
            onClick={() => setPageSize((size) => size + PAGE_SIZE)}
          >
            <ChevronDown className="size-4 mr-2" />
            Load More Projects
          </Button>
          <p className="text-sm text-muted-foreground">
            Showing {items.length} of {total} projects
          </p>
        </div>
      )}
    </section>
  );
}
