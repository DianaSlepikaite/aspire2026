import { Badge } from "@/components/ui/badge";
import { EditableTextareaField } from "@/components/layout/core/EditableTextareaField";

interface SummaryGoalsSectionProps {
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  summaryDraft: string;
  setSummaryDraft: (value: string) => void;
  goalsDraft: string;
  setGoalsDraft: (value: string) => void;
  strengthsDraft: string;
  setStrengthsDraft: (value: string) => void;
}

export function SummaryGoalsSection({
  editingField,
  setEditingField,
  summaryDraft,
  setSummaryDraft,
  goalsDraft,
  setGoalsDraft,
  strengthsDraft,
  setStrengthsDraft,
}: SummaryGoalsSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Summary & Goals</h4>
        <Badge variant="secondary">Editable</Badge>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="core-summary"
            id="core-summary-label"
            className="text-xs font-semibold text-muted-foreground uppercase"
          >
            Professional Summary
          </label>
          <EditableTextareaField
            field="summary"
            value={summaryDraft}
            placeholder="Professional summary"
            onChange={setSummaryDraft}
            editingField={editingField}
            setEditingField={setEditingField}
            className="min-h-[120px]"
            inputId="core-summary"
            labelId="core-summary-label"
            ariaLabel="Professional summary"
            describedById="core-editing-hint"
          />
        </div>
        <div>
          <label
            htmlFor="core-goals"
            id="core-goals-label"
            className="text-xs font-semibold text-muted-foreground uppercase"
          >
            Career Goals
          </label>
          <EditableTextareaField
            field="goals"
            value={goalsDraft}
            placeholder="Career goals"
            onChange={setGoalsDraft}
            editingField={editingField}
            setEditingField={setEditingField}
            className="min-h-[120px]"
            inputId="core-goals"
            labelId="core-goals-label"
            ariaLabel="Career goals"
            describedById="core-editing-hint"
          />
        </div>
      </div>
      <div>
        <label
          htmlFor="core-strengths"
          id="core-strengths-label"
          className="text-xs font-semibold text-muted-foreground uppercase"
        >
          Core Strengths
        </label>
        <EditableTextareaField
          field="strengths"
          value={strengthsDraft}
          placeholder="Core strengths"
          onChange={setStrengthsDraft}
          editingField={editingField}
          setEditingField={setEditingField}
          className="min-h-[90px]"
          inputId="core-strengths"
          labelId="core-strengths-label"
          ariaLabel="Core strengths"
          describedById="core-editing-hint"
        />
      </div>
    </div>
  );
}
