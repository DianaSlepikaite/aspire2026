import { Button } from "@/components/ui/button";

export default function Opportunities() {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold">Opportunities</h3>
        <Button variant="link" className="text-primary font-semibold">
          Explore Matches
        </Button>
      </div>
      <div className="bg-card rounded-2xl border border-border p-8">
        <p className="text-muted-foreground">
          Discover internal roles, projects, and stretch assignments aligned to your profile and growth goals.
        </p>
      </div>
    </section>
  );
}
