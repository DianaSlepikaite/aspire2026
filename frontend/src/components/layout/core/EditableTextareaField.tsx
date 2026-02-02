import { Textarea } from "@/components/ui/textarea";

interface EditableTextareaFieldProps {
  field: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  className?: string;
  inputId?: string;
  labelId?: string;
  ariaLabel?: string;
  describedById?: string;
}

export function EditableTextareaField({
  field,
  value,
  placeholder,
  onChange,
  editingField,
  setEditingField,
  className,
  inputId,
  labelId,
  ariaLabel,
  describedById,
}: EditableTextareaFieldProps) {
  if (editingField === field) {
    return (
      <Textarea
        id={inputId}
        className={className}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onBlur={() => setEditingField(null)}
        aria-label={ariaLabel}
        aria-labelledby={labelId}
        aria-describedby={describedById}
      />
    );
  }

  return (
    <button
      type="button"
      className="min-h-[96px] w-full rounded-md border border-border px-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors whitespace-pre-wrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      onClick={() => setEditingField(field)}
      aria-label={ariaLabel}
      aria-labelledby={labelId}
      aria-describedby={describedById}
    >
      {value || <span className="text-muted-foreground">{placeholder}</span>}
    </button>
  );
}
