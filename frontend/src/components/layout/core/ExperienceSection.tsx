import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ExperienceSectionProps {
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  pagedExperience: string[];
  experienceStart: number;
  updateExperienceItem: (index: number, value: string) => void;
  removeExperienceItem: (index: number) => void;
  addExperienceItem: () => void;
  safeExperiencePage: number;
  experienceTotalPages: number;
  setExperiencePage: (updater: (prev: number) => number) => void;
}

export function ExperienceSection({
  editingField,
  setEditingField,
  pagedExperience,
  experienceStart,
  updateExperienceItem,
  removeExperienceItem,
  addExperienceItem,
  safeExperiencePage,
  experienceTotalPages,
  setExperiencePage,
}: ExperienceSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Experience Highlights</h4>
        <Badge variant="secondary">Editable</Badge>
      </div>
      <div className="space-y-3">
        {pagedExperience.map((item, localIdx) => {
          const idx = experienceStart + localIdx;
          const key = `experience-${idx}`;
          return (
            <div key={key} className="flex items-start gap-3 rounded-xl border border-border p-4">
              <span className="text-xs font-bold text-muted-foreground mt-1">0{idx + 1}</span>
              <div className="flex-1 space-y-2">
                {editingField === key ? (
                  <>
                    <Textarea
                      value={item}
                      onChange={(event) => updateExperienceItem(idx, event.target.value)}
                      className="min-h-[90px]"
                      onBlur={() => setEditingField(null)}
                      aria-label={`Experience highlight ${idx + 1}`}
                    />
                    <div className="flex justify-between">
                      <Button variant="ghost" size="sm" onClick={() => removeExperienceItem(idx)}>
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
                    className="min-h-[90px] w-full rounded-md border border-border px-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors whitespace-pre-wrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    onClick={() => setEditingField(key)}
                    aria-label={`Edit experience highlight ${idx + 1}`}
                  >
                    {item || <span className="text-muted-foreground">Click to add highlight</span>}
                  </button>
                )}
              </div>
            </div>
          );
        })}
        <Button variant="outline" className="w-full font-semibold" onClick={addExperienceItem}>
          Add Highlight
        </Button>
        {experienceTotalPages > 1 && (
          <div className="flex items-center justify-between">
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={() => setExperiencePage((prev) => Math.max(1, prev - 1))}
              disabled={safeExperiencePage === 1}
            >
              Previous
            </Button>
            <span className="text-xs text-muted-foreground">
              Page {safeExperiencePage} of {experienceTotalPages}
            </span>
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={() => setExperiencePage((prev) => Math.min(experienceTotalPages, prev + 1))}
              disabled={safeExperiencePage === experienceTotalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
