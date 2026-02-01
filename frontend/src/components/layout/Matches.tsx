import { Header } from "@/components/layout/Header";
import { AISidebar } from "@/components/layout/AISidebar";
import { Footer } from "@/components/layout/Footer";
import { MatchCard } from "@/components/cards/MatchCard";
import { Button } from "@/components/ui/button";
import { Filter, Check, ChevronDown, Zap } from "lucide-react";

const matches = [
  {
    title: "Project Phoenix: Lead Developer",
    department: "Engineering Dept",
    matchScore: 98,
    duration: "6 Months",
    location: "Remote",
    skills: ["React", "GoLang", "Architecture"],
    description: "Scale the core orchestration engine to support 10M+ concurrent users. Looking for high architectural ownership.",
    image: "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=200&fit=crop",
  },
  {
    title: "Growth Specialist: Alpha",
    department: "Marketing Dept",
    matchScore: 92,
    duration: "12 Months",
    location: "Hybrid",
    skills: ["Data Analysis", "SEO"],
    description: "Design experiments to increase user retention across the DACH region by 15% using behavior-based triggers.",
    image: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop",
  },
  {
    title: "Nexus Ops: Coordinator",
    department: "Operations Dept",
    matchScore: 89,
    duration: "3 Months",
    location: "Remote",
    skills: ["Agile", "Logistics"],
    description: "Oversee the migration of the internal supply chain database to the new SAP instance. Short-term high impact.",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",
  },
  {
    title: "Security Engineer: Cloud",
    department: "Infrastructure",
    matchScore: 85,
    duration: "Ongoing",
    location: "Hybrid",
    skills: ["CyberSec", "AWS"],
    description: "Implement Zero Trust protocols across our cloud migration efforts. Critical role for the security roadmap.",
    image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=200&fit=crop",
  },
];

const filters = [
  { label: "Highest Match", active: true, icon: Check },
  { label: "Engineering", active: false, hasDropdown: true },
  { label: "Remote Only", active: false },
  { label: "Urgent Needs", active: false, icon: Zap, highlight: true },
];

export default function Matches() {
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
          <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-6">
            {matches.map((match, idx) => (
              <MatchCard key={idx} {...match} />
            ))}
          </div>
        </div>
      </section>
  );
}
