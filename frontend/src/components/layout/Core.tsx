import { useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { useDocuments } from "@/context/DocumentContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Briefcase,
  Building2,
  Calendar,
  Eye,
  FileText,
  Github,
  Link2,
  Linkedin,
  Mail,
  MapPin,
  Pencil,
  Phone,
  RefreshCw,
  Trash2,
  Upload,
} from "lucide-react";

const coreProfile = {
  fullName: "Sarah Jenkins",
  title: "Senior Project Manager",
  department: "Staffing Tech Div.",
  manager: "Alicia Romero",
  location: "Austin, TX",
  email: "sarah.jenkins@aspire.io",
  phone: "+1 (512) 555-0184",
  startDate: "April 14, 2021",
  employmentType: "Full-time",
  summary:
    "Program leader focused on cross-functional delivery, portfolio health, and stakeholder alignment across enterprise initiatives.",
  strengths: "Agile delivery, executive reporting, risk mitigation, data storytelling, vendor management.",
  goals: "Move into Director-level program leadership within 18 months.",
  topSkills: ["Agile Leadership", "Data Visualization", "Stakeholder Mgmt", "Python", "SQL", "Team Building", "Scrum"],
  certifications: ["PMP (Active)", "CSM", "ICAgile ICP-APM"],
  education: [
    { school: "University of Texas at Austin", degree: "B.S. Information Systems", year: "2016" },
    { school: "Kellogg Executive Education", degree: "Leadership in Digital Transformation", year: "2022" },
  ],
  experienceHighlights: [
    "Led a $12M enterprise migration program, achieving 18% delivery acceleration.",
    "Standardized program reporting for 9 global teams, reducing status churn by 30%.",
    "Mentored 6 project leads and built succession plans for critical initiatives.",
  ],
};

const integrations = [
  {
    name: "LinkedIn",
    description: "Sync roles, endorsements, and profile summary.",
    icon: Linkedin,
    connected: true,
    handle: "linkedin.com/in/sarah-jenkins",
  },
  {
    name: "GitHub",
    description: "Pull repositories and contribution signals.",
    icon: Github,
    connected: false,
    handle: "github.com/sarahjenkins",
  },
  {
    name: "Portfolio",
    description: "External project showcase or personal site.",
    icon: Link2,
    connected: false,
    handle: "sarahjenkins.io",
  },
];

export default function Core() {
  const { documents, addFiles, removeDocument } = useDocuments();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 5;

  function handleFileAction(fileItem: (typeof documents)[number]) {
    setSelectedDocId(fileItem.id);
    if (fileItem.file) {
      const url = URL.createObjectURL(fileItem.file);
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
    <section className="space-y-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h3 className="text-2xl font-bold">Core Employee Profile</h3>
          <p className="text-muted-foreground mt-1">
            Synced from agent insights and enriched by your edits. Last sync: Jan 12, 2024.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" className="font-semibold">
            <RefreshCw className="size-4 mr-2" />
            Sync From Agent
          </Button>
          <Button className="font-semibold">Save Changes</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-2xl border border-border p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Personal & Contact</h4>
            <Badge variant="secondary">Editable</Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Full Name</label>
              <Input defaultValue={coreProfile.fullName} />
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Location</label>
              <div className="relative">
                <MapPin className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.location} />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Email</label>
              <div className="relative">
                <Mail className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.email} />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Phone</label>
              <div className="relative">
                <Phone className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.phone} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card rounded-2xl border border-border p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Role & Org</h4>
            <Badge variant="secondary">Editable</Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Title</label>
              <div className="relative">
                <Briefcase className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.title} />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Department</label>
              <div className="relative">
                <Building2 className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.department} />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Manager</label>
              <Input defaultValue={coreProfile.manager} />
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Start Date</label>
              <div className="relative">
                <Calendar className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <Input className="pl-9" defaultValue={coreProfile.startDate} />
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase">Employment Type</label>
              <Input defaultValue={coreProfile.employmentType} />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Summary & Goals</h4>
          <Badge variant="secondary">Editable</Badge>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Professional Summary</label>
            <Textarea defaultValue={coreProfile.summary} className="min-h-[120px]" />
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Career Goals</label>
            <Textarea defaultValue={coreProfile.goals} className="min-h-[120px]" />
          </div>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase">Core Strengths</label>
          <Textarea defaultValue={coreProfile.strengths} className="min-h-[90px]" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Skills & Certifications</h4>
            <Badge variant="secondary">Editable</Badge>
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Top Skills</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {coreProfile.topSkills.map((skill) => (
                <Badge key={skill} variant="outline">
                  {skill}
                </Badge>
              ))}
              <Button variant="ghost" size="sm" className="text-muted-foreground">
                <Pencil className="size-3 mr-2" />
                Edit Skills
              </Button>
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Certifications</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {coreProfile.certifications.map((cert) => (
                <Badge key={cert} variant="secondary">
                  {cert}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Education</h4>
            <Badge variant="secondary">Editable</Badge>
          </div>
          <div className="space-y-4">
            {coreProfile.education.map((item) => (
              <div key={item.degree} className="rounded-xl border border-border p-4 space-y-1">
                <p className="font-semibold">{item.school}</p>
                <p className="text-sm text-muted-foreground">{item.degree}</p>
                <p className="text-xs text-muted-foreground">{item.year}</p>
              </div>
            ))}
            <Button variant="outline" className="w-full font-semibold">
              Add Education
            </Button>
          </div>
        </div>
      </div>

      <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Experience Highlights</h4>
          <Badge variant="secondary">Editable</Badge>
        </div>
        <div className="space-y-3">
          {coreProfile.experienceHighlights.map((item, idx) => (
            <div key={idx} className="flex items-start gap-3 rounded-xl border border-border p-4">
              <span className="text-xs font-bold text-muted-foreground mt-1">0{idx + 1}</span>
              <p className="text-sm text-foreground">{item}</p>
            </div>
          ))}
          <Button variant="outline" className="w-full font-semibold">
            Add Highlight
          </Button>
        </div>
      </div>

      <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Context Files</h4>
          <div className="flex items-center gap-3">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(event) => {
                addFiles(event.target.files, "core");
                event.currentTarget.value = "";
              }}
            />
            <Button variant="outline" className="font-semibold" onClick={() => fileInputRef.current?.click()}>
              <Upload className="size-4 mr-2" />
              Upload File
            </Button>
          </div>
        </div>
        <div className="bg-card rounded-2xl border border-border overflow-hidden">
          <table className="w-full text-left table-fixed">
            <thead className="bg-secondary/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-2/5">Document Name</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/5">Type</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase w-1/5">Updated</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase text-right w-1/5">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {pagedDocuments.map((fileItem) => (
                <tr key={fileItem.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <FileText className="size-4 text-muted-foreground" />
                      <div>
                        <span className="font-medium block truncate max-w-[260px]" title={fileItem.name}>
                          {fileItem.name}
                        </span>
                        {fileItem.size && (
                          <p className="text-xs text-muted-foreground mt-1">{fileItem.size}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{fileItem.type ?? "Document"}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{fileItem.date}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:text-primary"
                        onClick={() => handleFileAction(fileItem)}
                      >
                        <Eye className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:text-primary"
                        onClick={() => removeDocument(fileItem.id)}
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
      </div>

      <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Integrations</h4>
          <Badge variant="secondary">Manage</Badge>
        </div>
        <div className="space-y-3">
          {integrations.map((integration) => (
            <div key={integration.name} className="rounded-xl border border-border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-xl bg-secondary flex items-center justify-center">
                    <integration.icon className="size-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-semibold">{integration.name}</p>
                    <p className="text-xs text-muted-foreground">{integration.description}</p>
                  </div>
                </div>
                <Switch defaultChecked={integration.connected} />
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center gap-2">
                  <Link2 className="size-3" />
                  {integration.handle}
                </span>
                <Button variant="ghost" size="sm" className="text-muted-foreground">
                  {integration.connected ? "Disconnect" : "Connect"}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
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
    </section>
  );
}
