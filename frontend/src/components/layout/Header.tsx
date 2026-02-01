import { Search, Bell, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { NavLink } from "@/components/NavLink";

interface HeaderProps {
  variant?: "default" | "staffing";
}

export function Header({ variant = "default" }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md px-6 py-3">
      <div className="max-w-[1440px] mx-auto flex items-center justify-between">
        <div className="flex items-center gap-8">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="size-5 text-primary-foreground" fill="currentColor">
                <path d="M21.22 22C21.22 22 18.04 17 20.58 12C23.43 6.47 21.19 2 21.19 2L3.51 2C3.51 2 5.83 6.47 2.98 12C0.44 17 3.64 22 3.64 22L21.22 22Z" />
              </svg>
            </div>
            <h2 className="text-lg font-bold tracking-tight hidden sm:block">
              Talent Orchestrator
            </h2>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <NavLink 
              to="/" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              activeClassName="text-primary font-semibold"
            >
              Dashboard
            </NavLink>
            <NavLink 
              to="/matches" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              activeClassName="text-primary font-semibold"
            >
              My Matches
            </NavLink>
            <NavLink 
              to="/staffing" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              activeClassName="text-primary font-semibold"
            >
              Staffing
            </NavLink>
            <NavLink 
              to="/roles" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              activeClassName="text-primary font-semibold"
            >
              Roles
            </NavLink>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative hidden lg:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              className="pl-10 w-64 bg-secondary border-none"
              placeholder="Search roles or projects..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Bell className="size-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Settings className="size-5" />
            </Button>
          </div>

          {/* User Avatar */}
          <div className="size-10 rounded-full border-2 border-primary overflow-hidden bg-primary/20">
            <img
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face"
              alt="User profile"
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
