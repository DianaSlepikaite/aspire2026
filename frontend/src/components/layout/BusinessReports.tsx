import { Button } from "@/components/ui/button";

export default function BusinessReports() {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-black tracking-tight">Business Reports</h3>
          <p className="text-muted-foreground mt-2">
            Monitor staffing health, pipeline velocity, and project utilization.
          </p>
        </div>
        <Button variant="secondary" className="font-bold">
          Export Report
        </Button>
      </div>
      <div className="bg-card rounded-2xl border border-border p-8">
        <p className="text-muted-foreground">
          Reports dashboard coming soon. This area will surface staffing trends, fulfillment SLAs,
          and team utilization metrics across projects.
        </p>
      </div>
    </section>
  );
}
