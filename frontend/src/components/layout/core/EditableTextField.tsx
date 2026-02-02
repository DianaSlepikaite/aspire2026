import { Input } from "@/components/ui/input";

interface EditableTextFieldProps {
  field: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  className?: string;
  displayClassName?: string;
  inputId?: string;
  labelId?: string;
  ariaLabel?: string;
  describedById?: string;
}

export function EditableTextField({
  field,
  value,
  placeholder,
  onChange,
  editingField,
  setEditingField,
  className,
  displayClassName,
  inputId,
  labelId,
  ariaLabel,
  describedById,
}: EditableTextFieldProps) {
  if (editingField === field) {
    return (
      <Input
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
      className={`min-h-[40px] w-full rounded-md border border-border px-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate ${displayClassName ?? ""}`}
      onClick={() => setEditingField(field)}
      title={value}
      aria-label={ariaLabel}
      aria-labelledby={labelId}
      aria-describedby={describedById}
    >
      {value || <span className="text-muted-foreground">{placeholder}</span>}
    </button>
  );
}
