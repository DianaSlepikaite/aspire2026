import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Footer } from "@/components/layout/Footer";
import { Mic, ArrowRight, Upload, Info, Bell, User, Paperclip, Zap } from "lucide-react";

export default function Onboarding() {
  return (
    <div className="layout-container flex min-h-screen flex-col dark">
      {/* Top Navigation */}
      <header className="flex items-center justify-between border-b border-border px-6 md:px-20 py-4 bg-background sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="size-8 text-primary">
            <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path d="M42.4379 44C42.4379 44 36.0744 33.9038 41.1692 24C46.8624 12.9336 42.2078 4 42.2078 4L7.01134 4C7.01134 4 11.6577 12.932 5.96912 23.9969C0.876273 33.9029 7.27094 44 7.27094 44L42.4379 44Z" fill="currentColor" />
            </svg>
          </div>
          <h2 className="text-lg font-bold leading-tight tracking-tight hidden sm:block">Talent Orchestration</h2>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="bg-secondary text-muted-foreground hover:text-foreground">
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
        {/* Progress Bar Section */}
        <div className="w-full max-w-xl mb-12">
          <div className="flex justify-between items-end mb-3">
            <div>
              <p className="text-primary text-xs font-bold uppercase tracking-widest mb-1">Getting Started</p>
              <p className="text-xl font-bold">Onboarding Progress</p>
            </div>
            <p className="text-sm font-medium text-muted-foreground">Step 1 of 4 (25%)</p>
          </div>
          <Progress value={25} className="h-2" />
          <p className="mt-3 text-sm text-muted-foreground flex items-center gap-2">
            <Info className="size-4" />
            Setting up your talent profile & preferences
          </p>
        </div>

        {/* Hero Text */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
            Let's get to know each other
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Share your professional journey your way. Speak to us, type it out, or upload your existing CV to begin your orchestration.
          </p>
        </div>

        {/* Interaction Hub */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          {/* Voice Column */}
          <div className="flex flex-col items-center justify-between p-8 bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-shadow group">
            <div className="text-center">
              <h3 className="font-bold text-xl mb-2">Speak</h3>
              <p className="text-sm text-muted-foreground mb-8">Tell us your story via voice note</p>
            </div>
            <div className="relative flex items-center justify-center mb-8">
              <div className="absolute inset-0 bg-primary/20 rounded-full scale-125 animate-ping opacity-20" />
              <button className="relative flex items-center justify-center size-24 rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-transform">
                <Mic className="size-10" />
              </button>
            </div>
            <div className="flex gap-1 h-8 items-end justify-center mb-4">
              {[2, 5, 3, 6, 4, 2].map((h, i) => (
                <div key={i} className="w-1 bg-primary rounded-full" style={{ height: `${h * 4}px` }} />
              ))}
            </div>
            <span className="text-xs font-bold uppercase tracking-tighter text-muted-foreground/60">
              Tap to start recording
            </span>
          </div>

          {/* Manual Entry Column */}
          <div className="flex flex-col p-8 bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="text-center mb-6">
              <h3 className="font-bold text-xl mb-2">Write</h3>
              <p className="text-sm text-muted-foreground">Type or paste your bio manually</p>
            </div>
            <Textarea
              className="flex-1 w-full bg-secondary/50 border-border min-h-[160px] resize-none"
              placeholder="E.g. I am a Senior Product Designer with 8 years of experience in FinTech..."
            />
            <Button className="mt-4 w-full font-bold" variant="secondary">
              Submit Bio
              <ArrowRight className="size-4 ml-2" />
            </Button>
          </div>

          {/* Upload Column */}
          <div className="flex flex-col items-center justify-between p-8 bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="text-center">
              <h3 className="font-bold text-xl mb-2">Upload</h3>
              <p className="text-sm text-muted-foreground mb-8">Import data from your CV/Resume</p>
            </div>
            <div className="w-full flex-1 border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center p-6 bg-secondary/30 hover:bg-primary/5 cursor-pointer transition-colors group">
              <div className="size-16 bg-card border border-border rounded-full flex items-center justify-center mb-4 shadow-sm group-hover:border-primary transition-colors">
                <Upload className="size-8 text-primary" />
              </div>
              <p className="text-sm font-semibold mb-1">Drop your file here</p>
              <p className="text-xs text-muted-foreground/60">PDF, DOCX up to 10MB</p>
            </div>
            <Button variant="outline" className="mt-6 w-full font-medium">
              <Paperclip className="size-4 mr-2" />
              Browse Files
            </Button>
          </div>
        </div>

      </main>

      <Footer variant="minimal" />

      {/* Background Pattern */}
      <div className="fixed inset-0 -z-10 h-full w-full bg-dot-pattern opacity-30" />
    </div>
  );
}
