import { ChevronRight, Code, Palette, Database } from "lucide-react";
import { cn } from "@/lib/utils";

interface RoleCardProps {
  title: string;
  project: string;
  client: string;
  status: "high-priority" | "interviewing" | "pending";
  applicants: { image: string }[];
  icon?: "code" | "design" | "data";
}

const iconMap = {
  code: Code,
  design: Palette,
  data: Database,
};

const statusStyles = {
  "high-priority": "bg-primary text-primary-foreground",
  interviewing: "bg-secondary text-foreground",
  pending: "bg-secondary text-foreground",
};

const statusLabels = {
  "high-priority": "High Priority",
  interviewing: "Interviewing",
  pending: "Pending SOW",
};

export function RoleCard({
  title,
  project,
  client,
  status,
  applicants,
  icon = "code",
}: RoleCardProps) {
  const Icon = iconMap[icon];

  return (
    <div className="bg-card border border-border rounded-xl p-5 flex items-center justify-between hover:border-primary/50 transition-colors group cursor-pointer">
      <div className="flex items-center gap-6">
        <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
          <Icon className="size-5" />
        </div>
        <div>
          <h3 className="font-bold text-lg">{title}</h3>
          <p className="text-muted-foreground text-sm">
            Project: {project} • {client}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-8">
        <div className="text-right">
          <p className="text-muted-foreground text-xs font-bold uppercase tracking-wider mb-1">Status</p>
          <span className={cn(
            "px-3 py-1 text-[10px] font-black uppercase tracking-tighter rounded-full",
            statusStyles[status]
          )}>
            {statusLabels[status]}
          </span>
        </div>
        <div className="text-right">
          <p className="text-muted-foreground text-xs font-bold uppercase tracking-wider mb-1">Applicants</p>
          <div className="flex -space-x-2">
            {applicants.slice(0, 2).map((applicant, i) => (
              <div
                key={i}
                className="size-8 rounded-full border-2 border-card bg-cover bg-center"
                style={{ backgroundImage: `url('${applicant.image}')` }}
              />
            ))}
            {applicants.length > 2 && (
              <div className="size-8 rounded-full border-2 border-card bg-secondary flex items-center justify-center text-[10px] font-bold">
                +{applicants.length - 2}
              </div>
            )}
            {applicants.length === 0 && (
              <div className="size-8 rounded-full border-2 border-card bg-secondary flex items-center justify-center text-[10px] font-bold">
                0
              </div>
            )}
          </div>
        </div>
        <button className="text-muted-foreground group-hover:text-primary transition-colors">
          <ChevronRight className="size-5" />
        </button>
      </div>
    </div>
  );
}
