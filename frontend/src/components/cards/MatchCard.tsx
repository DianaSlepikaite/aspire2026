import { Calendar, MapPin, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface MatchCardProps {
  title: string;
  department: string;
  matchScore: number;
  duration: string;
  location: string;
  skills: string[];
  description: string;
  image: string;
}

export function MatchCard({
  title,
  department,
  matchScore,
  duration,
  location,
  skills,
  description,
  image,
}: MatchCardProps) {
  return (
    <div className="group relative flex flex-col bg-card rounded-xl border border-border overflow-hidden hover:border-primary transition-all hover:shadow-2xl hover:shadow-primary/10">
      {/* Image Header */}
      <div className="h-40 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute top-4 left-4 z-20">
          <span className={cn(
            "px-3 py-1 text-xs font-black rounded-lg shadow-lg text-primary-foreground",
            matchScore >= 90 ? "bg-primary" : matchScore >= 80 ? "bg-primary/90" : "bg-primary/80"
          )}>
            {matchScore}% MATCH
          </span>
        </div>
        <div className="absolute bottom-4 left-4 z-20">
          <p className="text-xs text-slate-300 font-medium uppercase tracking-widest mb-1">
            {department}
          </p>
          <h3 className="text-white text-lg font-bold leading-tight">{title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="size-3.5" />
            {duration}
          </span>
          <span className="flex items-center gap-1">
            <MapPin className="size-3.5" />
            {location}
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <span
              key={skill}
              className="px-2 py-1 rounded bg-secondary text-[10px] font-bold uppercase"
            >
              {skill}
            </span>
          ))}
        </div>

        <p className="text-sm line-clamp-2 text-muted-foreground">{description}</p>

        <div className="pt-2">
          <Button className="w-full font-bold">Express Interest</Button>
        </div>
      </div>
    </div>
  );
}
