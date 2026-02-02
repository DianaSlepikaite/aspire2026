import { useCallback, useEffect, useState } from "react";
import { DarkSidebar } from "@/components/layout/DarkSidebar";
import { Button } from "@/components/ui/button";
import { Bell, Settings } from "lucide-react";
import BusinessStaffing from "@/components/layout/BusinessStaffing";
import BusinessRoles from "@/components/layout/BusinessRoles";
import BusinessReports from "@/components/layout/BusinessReports";
import { AgentResponse } from "@/lib/clientNeedApi";
import { DocumentProvider } from "@/context/DocumentContext";
import { EmployeeProvider } from "@/context/EmployeeContext";

const STORAGE_KEYS = {
  selectedClientNeedId: "business.selectedClientNeedId",
  activeTab: "business.activeTab",
  agentRuns: "business.agentRuns",
} as const;

function loadAgentRuns(): AgentResponse[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEYS.agentRuns);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function loadActiveTab(): "staffing" | "roles" | "reports" {
  const saved = window.localStorage.getItem(STORAGE_KEYS.activeTab);
  if (saved === "staffing" || saved === "roles" || saved === "reports") return saved;
  return "staffing";
}

export default function BusinessPortal() {
  const [activeTab, setActiveTab] = useState<"staffing" | "roles" | "reports">(loadActiveTab);
  const [selectedClientNeedId, setSelectedClientNeedId] = useState<string | null>(null);
  const [agentRuns, setAgentRuns] = useState<AgentResponse[]>(loadAgentRuns);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEYS.selectedClientNeedId);
    if (saved) {
      setSelectedClientNeedId(saved);
    }
  }, []);

  // Persist activeTab to localStorage
  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEYS.activeTab, activeTab);
  }, [activeTab]);

  // Persist agentRuns to localStorage whenever they change
  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEYS.agentRuns, JSON.stringify(agentRuns));
  }, [agentRuns]);

  const addAgentRun = useCallback((result: AgentResponse) => {
    setAgentRuns((prev) => {
      // Deduplicate: replace existing run for the same client_need_id
      if (result.client_need_id) {
        const filtered = prev.filter((r) => r.client_need_id !== result.client_need_id);
        return [result, ...filtered];
      }
      return [result, ...prev];
    });
  }, []);

  return (
    <EmployeeProvider>
      <DocumentProvider>
        <div className="flex h-screen overflow-hidden dark">
        <DarkSidebar
          variant="business"
          userName="Alex Rivera"
          userRole="Workforce Planning Lead"
          userImage="https://images.unsplash.com/photo-1544723795-3fb6469f5b39?w=100&h=100&fit=crop&crop=face"
          activeClientNeedId={selectedClientNeedId}
          onClientNeedCreated={(clientNeedId) => {
            setSelectedClientNeedId(clientNeedId);
            window.localStorage.setItem(STORAGE_KEYS.selectedClientNeedId, clientNeedId);
            setActiveTab("roles");
          }}
          onAgentResult={(result) => {
            addAgentRun(result);
            if (result.client_need_id) {
              setSelectedClientNeedId(result.client_need_id);
              window.localStorage.setItem(STORAGE_KEYS.selectedClientNeedId, result.client_need_id);
              setActiveTab("roles");
            }
          }}
        />

        <main className="flex-1 h-full bg-background overflow-y-auto">
          <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md px-10 py-6 border-b border-border flex justify-between items-center">
            <nav className="flex gap-8" role="tablist" aria-label="Business sections">
              <button
                type="button"
                role="tab"
                id="tab-staffing"
                aria-controls="tabpanel-staffing"
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
                id="tab-roles"
                aria-controls="tabpanel-roles"
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
                id="tab-reports"
                aria-controls="tabpanel-reports"
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
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-foreground"
                aria-label="Notifications"
              >
                <Bell className="size-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-foreground"
                aria-label="Settings"
              >
                <Settings className="size-5" />
              </Button>
            </div>
          </header>

          <div className="p-10 max-w-6xl mx-auto space-y-12">
            {activeTab === "staffing" && (
              <section role="tabpanel" id="tabpanel-staffing" aria-labelledby="tab-staffing" tabIndex={0}>
                <BusinessStaffing
                selectedClientNeedId={selectedClientNeedId}
                onSelectNeed={(id) => {
                  setSelectedClientNeedId(id);
                  window.localStorage.setItem(STORAGE_KEYS.selectedClientNeedId, id);
                }}
                  onViewRoles={() => setActiveTab("roles")}
                  agentRuns={agentRuns}
                />
              </section>
            )}
            {activeTab === "roles" && (
              <section role="tabpanel" id="tabpanel-roles" aria-labelledby="tab-roles" tabIndex={0}>
                <BusinessRoles clientNeedId={selectedClientNeedId} agentRuns={agentRuns} />
              </section>
            )}
            {activeTab === "reports" && (
              <section role="tabpanel" id="tabpanel-reports" aria-labelledby="tab-reports" tabIndex={0}>
                <BusinessReports agentRuns={agentRuns} />
              </section>
            )}
          </div>
        </main>
        </div>
      </DocumentProvider>
    </EmployeeProvider>
  );
}
