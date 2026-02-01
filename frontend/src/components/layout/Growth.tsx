import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CourseCard } from "@/components/cards/CourseCard";
import { Clock, Flame, Trophy } from "lucide-react";
import {
  inProgressLearning,
  learningRecommendations,
  learningStats,
  mandatoryTrainings,
} from "@/components/layout/learningData";

export default function Growth() {
  return (
    <section className="space-y-10">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h3 className="text-2xl font-bold">Growth & Learning</h3>
          <p className="text-muted-foreground mt-1">
            Track learnings, maintain mandatory training, and move toward skill goals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" className="font-semibold">
            <Trophy className="size-4 mr-2" />
            View Achievements
          </Button>
          <Button className="font-semibold">Log Learning</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {learningStats.map((stat) => (
          <div key={stat.label} className="rounded-2xl border border-border bg-card p-5">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">{stat.label}</p>
            <div className="mt-3 flex items-end justify-between">
              <p className="text-2xl font-bold">{stat.value}</p>
              <Badge variant="secondary">{stat.change}</Badge>
            </div>
          </div>
        ))}
      </div>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h4 className="text-xl font-bold">In Progress</h4>
          <Button variant="link" className="text-primary font-semibold">
            View All
          </Button>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {inProgressLearning.map((item) => (
            <div key={item.title} className="rounded-2xl border border-border bg-card p-5 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">{item.provider}</p>
                <h5 className="text-lg font-semibold">{item.title}</h5>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Progress</span>
                  <span>{item.progress}%</span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-secondary">
                  <div
                    className="h-2 rounded-full bg-primary"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center gap-2">
                  <Clock className="size-3" />
                  {item.hoursRemaining}h left
                </span>
                <span>Due {item.due}</span>
              </div>
              <Button variant="outline" className="w-full font-semibold">
                Continue
              </Button>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h4 className="text-xl font-bold">Recommended Learning</h4>
          <Button variant="link" className="text-primary font-semibold">
            Explore Catalog
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {learningRecommendations.map((course, idx) => (
            <CourseCard key={idx} {...course} />
          ))}
        </div>
      </section>

      <section className="space-y-5">
        <div className="flex items-center justify-between">
          <h4 className="text-xl font-bold">Mandatory Training</h4>
          <Button variant="link" className="text-primary font-semibold">
            View Policy
          </Button>
        </div>
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="divide-y divide-border">
            {mandatoryTrainings.map((item) => (
              <div key={item.title} className="flex flex-col gap-3 p-5 md:flex-row md:items-center md:justify-between">
                <div className="space-y-1">
                  <h5 className="text-base font-semibold">{item.title}</h5>
                  <p className="text-xs text-muted-foreground">{item.requiredBy}</p>
                </div>
                <div className="flex flex-wrap items-center gap-4 text-sm">
                  <span className="text-muted-foreground">Due {item.due}</span>
                  <Badge variant={item.status === "Completed" ? "secondary" : "destructive"}>
                    {item.status}
                  </Badge>
                  <Button variant="outline" size="sm" className="font-semibold">
                    {item.status === "Completed" ? "Review" : "Start"}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-secondary/40 p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Flame className="size-5 text-primary" />
            <div>
              <p className="font-semibold">Learning Streak: 12 days</p>
              <p className="text-xs text-muted-foreground">Keep it going to unlock bonuses.</p>
            </div>
          </div>
          <Button variant="secondary" className="font-semibold">
            View Streak
          </Button>
        </div>
      </section>
    </section>
  );
}
