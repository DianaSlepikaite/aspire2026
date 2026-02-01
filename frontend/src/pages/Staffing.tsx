import { Header } from "@/components/layout/Header";
import { StaffingProjectCard } from "@/components/cards/StaffingProjectCard";
import { Button } from "@/components/ui/button";
import { PlusCircle, Filter, ChevronDown, AlertTriangle, Calendar, Zap } from "lucide-react";

const projects = [
  {
    projectId: "ALP-829",
    title: "Cloud Migration Alpha",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=200&h=200&fit=crop",
    timeline: "July - Dec 2024",
    manager: "Sarah Chen",
    matchHealth: 92,
    priority: "high" as const,
    roles: [
      {
        role: "Senior DevOps Engineer",
        type: "Cloud Infrastructure • Full-time",
        candidateName: "Marcus V. Thompson",
        candidateImage: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
        matchScore: 98,
        aiInsight: "Strong AWS/Terraform history + available immediately for Q3 ramp up.",
        availability: "available" as const,
      },
      {
        role: "Security Architect",
        type: "Compliance • Part-time",
        candidateName: "Dr. Elena Rodriguez",
        candidateImage: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop&crop=face",
        matchScore: 86,
        aiInsight: "Matches 4/5 compliance certifications; overlap with current project manageable.",
        availability: "limited" as const,
      },
    ],
  },
  {
    projectId: "INT-041",
    title: "Data Lake Governance",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=200&h=200&fit=crop",
    timeline: "Aug - Oct 2024",
    manager: "David K. Miller",
    matchHealth: 64,
    priority: "internal" as const,
    roles: [
      {
        role: "Principal Data Scientist",
        type: "Machine Learning • Full-time",
        candidateName: null,
        candidateImage: null,
        matchScore: null,
        aiInsight: "Requires niche 'Snowflake Governance' expertise currently unassigned in pool.",
        availability: "unavailable" as const,
      },
    ],
  },
];

const filterChips = [
  { label: "All Departments", active: true, hasDropdown: true },
  { label: "Urgent Only", active: false, icon: AlertTriangle },
  { label: "Match > 85%", active: false, hasDropdown: true },
  { label: "Q3-Q4 Availability", active: false, icon: Calendar },
];

export default function Staffing() {
  return (
    <div className="min-h-screen bg-background dark">
      <Header variant="staffing" />

      <main className="max-w-[1440px] mx-auto p-6 md:p-10">
        {/* Page Heading */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div className="flex flex-col gap-1">
            <h1 className="text-4xl font-black leading-tight tracking-tight">Match Orchestration</h1>
            <p className="text-muted-foreground text-lg">12 Active Projects, 48 Optimal Matches Found</p>
          </div>
          <div className="flex gap-3">
            <Button className="font-bold">
              <PlusCircle className="size-4 mr-2" />
              New Project Request
            </Button>
            <Button variant="outline" className="font-bold">
              <Filter className="size-4 mr-2" />
              Advanced Filters
            </Button>
          </div>
        </div>

        {/* Filter Chips */}
        <div className="flex gap-3 mb-8 flex-wrap">
          {filterChips.map((chip, idx) => (
            <button
              key={idx}
              className={`flex h-9 items-center justify-center gap-2 rounded-full px-4 text-sm font-medium transition-colors ${
                chip.active
                  ? "bg-primary/10 border border-primary/30 text-primary font-semibold"
                  : "bg-card border border-border text-muted-foreground hover:bg-secondary"
              }`}
            >
              {chip.icon && <chip.icon className="size-4 text-primary" />}
              <span>{chip.label}</span>
              {chip.hasDropdown && <ChevronDown className="size-4" />}
            </button>
          ))}
        </div>

        {/* Projects */}
        <div className="space-y-8">
          <h2 className="text-2xl font-bold tracking-tight px-1 flex items-center gap-2">
            <Zap className="size-5 text-primary" />
            Active Project Matches
          </h2>

          {projects.map((project, idx) => (
            <StaffingProjectCard key={idx} {...project} />
          ))}
        </div>

        {/* Load More */}
        <div className="mt-12 flex flex-col items-center gap-4">
          <Button variant="outline" size="lg" className="font-bold">
            <ChevronDown className="size-4 mr-2" />
            Load More Projects
          </Button>
          <p className="text-sm text-muted-foreground">Showing 2 of 12 projects</p>
        </div>
      </main>

      {/* Floating AI Button */}
      <button className="fixed bottom-8 right-8 size-14 rounded-full bg-primary text-primary-foreground shadow-2xl shadow-primary/40 flex items-center justify-center hover:scale-110 transition-transform active:scale-95 group">
        <Zap className="size-6" />
        <span className="absolute right-16 bg-foreground text-background text-xs py-1.5 px-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
          Ask AI about these matches
        </span>
      </button>
    </div>
  );
}
