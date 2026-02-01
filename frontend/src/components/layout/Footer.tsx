import { cn } from "@/lib/utils";

interface FooterProps {
  variant?: "default" | "minimal";
}

export function Footer({ variant = "default" }: FooterProps) {
  if (variant === "minimal") {
    return (
      <footer className="mt-auto py-8 px-6 border-t border-border bg-secondary/50">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-6 text-muted-foreground text-xs">
            <a href="#" className="hover:underline">Privacy Policy</a>
            <a href="#" className="hover:underline">Terms of Service</a>
            <a href="#" className="hover:underline">Help Center</a>
          </div>
          <div className="text-xs text-muted-foreground/60">
            © 2024 Talent Orchestration Platform. All rights reserved.
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="mt-12 border-t border-border px-6 py-4 bg-card/50">
      <div className="max-w-[1440px] mx-auto flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1 text-success">
            <span className="size-2 bg-success rounded-full animate-pulse" />
            AI Sync Active
          </span>
          <span>Last updated: 5 mins ago</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="#" className="hover:text-primary transition-colors">Platform Status</a>
          <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-primary transition-colors">Feedback</a>
        </div>
      </div>
    </footer>
  );
}
