import { useState } from "react";
import { DarkSidebar } from "@/components/layout/DarkSidebar";
import { Button } from "@/components/ui/button";
import { Bell, Settings } from "lucide-react";
import Profile from "@/components/layout/Profile";
import Core from "@/components/layout/Core";
import Growth from "@/components/layout/Growth";
import Matches from "../components/layout/Matches";
import { DocumentProvider } from "@/context/DocumentContext";

export default function Index() {
  const [activeTab, setActiveTab] = useState<"profile" | "core" | "growth" | "opportunities">("profile");

  return (
    <DocumentProvider>
      <div className="flex h-screen overflow-hidden dark">
        {/* Left Panel: AI Interaction Hub */}
        <DarkSidebar
          userName="Sarah Jenkins"
          userRole="Senior Project Manager"
          userImage="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face"
        />

      {/* Right Panel: Dashboard Content */}
      <main className="flex-1 h-full bg-background overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md px-10 py-6 border-b border-border flex justify-between items-center">
          <nav className="flex gap-8" role="tablist" aria-label="Dashboard sections">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "profile"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "profile" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("profile")}
            >
              Profile
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "core"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "core" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("core")}
            >
              Core
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "growth"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "growth" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("growth")}
            >
              Growth
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "opportunities"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "opportunities" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("opportunities")}
            >
              Opportunities
            </button>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Bell className="size-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Settings className="size-5" />
            </Button>
          </div>
        </header>

        <div className="p-10 max-w-6xl mx-auto space-y-12">
          {activeTab === "profile" && (
            <Profile />
          )}

          {activeTab === "core" && (
            <Core />
          )}

          {activeTab === "growth" && (
            <Growth />
          )}

          {activeTab === "opportunities" && (
            <Matches />
          )}
        </div>
        </main>
      </div>
    </DocumentProvider>
  );
}
