import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface CoreHeaderProps {
  lastSyncLabel: string;
  isSaving: boolean;
  canSave: boolean;
  onSync: () => void;
  onSave: () => void;
}

export function CoreHeader({ lastSyncLabel, isSaving, canSave, onSync, onSave }: CoreHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-6">
      <div>
        <h3 className="text-2xl font-bold">Core Employee Profile</h3>
        <p className="text-muted-foreground mt-1">
          Synced from agent insights and enriched by your edits. {lastSyncLabel}.
        </p>
      </div>
      <div className="flex items-center gap-3">
        <Button variant="secondary" className="font-semibold" onClick={onSync}>
          <RefreshCw className="size-4 mr-2" />
          Sync From Agent
        </Button>
        <Button className="font-semibold" onClick={onSave} disabled={isSaving || !canSave}>
          {isSaving ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}
