import { useMemo } from "react";
import { MatchCard } from "@/components/cards/MatchCard";
import { Button } from "@/components/ui/button";
import { Check, ChevronDown, Zap } from "lucide-react";
import { useClientNeedsList } from "@/hooks/useClientNeeds";
import { useEmployeeContext } from "@/context/EmployeeContext";
import { useQueries } from "@tanstack/react-query";
import { evaluateCandidateForNeed } from "@/lib/clientNeedApi";

const filters = [
  { label: "Highest Match", active: true, icon: Check },
  { label: "Engineering", active: false, hasDropdown: true },
  { label: "Remote Only", active: false },
  { label: "Urgent Needs", active: false, icon: Zap, highlight: true },
];

export default function Matches() {
  const { employeeProfileId } = useEmployeeContext();
  const { data, isLoading, isError } = useClientNeedsList({ limit: 12, offset: 0 });
  const needs = useMemo(() => data?.items ?? [], [data?.items]);

  const matchQueries = useQueries({
    queries: needs.map((need) => ({
      queryKey: ["candidate-match", employeeProfileId, need.id],
      queryFn: async () => {
        try {
          return await evaluateCandidateForNeed({
            employee_profile_id: employeeProfileId ?? "",
            client_need_id: need.id,
          });
        } catch (error) {
          return null;
        }
      },
      enabled: Boolean(employeeProfileId && need.id),
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    })),
  });

  const matchCards = useMemo(() => {
    const images = [
      "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",
      "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=200&fit=crop",
    ];
    return needs
      .map((need, idx) => {
        const match = matchQueries[idx]?.data?.match;
        if (!match) return null;
        const duration = need.timeline_duration_weeks
          ? `${need.timeline_duration_weeks} weeks`
          : "Timeline TBD";
        const location = need.work_location
          ? need.work_location.charAt(0).toUpperCase() + need.work_location.slice(1)
          : "Flexible";
        return {
          title: need.project_title ?? `Project ${need.id.slice(0, 6)}`,
          department: need.client_company ?? "Project Team",
          matchScore: match.match_score,
          duration,
          location,
          skills: need.required_skills ?? [],
          description: need.needs_summary ?? need.project_description ?? "Project details available on request.",
          image: images[idx % images.length],
        };
      })
      .filter(Boolean) as Array<{
        title: string;
        department: string;
        matchScore: number;
        duration: string;
        location: string;
        skills: string[];
        description: string;
        image: string;
      }>;
  }, [needs, matchQueries]);

  if (!employeeProfileId) {
    return (
      <section className="space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h3 className="text-2xl font-bold tracking-tight mb-2">Your Role Matches</h3>
            <p className="text-muted-foreground">
              Complete your profile or upload a CV to unlock personalized matches.
            </p>
          </div>
        </div>
        <div className="bg-card rounded-2xl border border-border p-8 text-sm text-muted-foreground">
          No profile found yet. Start a conversation or upload your CV in the Career portal.
        </div>
      </section>
    );
  }

  return (
      <section >

        {/* Main Content */}
        <div className="flex-1 space-y-6">
          {/* Page Heading & Filters */}
          <div className="space-y-4">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h3 className="text-2xl font-bold tracking-tight mb-2">Your Role Matches</h3>
                <p className="text-muted-foreground">Discover your next career move within the ecosystem.</p>
              </div>
            </div>

            {/* Filter Chips */}
            <div className="flex flex-wrap gap-2">
              {filters.map((filter, idx) => (
                <button
                  key={idx}
                  className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${
                    filter.active
                      ? "bg-primary text-primary-foreground"
                      : filter.highlight
                      ? "bg-card border border-border text-primary hover:bg-secondary"
                      : "bg-card border border-border hover:bg-secondary"
                  }`}
                >
                  {filter.label}
                  {filter.icon && <filter.icon className="size-3.5" />}
                  {filter.hasDropdown && <ChevronDown className="size-3.5" />}
                </button>
              ))}
            </div>
          </div>

          {/* Grid Results */}
          {isLoading && (
            <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
              Loading opportunities...
            </div>
          )}
          {isError && (
            <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
              Unable to load opportunities right now.
            </div>
          )}
          {!isLoading && !isError && matchCards.length === 0 && (
            <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
              No strong matches yet. Continue refining your profile to improve match quality.
            </div>
          )}
          {!isLoading && !isError && matchCards.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-6">
              {matchCards.map((match, idx) => (
                <MatchCard key={idx} {...match} />
              ))}
            </div>
          )}
        </div>
      </section>
  );
}
