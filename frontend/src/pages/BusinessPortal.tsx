import { useState } from "react";
import { DarkSidebar } from "@/components/layout/DarkSidebar";
import { Button } from "@/components/ui/button";
import { Bell, Settings } from "lucide-react";
import BusinessStaffing from "@/components/layout/BusinessStaffing";
import BusinessRoles from "@/components/layout/BusinessRoles";
import BusinessReports from "@/components/layout/BusinessReports";

export default function BusinessPortal() {
  const [activeTab, setActiveTab] = useState<"staffing" | "roles" | "reports">("staffing");

  return (
    <div className="flex h-screen overflow-hidden dark">
      <DarkSidebar
        variant="business"
        userName="Alex Rivera"
        userRole="Workforce Planning Lead"
        userImage="https://images.unsplash.com/photo-1544723795-3fb6469f5b39?w=100&h=100&fit=crop&crop=face"
      />

      <main className="flex-1 h-full bg-background overflow-y-auto">
        <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md px-10 py-6 border-b border-border flex justify-between items-center">
          <nav className="flex gap-8" role="tablist" aria-label="Business sections">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "staffing"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "staffing" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("staffing")}
            >
              Staffing
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "roles"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "roles" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("roles")}
            >
              Roles
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "reports"}
              className={`text-muted-foreground font-medium pb-1 transition-colors hover:text-foreground ${
                activeTab === "reports" ? "text-primary font-bold border-b-2 border-primary" : ""
              }`}
              onClick={() => setActiveTab("reports")}
            >
              Reports
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
          {activeTab === "staffing" && <BusinessStaffing />}
          {activeTab === "roles" && <BusinessRoles />}
          {activeTab === "reports" && <BusinessReports />}
        </div>
      </main>
    </div>
  );
}
