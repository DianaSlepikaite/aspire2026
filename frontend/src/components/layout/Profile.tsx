import { useRef, useState } from "react";
import { Download, Eye, File, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CourseCard } from "@/components/cards/CourseCard";
import { ProfileCard, SkillAnalysisCard } from "@/components/cards/ProfileCard";
import { learningRecommendations } from "@/components/layout/learningData";
import { useDocuments } from "@/context/DocumentContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function Profile() {
  const { documents, addFiles } = useDocuments();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 5;

  function handleFileAction(doc: (typeof documents)[number]) {
    setSelectedDocId(doc.id);
    if (doc.file) {
      const url = URL.createObjectURL(doc.file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  }

  function closePreview() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setSelectedDocId(null);
  }

  const totalPages = Math.max(1, Math.ceil(documents.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const pagedDocuments = documents.slice(startIndex, startIndex + pageSize);
  const selectedDoc = documents.find((doc) => doc.id === selectedDocId) ?? null;

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
            name="Sarah Jenkins"
            role="Senior Project Manager"
            department="Staffing Tech Div."
            image="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face"
            skills={["Agile Leadership", "Data Visualization", "Stakeholder Mgmt", "Python", "SQL", "Team Building", "Scrum"]}
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
                addFiles(event.target.files, "profile");
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
                        <span className="font-medium block truncate max-w-[320px]" title={doc.name}>
                          {doc.name}
                        </span>
                        {doc.size && (
                          <p className="text-xs text-muted-foreground mt-1">{doc.size}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{doc.date}</td>
                  <td className="px-6 py-4 text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-muted-foreground hover:text-primary"
                      onClick={() => handleFileAction(doc)}
                    >
                      {doc.status === "Pending Review" ? <Eye className="size-4" /> : <Download className="size-4" />}
                    </Button>
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
            <DialogTitle>{selectedDoc?.name ?? "Document Preview"}</DialogTitle>
          </DialogHeader>
          {previewUrl ? (
            <iframe
              title={selectedDoc?.name ?? "Document Preview"}
              src={previewUrl}
              className="w-full h-[70vh] rounded-lg border border-border"
            />
          ) : (
            <div className="rounded-lg border border-border p-6 text-sm text-muted-foreground">
              Preview unavailable. Upload a file to view it here.
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
