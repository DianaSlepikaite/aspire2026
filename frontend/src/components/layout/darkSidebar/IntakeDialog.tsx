import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface IntakeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  clientName: string;
  clientEmail: string;
  briefText: string;
  intakeFile: File | null;
  statusMessage: string | null;
  statusIsError: boolean;
  isSubmitting: boolean;
  onClientNameChange: (value: string) => void;
  onClientEmailChange: (value: string) => void;
  onBriefTextChange: (value: string) => void;
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
}

export function IntakeDialog({
  open,
  onOpenChange,
  clientName,
  clientEmail,
  briefText,
  intakeFile,
  statusMessage,
  statusIsError,
  isSubmitting,
  onClientNameChange,
  onClientEmailChange,
  onBriefTextChange,
  onFileChange,
  onSubmit,
}: IntakeDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Client Need Intake</DialogTitle>
          <DialogDescription>
            Upload a brief or paste requirements to create a client need.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-1 gap-3">
          <Input
            placeholder="Client name (optional)"
            value={clientName}
            onChange={(event) => onClientNameChange(event.target.value)}
            aria-label="Client name"
            aria-describedby={statusMessage ? "intake-status" : undefined}
            aria-invalid={statusIsError}
          />
          <Input
            placeholder="Client email (optional)"
            value={clientEmail}
            onChange={(event) => onClientEmailChange(event.target.value)}
            aria-label="Client email"
            aria-describedby={statusMessage ? "intake-status" : undefined}
            aria-invalid={statusIsError}
          />
          <Textarea
            className="min-h-[140px]"
            placeholder="Paste the project brief or key requirements..."
            value={briefText}
            onChange={(event) => onBriefTextChange(event.target.value)}
            aria-label="Project brief"
            aria-describedby={statusMessage ? "intake-status" : undefined}
            aria-invalid={statusIsError}
          />
          <Input
            type="file"
            accept=".pdf,.wav,.mp3,.ogg,.m4a"
            onChange={(event) => {
              const file = event.target.files?.[0] || null;
              onFileChange(file);
            }}
            aria-label="Upload brief file"
            aria-describedby={statusMessage ? "intake-status" : undefined}
            aria-invalid={statusIsError}
          />
          {intakeFile && (
            <p className="text-xs text-muted-foreground">Selected file: {intakeFile.name}</p>
          )}
        </div>
        {statusMessage && (
          <p
            id="intake-status"
            className="text-xs text-muted-foreground"
            role={statusIsError ? "alert" : "status"}
            aria-live={statusIsError ? "assertive" : "polite"}
          >
            {statusMessage}
          </p>
        )}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={isSubmitting}>
            {isSubmitting ? "Processing Intake..." : "Process Client Need"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
