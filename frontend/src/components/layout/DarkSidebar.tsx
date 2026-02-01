import { Mic, MessageSquare, FileUp, PlusCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface DarkSidebarProps {
  userName?: string;
  userRole?: string;
  userImage?: string;
}

export function DarkSidebar({ 
  userName = "Sarah Jenkins",
  userRole = "Senior Project Manager",
  userImage = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face"
}: DarkSidebarProps) {
  return (
    <aside className="w-1/2 min-w-[400px] h-full bg-background flex flex-col border-r border-border p-8">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-12">
        <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
          <Zap className="size-4 text-primary-foreground" />
        </div>
        <h2 className="text-foreground text-xl font-bold tracking-tight">Talent Orchestration</h2>
      </div>

      {/* Welcome Message */}
      <div className="flex-1 flex flex-col justify-between gap-8">
        <div className="space-y-4">
          <h1 className="text-4xl font-extrabold text-foreground leading-tight">
            Welcome back, {userName.split(' ')[0]}.
          </h1>
          <p className="text-muted-foreground text-lg">
            Your AI career assistant is ready. How can I help you grow today?
          </p>
        </div>

        {/* AI Pulse Visualizer */}
        <div className="h-24 flex  items-center justify-center gap-1">
          {[40, 60, 100, 80, 50, 70].map((height, i) => (
            <div
              key={i}
              className="w-1 bg-primary rounded-full animate-pulse"
              style={{
                height: `${height}%`,
                opacity: height / 100,
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>

        {/* AI Interaction Composer */}
      <div className="bg-card border border-border rounded-xl p-4">
          <Textarea
            className="w-full bg-transparent border-none resize-none h-32 text-base placeholder:text-muted-foreground focus-visible:ring-0"
            placeholder="Ask AI to analyze your recent project or update your CV..."
          />
          <div className="flex items-center justify-between pt-2 border-t border-border mt-4">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                <Mic className="size-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                <FileUp className="size-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                <PlusCircle className="size-5" />
              </Button>
            </div>
            <Button className="font-semibold">
              Send Command
            </Button>
          </div>
        </div>
        
      </div>
      

      {/* User Profile */}
      <div className="mt-auto pt-8 flex items-center gap-4 border-t border-border">
        <div 
          className="size-10 rounded-full bg-cover bg-center border border-border"
          style={{ backgroundImage: `url('${userImage}')` }}
        />
        <div className="flex-1 min-w-0">
          <p className="text-foreground text-sm font-semibold truncate">{userName}</p>
          <p className="text-muted-foreground text-xs truncate">{userRole}</p>
        </div>
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="size-5">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" x2="9" y1="12" y2="12" />
          </svg>
        </Button>
      </div>
    </aside>
  );
}
