import { Send, Mic, FileUp, Sparkles, TrendingUp, FileEdit, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface AISidebarProps {
  variant?: "employee" | "staffing";
  userName?: string;
  message?: string;
}

export function AISidebar({ variant = "employee", userName = "there", message }: AISidebarProps) {
  const defaultMessage = variant === "employee"
    ? `Hey ${userName}! Based on your recent certification in Cloud Architecture, I've found 3 new matches in the Engineering department.`
    : `Ready to analyze your talent pool and optimize staffing decisions.`;

  return (
    <aside className="w-80 shrink-0 hidden lg:flex flex-col gap-6 sticky top-24 h-[calc(100vh-120px)]">
      <div className="flex flex-col flex-1 bg-card rounded-xl border border-border overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-border">
          <div className="flex items-center gap-2 mb-1">
            <Brain className="size-5 text-primary" />
            <h3 className="font-bold text-lg">AI Career Coach</h3>
          </div>
          <p className="text-xs text-muted-foreground">
            Your matches are optimized for growth.
          </p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="bg-secondary p-3 rounded-lg text-sm leading-relaxed">
            {message || defaultMessage}
          </div>

          <div className="flex flex-col gap-2">
            <QuickAction 
              icon={<Sparkles className="size-4" />} 
              label="Explain my matches" 
              active 
            />
            <QuickAction 
              icon={<FileEdit className="size-4" />} 
              label="Improve profile visibility" 
            />
            <QuickAction 
              icon={<TrendingUp className="size-4" />} 
              label="Skill gap analysis" 
            />
          </div>
        </div>

        {/* Input */}
        <div className="p-4 bg-secondary/50 mt-auto border-t border-border">
          <div className="relative">
            <Input
              className="w-full pl-4 pr-10 py-2.5 bg-background border-border"
              placeholder="Ask AI Coach..."
            />
            <Button
              size="icon"
              variant="ghost"
              className="absolute right-1 top-1/2 -translate-y-1/2 size-8 text-primary hover:text-primary"
            >
              <Send className="size-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <Button className="w-full py-6 font-bold shadow-glow-sm hover:shadow-glow transition-shadow">
        <Sparkles className="size-4 mr-2" />
        New Role Query
      </Button>
    </aside>
  );
}

function QuickAction({ 
  icon, 
  label, 
  active = false 
}: { 
  icon: React.ReactNode; 
  label: string; 
  active?: boolean;
}) {
  return (
    <button 
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left",
        active 
          ? "bg-primary/10 text-primary hover:bg-primary/20" 
          : "hover:bg-secondary"
      )}
    >
      {icon}
      {label}
    </button>
  );
}
