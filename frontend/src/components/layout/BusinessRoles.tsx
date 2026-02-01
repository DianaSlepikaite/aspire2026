import { RoleCard } from "@/components/cards/RoleCard";
import { Button } from "@/components/ui/button";
import { TrendingDown, TrendingUp } from "lucide-react";

const stats = [
  { label: "Total Project Roles", value: 42, change: "+2.4%", up: true },
  { label: "Open Positions", value: 12, change: "+5.1%", up: true },
  { label: "Filled (Last 30 days)", value: 30, change: "-1.2%", up: false },
];

const roles = [
  {
    title: "Senior Fullstack Engineer",
    project: "Neo-Banking Mobile App",
    client: "CloudScale Systems",
    status: "high-priority" as const,
    icon: "code" as const,
    applicants: [
      { image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=50&h=50&fit=crop&crop=face" },
      { image: "" },
      { image: "" },
      { image: "" },
      { image: "" },
    ],
  },
  {
    title: "Lead Product Designer",
    project: "Design System 2.0",
    client: "MetaLogix",
    status: "interviewing" as const,
    icon: "design" as const,
    applicants: [
      { image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=50&h=50&fit=crop&crop=face" },
      { image: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=50&h=50&fit=crop&crop=face" },
      { image: "" },
      { image: "" },
    ],
  },
  {
    title: "Data Architect",
    project: "Big Data Migration",
    client: "FinServ Global",
    status: "pending" as const,
    icon: "data" as const,
    applicants: [],
  },
];

const tabs = ["Client", "Project", "Roles", "Documents"];

export default function BusinessRoles() {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Roles Management</h3>
          <p className="text-muted-foreground text-sm mt-2">
            Allocate and optimize staffing for active project cycles.
          </p>
        </div>
        <Button variant="secondary" className="font-bold">
          Create New Role
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="flex flex-col gap-2 rounded-xl p-6 border border-border bg-card">
            <p className="text-muted-foreground text-sm font-medium">{stat.label}</p>
            <div className="flex items-end justify-between">
              <p className="text-2xl font-bold">{stat.value}</p>
              <span className={`text-sm font-bold flex items-center gap-1 ${stat.up ? "text-success" : "text-warning"}`}>
                {stat.up ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                {stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div>
        <div className="flex border-b border-border gap-10">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`flex flex-col items-center justify-center pb-4 pt-2 transition-all ${
                tab === "Roles"
                  ? "border-b-2 border-primary text-foreground"
                  : "border-b-2 border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <p className="text-sm font-bold tracking-wide">{tab}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {roles.map((role, idx) => (
          <RoleCard key={idx} {...role} />
        ))}
      </div>
    </section>
  );
}
