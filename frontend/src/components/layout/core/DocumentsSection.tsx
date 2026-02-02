import { RefObject } from "react";
import { Button } from "@/components/ui/button";
import { Eye, FileText, Trash2, Upload } from "lucide-react";

interface DocumentsSectionProps {
  fileInputRef: RefObject<HTMLInputElement>;
  pagedDocuments: Array<{
    id: string;
    file_name?: string | null;
    mime_type?: string | null;
    created_at: string;
  }>;
  safePage: number;
  totalPages: number;
  onUploadClick: () => void;
  onUploadFile: (file: File) => void;
  onView: (document: DocumentsSectionProps["pagedDocuments"][number]) => void;
  onDelete: (documentId: string) => void;
  onPrevPage: () => void;
  onNextPage: () => void;
}

export function DocumentsSection({
  fileInputRef,
  pagedDocuments,
  safePage,
  totalPages,
  onUploadClick,
  onUploadFile,
  onView,
  onDelete,
  onPrevPage,
  onNextPage,
}: DocumentsSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Context Files</h4>
        <div className="flex items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            aria-label="Upload document"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (!file) return;
              onUploadFile(file);
              event.currentTarget.value = "";
            }}
          />
          <Button variant="outline" className="font-semibold" onClick={onUploadClick}>
            <Upload className="size-4 mr-2" />
            Upload File
          </Button>
        </div>
      </div>
      <div className="bg-card rounded-2xl border border-border overflow-hidden">
        <table className="w-full text-left table-fixed">
          <thead className="bg-secondary/50 border-b border-border">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/2">Document Name</th>
              <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/6">Type</th>
              <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/6">Updated</th>
              <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase text-right w-1/6">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {pagedDocuments.map((fileItem) => (
              <tr key={fileItem.id} className="hover:bg-secondary/30 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <FileText className="size-4 text-muted-foreground" />
                    <div>
                      <span className="font-medium block truncate max-w-[260px]" title={fileItem.file_name ?? ""}>
                        {fileItem.file_name ?? "Untitled document"}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  <span className="block truncate max-w-[140px]" title={fileItem.mime_type ?? ""}>
                    {fileItem.mime_type ?? "Document"}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  {new Date(fileItem.created_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "2-digit",
                    year: "numeric",
                  })}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-muted-foreground hover:text-primary"
                      onClick={() => onView(fileItem)}
                      aria-label={`View ${fileItem.file_name ?? "document"}`}
                    >
                      <Eye className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-muted-foreground hover:text-primary"
                      onClick={() => onDelete(fileItem.id)}
                      aria-label={`Delete ${fileItem.file_name ?? "document"}`}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="bg-secondary/50 p-4 text-center">
          <div className="flex items-center justify-between">
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={onPrevPage}
              disabled={safePage === 1}
            >
              Previous
            </Button>
            <span className="text-xs text-muted-foreground">
              Page {safePage} of {totalPages}
            </span>
            <Button
              variant="link"
              className="text-sm font-bold text-muted-foreground hover:text-foreground"
              onClick={onNextPage}
              disabled={safePage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
