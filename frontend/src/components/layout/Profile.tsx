import { useRef, useState } from "react";
import { Eye, File, Trash2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CourseCard } from "@/components/cards/CourseCard";
import { ProfileCard, SkillAnalysisCard } from "@/components/cards/ProfileCard";
import { learningRecommendations } from "@/components/layout/learningData";
import {
  useEmployeeDocuments,
  useEmployeeProfile,
  useEmployeeUpload,
  useEmployeeDocumentDelete,
} from "@/hooks/useEmployee";
import { useQueryClient } from "@tanstack/react-query";
import { useEmployeeContext } from "@/context/EmployeeContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function Profile() {
  const { employeeProfileId, setEmployeeProfileId, conversationId } = useEmployeeContext();
  const { data: profile } = useEmployeeProfile(employeeProfileId);
  const { data: documents = [] } = useEmployeeDocuments(employeeProfileId);
  const uploadMutation = useEmployeeUpload();
  const deleteMutation = useEmployeeDocumentDelete();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [previewText, setPreviewText] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 5;

  function handleFileAction(doc: (typeof documents)[number]) {
    setSelectedDocId(doc.id);
    setPreviewText(doc.raw_text ?? null);
  }

  function closePreview() {
    setPreviewText(null);
    setSelectedDocId(null);
  }

  const totalPages = Math.max(1, Math.ceil(documents.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const pagedDocuments = documents.slice(startIndex, startIndex + pageSize);
  const selectedDoc = documents.find((doc) => doc.id === selectedDocId) ?? null;
  const skills = profile?.skills ?? [];
  const preferredRole = profile?.preferred_roles?.[0] ?? "Role not set";

  return (
    <>
      <section>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold">Your Overview</h3>
          <Button variant="link" className="text-primary font-semibold">
            Edit Profile
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ProfileCard
            name={profile?.full_name ?? "Career Profile"}
            role={preferredRole}
            department="Career Track"
            image="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face"
            skills={skills.length > 0 ? skills : ["Add skills to build your profile"]}
            verified
          />
          <SkillAnalysisCard skillName="Python" progress={72} improvement={15} />
        </div>
      </section>

      {/* Learning Recommendations */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold">Recommended Learning</h3>
          <Button variant="link" className="text-primary font-semibold">
            Explore Catalog
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {learningRecommendations.map((course, idx) => (
            <CourseCard key={idx} {...course} />
          ))}
        </div>
      </section>

      {/* Documents Section */}
      <section className="pb-20">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold">Recent Documents</h3>
          <div className="flex items-center gap-3">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (!file) return;
                uploadMutation
                  .mutateAsync({
                    file,
                    employeeProfileId,
                    conversationId,
                  })
                  .then((result) => {
                    if (result.employee_profile_id) {
                      setEmployeeProfileId(result.employee_profile_id);
                      queryClient.invalidateQueries({ queryKey: ["employee-profile", result.employee_profile_id] });
                      queryClient.invalidateQueries({ queryKey: ["employee-documents", result.employee_profile_id] });
                    }
                  })
                  .catch(() => {
                    // noop; UI will remain unchanged on failure
                  });
                event.currentTarget.value = "";
              }}
            />
            <Button
              variant="link"
              className="text-primary font-semibold flex items-center gap-1"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="size-4" />
              Upload New
            </Button>
          </div>
        </div>
        <div className="bg-card rounded-2xl shadow-sm border border-border overflow-hidden">
          <table className="w-full text-left table-fixed">
            <thead className="bg-secondary/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-3/5">Document Name</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/5">Upload Date</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase text-right w-1/5">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {pagedDocuments.map((doc) => {
                return (
                <tr key={doc.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <File className="size-4 text-muted-foreground" />
                      <div>
                        <span className="font-medium block truncate max-w-[320px]" title={doc.file_name ?? ""}>
                          {doc.file_name ?? "Untitled document"}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">
                    {new Date(doc.created_at).toLocaleDateString("en-US", {
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
                      onClick={() => handleFileAction(doc)}
                      aria-label={`View ${doc.file_name ?? "document"}`}
                    >
                      <Eye className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-muted-foreground hover:text-primary"
                      onClick={() => {
                        deleteMutation
                          .mutateAsync({ documentId: doc.id })
                          .then(() => {
                            if (employeeProfileId) {
                              queryClient.invalidateQueries({
                                queryKey: ["employee-documents", employeeProfileId],
                              });
                            }
                          })
                          .catch(() => {
                            // noop
                          });
                      }}
                      aria-label={`Delete ${doc.file_name ?? "document"}`}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                    </div>
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
          <div className="bg-secondary/50 p-4 text-center">
            <div className="flex items-center justify-between">
              <Button
                variant="link"
                className="text-sm font-bold text-muted-foreground hover:text-foreground"
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
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
                onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={safePage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      </section>
      <Dialog open={Boolean(selectedDocId)} onOpenChange={(open) => !open && closePreview()}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{selectedDoc?.file_name ?? "Document Preview"}</DialogTitle>
          </DialogHeader>
          <div className="rounded-lg border border-border p-6 text-sm text-muted-foreground max-h-[70vh] overflow-auto whitespace-pre-wrap">
            {previewText
              ? previewText
              : "Preview unavailable. This document does not have extracted text yet."}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
