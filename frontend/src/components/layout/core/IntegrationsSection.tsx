import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Link2 } from "lucide-react";

interface IntegrationItem {
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  connected: boolean;
  handle: string;
}

interface IntegrationsSectionProps {
  integrations: IntegrationItem[];
}

export function IntegrationsSection({ integrations }: IntegrationsSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Integrations</h4>
        <Badge variant="secondary">Manage</Badge>
      </div>
      <div className="space-y-3">
        {integrations.map((integration) => (
          <div key={integration.name} className="rounded-xl border border-border p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="size-10 rounded-xl bg-secondary flex items-center justify-center">
                  <integration.icon className="size-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-semibold">{integration.name}</p>
                  <p className="text-xs text-muted-foreground">{integration.description}</p>
                </div>
              </div>
              <Switch defaultChecked={integration.connected} />
            </div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="flex items-center gap-2">
                <Link2 className="size-3" />
                {integration.handle}
              </span>
              <Button variant="ghost" size="sm" className="text-muted-foreground">
                {integration.connected ? "Disconnect" : "Connect"}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
