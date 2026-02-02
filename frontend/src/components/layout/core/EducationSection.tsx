import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { EducationItem } from "@/hooks/useCoreProfile";

interface EducationSectionProps {
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  pagedEducation: EducationItem[];
  educationStart: number;
  updateEducationItem: (index: number, field: keyof EducationItem, value: string) => void;
  removeEducationItem: (index: number) => void;
  addEducationItem: () => void;
  safeEducationPage: number;
  educationTotalPages: number;
  setEducationPage: (updater: (prev: number) => number) => void;
}

export function EducationSection({
  editingField,
  setEditingField,
  pagedEducation,
  educationStart,
  updateEducationItem,
  removeEducationItem,
  addEducationItem,
  safeEducationPage,
  educationTotalPages,
  setEducationPage,
}: EducationSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Education</h4>
        <Badge variant="secondary">Editable</Badge>
      </div>
      <div className="space-y-4">
        {pagedEducation.map((item, localIdx) => {
          const idx = educationStart + localIdx;
          const key = `education-${idx}`;
          const label = [item.degree, item.school, item.year].filter(Boolean).join(" • ");
          return (
            <div key={key} className="rounded-xl border border-border p-4 space-y-2">
              {editingField === key ? (
                <>
                  <Input
                    placeholder="School"
                    value={item.school}
                    onChange={(event) => updateEducationItem(idx, "school", event.target.value)}
                    onBlur={() => setEditingField(null)}
                    aria-label="School"
                  />
                  <Input
                    placeholder="Degree"
                    value={item.degree}
                    onChange={(event) => updateEducationItem(idx, "degree", event.target.value)}
                    aria-label="Degree"
                  />
                  <Input
                    placeholder="Year"
                    value={item.year}
                    onChange={(event) => updateEducationItem(idx, "year", event.target.value)}
                    aria-label="Year"
                  />
                  <div className="flex justify-between">
                    <Button variant="ghost" size="sm" onClick={() => removeEducationItem(idx)}>
                      Remove
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setEditingField(null)}>
                      Done
                    </Button>
                  </div>
                </>
              ) : (
                <button
                  type="button"
                  className="min-h-[64px] w-full rounded-md border border-border px-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors whitespace-pre-wrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  onClick={() => setEditingField(key)}
                  aria-label={`Edit education entry ${idx + 1}`}
                >
                  {label || <span className="text-muted-foreground">Click to add education</span>}
                </button>
              )}
            </div>
          );
        })}
        <Button variant="outline" className="w-full font-semibold" onClick={addEducationItem}>
          Add Education
        </Button>
        {educationTotalPages > 1 && (
          <div className="flex items-center justify-between">
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={() => setEducationPage((prev) => Math.max(1, prev - 1))}
              disabled={safeEducationPage === 1}
            >
              Previous
            </Button>
            <span className="text-xs text-muted-foreground">
              Page {safeEducationPage} of {educationTotalPages}
            </span>
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={() => setEducationPage((prev) => Math.min(educationTotalPages, prev + 1))}
              disabled={safeEducationPage === educationTotalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
