import { Button } from "@/components/ui/button";
import { Footer } from "@/components/layout/Footer";
import { TalentMatchMark } from "@/components/brand/TalentMatchMark";
import {
  Mic,
  ArrowRight,
  Upload,
  Info,
  Bell,
  User,
  Paperclip,
  Zap,
  Briefcase,
  TrendingUp,
  Users,
} from "lucide-react";
import { NavLink } from "react-router-dom";

export default function Mode() {
  //add mode tracking to use in App for switching profiles between business and career apps
  return (
    <div className="layout-container flex min-h-screen flex-col dark">
      {/* Top Navigation */}
      <header className="flex items-center justify-between border-b border-border px-6 md:px-20 py-4 bg-background sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="size-8 text-primary">
            <TalentMatchMark />
          </div>
          <h2 className="text-lg font-bold leading-tight tracking-tight hidden sm:block">
            TalentMatch
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="bg-secondary text-muted-foreground hover:text-foreground"
          >
            <Bell className="size-5" />
          </Button>
          <div className="h-8 w-[1px] bg-border mx-1" />
          <Button variant="ghost" className="bg-secondary text-foreground">
            <User className="size-5 mr-2" />
            <span className="text-sm font-medium">Alex Rivera</span>
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center px-6 py-10 md:py-16 max-w-5xl mx-auto w-full">
        {/* Hero Text */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
            Which portal would you like to enter?
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Select <i>career</i> for career portal or <i>business</i> for
            project and staffing portal
          </p>
        </div>

        {/* Interaction Hub */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
          {/*Career Column */}
          <NavLink to="/portal" className="flex flex-col items-center justify-between p-8 bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-shadow group">
            <div className="text-center">
              <h3 className="font-bold text-xl mb-2">Career</h3>
              <p className="text-sm text-muted-foreground mb-8">
                Enter your career portal and track your career
              </p>
            </div>
            <div className="relative flex items-center justify-center mb-8">
              {/* soft halo instead of "recording ping" */}
              <div className="absolute inset-0 rounded-full bg-primary/10 blur-xl scale-150 opacity-70" />
              <div className="absolute inset-0 rounded-full border border-primary/20 scale-125 animate-pulse" />

              <button className="relative flex items-center justify-center size-24 rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-transform">
                <Briefcase className="size-10" />
              </button>
            </div>
            <span className="text-xs font-bold uppercase tracking-tighter text-muted-foreground/60">
              Click to enter Career
            </span>
          </NavLink>

          {/* Business Column */}
          <NavLink to="/staffing" className="flex flex-col items-center justify-between p-8 bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-shadow group">
            <div className="text-center">
              <h3 className="font-bold text-xl mb-2">Business</h3>
              <p className="text-sm text-muted-foreground mb-8">
                Match the business with the right people
              </p>
            </div>
            <div className="relative flex items-center justify-center mb-8">
              {/* connection halo */}
              <div className="absolute inset-0 rounded-full bg-primary/10 blur-xl scale-150 opacity-70" />
              <div className="absolute inset-0 rounded-full border border-primary/20 scale-125 animate-pulse" />

              <button className="relative flex items-center justify-center size-24 rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-transform">
                <Users className="size-10" />
              </button>

              {/* matching indicator dots */}
              <div className="absolute left-2 top-1/2 -translate-y-1/2 size-3 rounded-full bg-primary animate-pulse" />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 size-3 rounded-full bg-primary animate-pulse delay-150" />
            </div>

            <span className="text-xs font-bold uppercase tracking-tighter text-muted-foreground/60">
              Click to enter Business
            </span>
          </NavLink>
        </div>
      </main>

      <Footer variant="minimal" />

      {/* Background Pattern */}
      <div className="fixed inset-0 -z-10 h-full w-full bg-dot-pattern opacity-30" />
    </div>
  );
}
