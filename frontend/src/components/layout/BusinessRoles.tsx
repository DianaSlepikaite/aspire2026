import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useClientNeed } from "@/hooks/useClientNeeds";
import { useUpdateClientNeed } from "@/hooks/useClientNeeds";

interface BusinessRolesProps {
  clientNeedId?: string | null;
}

function formatCategory(category: string) {
  return category
    .split("_")
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");
}

export default function BusinessRoles({ clientNeedId }: BusinessRolesProps) {
  const { data, isLoading } = useClientNeed(clientNeedId);
  const updateClientNeed = useUpdateClientNeed(clientNeedId);
  const roles = data?.required_roles ?? [];
  const requiredSkills = data?.required_skills ?? [];
  const [formState, setFormState] = useState({
    client_name: "",
    client_company: "",
    client_email: "",
    project_title: "",
    project_description: "",
    required_skills: "",
    timeline_duration_weeks: "",
    budget_min: "",
    budget_max: "",
    urgency_level: "",
    work_location: "",
    team_size_needed: "",
  });

  useEffect(() => {
    if (!data) return;
    setFormState({
      client_name: data.client_name || "",
      client_company: data.client_company || "",
      client_email: data.client_email || "",
      project_title: data.project_title || "",
      project_description: data.project_description || "",
      required_skills: (data.required_skills || []).join(", "),
      timeline_duration_weeks: data.timeline_duration_weeks?.toString() || "",
      budget_min: data.budget_min?.toString() || "",
      budget_max: data.budget_max?.toString() || "",
      urgency_level: data.urgency_level || "",
      work_location: data.work_location || "",
      team_size_needed: data.team_size_needed?.toString() || "",
    });
  }, [data]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Roles & Requirements</h3>
          <p className="text-muted-foreground text-sm mt-2">
            Review the extracted roles and requirements for the selected client need.
          </p>
        </div>
        <Button variant="secondary" className="font-bold">
          Export Summary
        </Button>
      </div>

      {!clientNeedId && (
        <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
          Select a client need from Staffing to view its extracted roles and requirements.
        </div>
      )}

      {clientNeedId && isLoading && (
        <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
          Loading client need details...
        </div>
      )}

      {clientNeedId && data && (
        <>
          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Client Need Details</h4>
              <Button
                className="font-semibold"
                onClick={() => {
                  const payload = {
                    client_name: formState.client_name || null,
                    client_company: formState.client_company || null,
                    client_email: formState.client_email || null,
                    project_title: formState.project_title || null,
                    project_description: formState.project_description || null,
                    required_skills: formState.required_skills
                      ? formState.required_skills.split(",").map((skill) => skill.trim()).filter(Boolean)
                      : null,
                    timeline_duration_weeks: formState.timeline_duration_weeks
                      ? Number(formState.timeline_duration_weeks)
                      : null,
                    budget_min: formState.budget_min ? Number(formState.budget_min) : null,
                    budget_max: formState.budget_max ? Number(formState.budget_max) : null,
                    urgency_level: formState.urgency_level || null,
                    work_location: formState.work_location || null,
                    team_size_needed: formState.team_size_needed ? Number(formState.team_size_needed) : null,
                  };
                  updateClientNeed.mutate(payload);
                }}
                disabled={updateClientNeed.isPending}
              >
                {updateClientNeed.isPending ? "Saving..." : "Save Updates"}
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs uppercase text-muted-foreground">Client Name</label>
                <Input
                  value={formState.client_name}
                  onChange={(event) => setFormState((prev) => ({ ...prev, client_name: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Client Company</label>
                <Input
                  value={formState.client_company}
                  onChange={(event) => setFormState((prev) => ({ ...prev, client_company: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Client Email</label>
                <Input
                  value={formState.client_email}
                  onChange={(event) => setFormState((prev) => ({ ...prev, client_email: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Project Title</label>
                <Input
                  value={formState.project_title}
                  onChange={(event) => setFormState((prev) => ({ ...prev, project_title: event.target.value }))}
                />
              </div>
              <div className="md:col-span-2">
                <label className="text-xs uppercase text-muted-foreground">Project Description</label>
                <Textarea
                  className="min-h-[120px]"
                  value={formState.project_description}
                  onChange={(event) => setFormState((prev) => ({ ...prev, project_description: event.target.value }))}
                />
              </div>
              <div className="md:col-span-2">
                <label className="text-xs uppercase text-muted-foreground">Required Skills (comma separated)</label>
                <Input
                  value={formState.required_skills}
                  onChange={(event) => setFormState((prev) => ({ ...prev, required_skills: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Timeline (weeks)</label>
                <Input
                  value={formState.timeline_duration_weeks}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, timeline_duration_weeks: event.target.value }))
                  }
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Team Size Needed</label>
                <Input
                  value={formState.team_size_needed}
                  onChange={(event) => setFormState((prev) => ({ ...prev, team_size_needed: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Budget Min</label>
                <Input
                  value={formState.budget_min}
                  onChange={(event) => setFormState((prev) => ({ ...prev, budget_min: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Budget Max</label>
                <Input
                  value={formState.budget_max}
                  onChange={(event) => setFormState((prev) => ({ ...prev, budget_max: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Urgency Level</label>
                <Input
                  value={formState.urgency_level}
                  onChange={(event) => setFormState((prev) => ({ ...prev, urgency_level: event.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs uppercase text-muted-foreground">Work Location</label>
                <Input
                  value={formState.work_location}
                  onChange={(event) => setFormState((prev) => ({ ...prev, work_location: event.target.value }))}
                />
              </div>
            </div>
            {updateClientNeed.isError && (
              <p className="text-sm text-warning">Failed to update client need. Please review inputs.</p>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-border bg-card p-6 space-y-3 lg:col-span-2">
              <div className="flex items-center gap-3">
                <h4 className="text-xl font-semibold">{data.project_title || "Untitled Client Need"}</h4>
                {data.urgency_level && (
                  <Badge variant={data.urgency_level === "critical" ? "destructive" : "secondary"}>
                    {data.urgency_level}
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                {data.client_company || data.client_name || "Client details pending"}
              </p>
              <p className="text-sm text-muted-foreground">
                {data.project_description || "No description available yet."}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Completeness</p>
                <p className="text-2xl font-bold">{data.profile_completeness_score}%</p>
              </div>
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>Timeline: {data.timeline_duration_weeks ? `${data.timeline_duration_weeks} weeks` : "TBD"}</p>
                <p>
                  Budget:{" "}
                  {data.budget_min && data.budget_max
                    ? `$${data.budget_min} - $${data.budget_max} ${data.budget_currency || "USD"}`
                    : "TBD"}
                </p>
                <p>Work Location: {data.work_location || "TBD"}</p>
                <p>Team Size: {data.team_size_needed || "TBD"}</p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Required Skills</h4>
              <Badge variant="secondary">{requiredSkills.length}</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              {requiredSkills.length === 0 && (
                <p className="text-sm text-muted-foreground">No required skills captured yet.</p>
              )}
              {requiredSkills.map((skill) => (
                <Badge key={skill} variant="outline">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-lg font-semibold">Extracted Roles</h4>
            {roles.length === 0 && (
              <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
                No roles have been extracted yet for this client need.
              </div>
            )}
            <div className="grid grid-cols-1 gap-4">
              {roles.map((role, idx) => (
                <div key={`${role.category}-${idx}`} className="rounded-2xl border border-border bg-card p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Category</p>
                      <h5 className="text-lg font-semibold">{formatCategory(role.category)}</h5>
                    </div>
                    {role.count && <Badge variant="secondary">x{role.count}</Badge>}
                  </div>
                  <p className="text-sm text-muted-foreground mt-3">Evidence</p>
                  <p className="text-sm">{role.evidence}</p>
                  {role.description && (
                    <>
                      <p className="text-sm text-muted-foreground mt-3">Notes</p>
                      <p className="text-sm">{role.description}</p>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  );
}
