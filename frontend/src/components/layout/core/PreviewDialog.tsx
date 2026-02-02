import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface PreviewDialogProps {
  open: boolean;
  fileName?: string | null;
  previewText?: string | null;
  onClose: () => void;
}

export function PreviewDialog({ open, fileName, previewText, onClose }: PreviewDialogProps) {
  return (
    <Dialog open={open} onOpenChange={(nextOpen) => !nextOpen && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>{fileName ?? "Document Preview"}</DialogTitle>
          <DialogDescription>
            Preview the document contents. Press Escape to close.
          </DialogDescription>
        </DialogHeader>
        <div className="rounded-lg border border-border p-6 text-sm text-muted-foreground max-h-[70vh] overflow-auto whitespace-pre-wrap">
          {previewText
            ? previewText
            : "Preview unavailable. This document does not have extracted text yet."}
        </div>
      </DialogContent>
    </Dialog>
  );
}
