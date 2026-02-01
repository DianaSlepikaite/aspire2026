import { Eye, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface RoleMatch {
  role: string;
  type: string;
  candidateName: string | null;
  candidateImage: string | null;
  matchScore: number | null;
  aiInsight: string;
  availability: "available" | "limited" | "unavailable";
}

interface StaffingProjectCardProps {
  projectId: string;
  title: string;
  image: string;
  timeline: string;
  manager: string;
  matchHealth: number;
  priority?: "high" | "internal" | "standard";
  roles: RoleMatch[];
}

export function StaffingProjectCard({
  projectId,
  title,
  image,
  timeline,
  manager,
  matchHealth,
  priority = "standard",
  roles,
}: StaffingProjectCardProps) {
  const healthColor = matchHealth >= 80 ? "text-success" : matchHealth >= 60 ? "text-warning" : "text-destructive";
  const healthLabel = matchHealth >= 80 ? "Optimal" : matchHealth >= 60 ? "Needs Attention" : "Critical";

  return (
    <div className="rounded-xl bg-card border border-border overflow-hidden shadow-sm">
      {/* Project Header */}
      <div className="p-6 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div
            className="size-16 rounded-lg bg-cover bg-center shrink-0 border border-border"
            style={{ backgroundImage: `url('${image}')` }}
          />
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={cn(
                "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                priority === "high" ? "bg-primary/10 text-primary" : "bg-secondary text-muted-foreground"
              )}>
                {priority === "high" ? "High Priority" : priority === "internal" ? "Internal Project" : "Standard"}
              </span>
              <span className="text-xs text-muted-foreground font-medium">Project ID: {projectId}</span>
            </div>
            <h3 className="text-xl font-bold">{title}</h3>
            <p className="text-sm text-muted-foreground">
              Timeline: {timeline} • Manager: <span className="text-foreground font-semibold">{manager}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 self-end md:self-center">
          <div className="text-right mr-2 hidden sm:block">
            <p className="text-xs text-muted-foreground uppercase font-bold">Total Match Health</p>
            <p className={cn("text-lg font-black", healthColor)}>
              {matchHealth}% {healthLabel}
            </p>
          </div>
          <Button 
            variant={matchHealth >= 80 ? "default" : "secondary"} 
            className={cn(matchHealth >= 80 ? "" : "cursor-not-allowed opacity-60")}
          >
            {matchHealth >= 80 ? "Confirm All" : "Review Gaps"}
          </Button>
        </div>
      </div>

      {/* Roles List */}
      <div className="divide-y divide-border">
        {roles.map((role, idx) => (
          <RoleEntry key={idx} {...role} />
        ))}
      </div>
    </div>
  );
}

function RoleEntry({
  role,
  type,
  candidateName,
  candidateImage,
  matchScore,
  aiInsight,
  availability,
}: RoleMatch) {
  const hasCandidate = candidateName && candidateImage && matchScore;

  return (
    <div className="p-6 flex flex-col lg:flex-row lg:items-center gap-6 group hover:bg-secondary/50 transition-colors">
      <div className="lg:w-1/4">
        <h4 className="font-bold">{role}</h4>
        <p className="text-xs text-muted-foreground">{type}</p>
      </div>

      <div className="lg:flex-1 flex items-center gap-4">
        {hasCandidate ? (
          <>
            <div className="size-12 rounded-full bg-secondary overflow-hidden ring-2 ring-primary/20">
              <img src={candidateImage} alt={candidateName} className="w-full h-full object-cover" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <p className="font-bold text-sm">{candidateName}</p>
                <span className={cn(
                  "size-2 rounded-full",
                  availability === "available" ? "bg-success" : availability === "limited" ? "bg-warning" : "bg-destructive"
                )} />
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-primary text-sm">💡</span>
                <p className="text-xs text-muted-foreground italic">"{aiInsight}"</p>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="size-12 rounded-full bg-secondary flex items-center justify-center border-2 border-dashed border-muted-foreground/40">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="size-5 text-muted-foreground">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="font-bold text-sm text-muted-foreground italic">No ideal match found</p>
              <div className="flex items-center gap-2 mt-1">
                <AlertTriangle className="size-3.5 text-muted-foreground" />
                <p className="text-xs text-muted-foreground italic">"{aiInsight}"</p>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="flex items-center justify-between lg:justify-end gap-6">
        {hasCandidate ? (
          <div className="flex flex-col items-center">
            <div className="size-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-black text-sm shadow-lg shadow-primary/30 ring-4 ring-primary/10">
              {matchScore}%
            </div>
            <span className="text-[10px] font-bold text-primary mt-1 uppercase tracking-tighter">Match</span>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="size-12 rounded-full bg-secondary flex items-center justify-center text-muted-foreground font-black text-sm ring-4 ring-border">
              --
            </div>
          </div>
        )}
        <div className="flex gap-2">
          {hasCandidate && (
            <Button variant="outline" size="icon" className="size-9">
              <Eye className="size-4" />
            </Button>
          )}
          <Button variant={hasCandidate ? "secondary" : "default"} size="sm" className="h-9 px-4 text-xs font-bold">
            {hasCandidate ? "Staff Role" : "Expand Search"}
          </Button>
        </div>
      </div>
    </div>
  );
}
