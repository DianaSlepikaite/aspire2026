import { NavLink } from "@/components/NavLink";
import { RoleCard } from "@/components/cards/RoleCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mic, MessageSquare, FileUp, PlusCircle, Search, Bell, TrendingUp, TrendingDown, Zap } from "lucide-react";

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

export default function Roles() {
  return (
    <div className="flex h-screen overflow-hidden dark">
      {/* Left Sidebar: AI Tools */}
      <aside className="w-64 border-r border-border flex flex-col bg-background">
        <div className="p-6 flex items-center gap-3">
          <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
            <Zap className="size-4 text-primary-foreground" />
          </div>
          <h2 className="text-foreground text-lg font-bold tracking-tight">Orchestrator</h2>
        </div>

        <div className="flex-1 px-4 flex flex-col gap-6 py-4">
          <div className="flex flex-col gap-1">
            <h1 className="text-foreground text-sm font-semibold px-3 mb-1">AI Assistant</h1>
            <p className="text-muted-foreground text-xs px-3 font-normal">Ready to analyze your talent pool</p>
          </div>

          <nav className="flex flex-col gap-2">
            <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors group">
              <Mic className="size-4 text-primary" />
              <span className="text-foreground text-sm font-medium">Voice Command</span>
            </button>
            <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-secondary/50 transition-colors">
              <MessageSquare className="size-4 text-muted-foreground" />
              <span className="text-foreground text-sm font-medium">Message AI</span>
            </button>
            <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-secondary/50 transition-colors">
              <FileUp className="size-4 text-muted-foreground" />
              <span className="text-foreground text-sm font-medium">Upload File</span>
            </button>
          </nav>

          <div className="mt-auto border-t border-border pt-6 pb-4">
            <div className="bg-secondary/30 p-4 rounded-xl border border-border">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold mb-2">AI Status</p>
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
                </span>
                <p className="text-xs text-foreground">Analyzing role fit...</p>
              </div>
            </div>
          </div>
        </div>

        <div className="p-4">
          <Button className="w-full font-bold">
            <PlusCircle className="size-4 mr-2" />
            New Request
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Top Nav Bar */}
        <header className="flex items-center justify-between h-16 border-b border-border px-8 bg-background/50 backdrop-blur-md sticky top-0 z-10">
          <nav className="flex items-center gap-6">
            <NavLink 
              to="/portal"
              className="text-foreground text-sm font-semibold"
              activeClassName="text-primary"
            >
              Dashboard
            </NavLink>
            <NavLink 
              to="/staffing" 
              className="text-muted-foreground text-sm font-medium hover:text-foreground transition-colors"
              activeClassName="text-primary font-semibold border-b-2 border-primary py-5"
            >
              Staffing
            </NavLink>
            <NavLink 
              to="/roles" 
              className="text-primary text-sm font-semibold border-b-2 border-primary py-5"
              activeClassName="text-primary font-semibold border-b-2 border-primary"
            >
              Roles
            </NavLink>
            <span className="text-muted-foreground text-sm font-medium cursor-pointer hover:text-foreground transition-colors">
              Reports
            </span>
            <span className="text-muted-foreground text-sm font-medium cursor-pointer hover:text-foreground transition-colors">
              Settings
            </span>
          </nav>

          <div className="flex items-center gap-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                className="w-64 bg-secondary border-none pl-10"
                placeholder="Search talent or roles..."
                aria-label="Search talent or roles"
              />
            </div>
            <div className="flex items-center gap-3 border-l border-border pl-6">
              <Button
                variant="ghost"
                size="icon"
                className="bg-secondary text-foreground hover:bg-secondary/80"
                aria-label="Notifications"
              >
                <Bell className="size-5" />
              </Button>
              <div
                className="size-9 rounded-full bg-cover bg-center border border-border"
                style={{ backgroundImage: "url('https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50&h=50&fit=crop&crop=face')" }}
                role="img"
                aria-label="User avatar"
              />
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-8 max-w-7xl mx-auto w-full">
          {/* Page Heading */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-4xl font-black tracking-tight leading-tight">Roles Management</h2>
              <p className="text-muted-foreground text-base mt-2">
                Allocate and optimize staffing for active project cycles.
              </p>
            </div>
            <Button variant="secondary" className="font-bold">
              <PlusCircle className="size-4 mr-2" />
              Add New Role
            </Button>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {stats.map((stat, idx) => (
              <div key={idx} className="flex flex-col gap-2 rounded-xl p-6 border border-border bg-card">
                <p className="text-muted-foreground text-sm font-medium">{stat.label}</p>
                <div className="flex items-end justify-between">
                  <p className="text-3xl font-bold">{stat.value}</p>
                  <span className={`text-sm font-bold flex items-center gap-1 ${stat.up ? "text-success" : "text-warning"}`}>
                    {stat.up ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                    {stat.change}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Tabs Section */}
          <div className="mb-8">
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

          {/* Roles Grid */}
          <div className="grid grid-cols-1 gap-4">
            {roles.map((role, idx) => (
              <RoleCard key={idx} {...role} />
            ))}
          </div>

          {/* Footer Summary */}
          <div className="mt-12 flex items-center justify-between text-muted-foreground text-sm border-t border-border pt-6">
            <p>© 2024 Talent Orchestrator Platform. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-foreground transition-colors">Documentation</a>
              <a href="#" className="hover:text-foreground transition-colors">Support</a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
