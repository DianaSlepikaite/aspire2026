import { Brain, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface ProfileCardProps {
  name: string;
  role: string;
  department: string;
  image: string;
  skills: string[];
  verified?: boolean;
}

export function ProfileCard({
  name,
  role,
  department,
  image,
  skills,
  verified = true,
}: ProfileCardProps) {
  return (
    <div className="col-span-2 bg-card p-8 rounded-2xl shadow-sm border border-border flex gap-8 items-start">
      <div
        className="size-24 rounded-2xl bg-secondary bg-cover bg-center shrink-0"
        style={{ backgroundImage: `url('${image}')` }}
      />
      <div className="flex-1">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h4 className="text-xl font-bold">{name}</h4>
            <p className="text-muted-foreground">
              {role} • {department}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mb-6">
          {skills.slice(0, 3).map((skill) => (
            <span
              key={skill}
              className="bg-primary/10 text-primary text-xs font-semibold px-3 py-1 rounded-full border border-primary/20"
            >
              {skill}
            </span>
          ))}
          {skills.length > 3 && (
            <span className="bg-secondary text-muted-foreground text-xs font-semibold px-3 py-1 rounded-full border border-border">
              +{skills.length - 3} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export function SkillAnalysisCard({
  skillName = "Python",
  progress = 72,
  improvement = 15,
}: {
  skillName?: string;
  progress?: number;
  improvement?: number;
}) {
  return (
    <div className="bg-card p-8 rounded-2xl shadow-sm border border-border flex flex-col items-center justify-center text-center">
      <div className="size-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mb-4">
        <Brain className="size-8" />
      </div>
      <h4 className="font-bold text-lg mb-1">Skill Analysis</h4>
      <p className="text-muted-foreground text-sm mb-4">
        Your proficiency in '{skillName}' has increased by {improvement}% this month.
      </p>
      <Progress value={progress} className="w-full h-2" />
    </div>
  );
}
