import { useEffect, useMemo, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  useEmployeeDocuments,
  useEmployeeProfile,
  useEmployeeUpload,
  useEmployeeProfileUpdate,
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
  Plus,
  Phone,
  RefreshCw,
  Trash2,
  Upload,
  X,
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

type EducationItem = {
  school: string;
  degree: string;
  year: string;
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
  const { employeeProfileId, setEmployeeProfileId, conversationId } = useEmployeeContext();
  const { data: profile } = useEmployeeProfile(employeeProfileId);
  const { data: documents = [] } = useEmployeeDocuments(employeeProfileId);
  const uploadMutation = useEmployeeUpload();
  const profileUpdateMutation = useEmployeeProfileUpdate();
  const documentDeleteMutation = useEmployeeDocumentDelete();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [previewText, setPreviewText] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [educationPage, setEducationPage] = useState(1);
  const [experiencePage, setExperiencePage] = useState(1);
  const [skillsDraft, setSkillsDraft] = useState<string[]>([]);
  const [certificationsDraft, setCertificationsDraft] = useState<string[]>([]);
  const [educationDraft, setEducationDraft] = useState<EducationItem[]>([]);
  const [experienceDraft, setExperienceDraft] = useState<string[]>([]);
  const [fullNameDraft, setFullNameDraft] = useState("");
  const [emailDraft, setEmailDraft] = useState("");
  const [phoneDraft, setPhoneDraft] = useState("");
  const [summaryDraft, setSummaryDraft] = useState("");
  const [titleDraft, setTitleDraft] = useState("");
  const [departmentDraft, setDepartmentDraft] = useState("");
  const [managerDraft, setManagerDraft] = useState("");
  const [locationDraft, setLocationDraft] = useState("");
  const [startDateDraft, setStartDateDraft] = useState("");
  const [employmentTypeDraft, setEmploymentTypeDraft] = useState("");
  const [strengthsDraft, setStrengthsDraft] = useState("");
  const [goalsDraft, setGoalsDraft] = useState("");
  const [skillInput, setSkillInput] = useState("");
  const [certInput, setCertInput] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [editingField, setEditingField] = useState<string | null>(null);
  const pageSize = 5;
  const listPageSize = 5;

  const coreTags = useMemo(() => {
    const tags = profile?.tags ?? {};
    const coreTag = (tags as Record<string, unknown>)?.core_profile;
    return (coreTag && typeof coreTag === "object" ? (coreTag as Record<string, unknown>) : {}) as Record<string, unknown>;
  }, [profile?.tags]);

  const displayProfile = {
    fullName: profile?.full_name ?? coreProfile.fullName,
    email: profile?.email ?? coreProfile.email,
    phone: profile?.phone ?? coreProfile.phone,
    summary: profile?.summary ?? coreProfile.summary,
    skills: profile?.skills ?? coreProfile.topSkills,
    certifications: profile?.certifications ?? coreProfile.certifications,
    education: profile?.education ?? coreProfile.education,
    experience: profile?.experience ?? coreProfile.experienceHighlights,
    title: (coreTags.title as string | undefined) ?? coreProfile.title,
    department: (coreTags.department as string | undefined) ?? coreProfile.department,
    manager: (coreTags.manager as string | undefined) ?? coreProfile.manager,
    location: (coreTags.location as string | undefined) ?? coreProfile.location,
    startDate: (coreTags.startDate as string | undefined) ?? coreProfile.startDate,
    employmentType: (coreTags.employmentType as string | undefined) ?? coreProfile.employmentType,
    strengths: (coreTags.strengths as string | undefined) ?? coreProfile.strengths,
    goals: (coreTags.goals as string | undefined) ?? coreProfile.goals,
  };

  function handleFileAction(fileItem: (typeof documents)[number]) {
    setSelectedDocId(fileItem.id);
    setPreviewText(fileItem.raw_text ?? null);
  }

  function closePreview() {
    setPreviewText(null);
    setSelectedDocId(null);
  }

  useEffect(() => {
    const nextSkills = Array.isArray(displayProfile.skills)
      ? displayProfile.skills.filter(Boolean)
      : [];
    setSkillsDraft(nextSkills);
    const nextCerts = Array.isArray(displayProfile.certifications)
      ? displayProfile.certifications.filter(Boolean)
      : [];
    setCertificationsDraft(nextCerts);
    const nextEdu = Array.isArray(displayProfile.education)
      ? displayProfile.education.map((item) => ({
          school: String((item as any)?.school ?? ""),
          degree: String((item as any)?.degree ?? ""),
          year: String((item as any)?.year ?? ""),
        }))
      : [];
    setEducationDraft(nextEdu);
    const nextExperience = Array.isArray(displayProfile.experience)
      ? displayProfile.experience.map((item) =>
          typeof item === "string" ? item : formatExperienceItem(item)
        )
      : [];
    setExperienceDraft(nextExperience);
    setFullNameDraft(displayProfile.fullName ?? "");
    setEmailDraft(displayProfile.email ?? "");
    setPhoneDraft(displayProfile.phone ?? "");
    setSummaryDraft(displayProfile.summary ?? "");
    setTitleDraft(displayProfile.title ?? "");
    setDepartmentDraft(displayProfile.department ?? "");
    setManagerDraft(displayProfile.manager ?? "");
    setLocationDraft(displayProfile.location ?? "");
    setStartDateDraft(displayProfile.startDate ?? "");
    setEmploymentTypeDraft(displayProfile.employmentType ?? "");
    setStrengthsDraft(displayProfile.strengths ?? "");
    setGoalsDraft(displayProfile.goals ?? "");
  }, [
    displayProfile.skills,
    displayProfile.certifications,
    displayProfile.education,
    displayProfile.experience,
    displayProfile.fullName,
    displayProfile.email,
    displayProfile.phone,
    displayProfile.summary,
    displayProfile.title,
    displayProfile.department,
    displayProfile.manager,
    displayProfile.location,
    displayProfile.startDate,
    displayProfile.employmentType,
    displayProfile.strengths,
    displayProfile.goals,
  ]);

  function addSkill() {
    const value = skillInput.trim();
    if (!value) return;
    if (skillsDraft.some((skill) => skill.toLowerCase() === value.toLowerCase())) {
      setSkillInput("");
      return;
    }
    setSkillsDraft((prev) => [...prev, value]);
    setSkillInput("");
  }

  function removeSkill(skill: string) {
    setSkillsDraft((prev) => prev.filter((item) => item !== skill));
  }

  function addCertification() {
    const value = certInput.trim();
    if (!value) return;
    if (certificationsDraft.some((cert) => cert.toLowerCase() === value.toLowerCase())) {
      setCertInput("");
      return;
    }
    setCertificationsDraft((prev) => [...prev, value]);
    setCertInput("");
  }

  function removeCertification(cert: string) {
    setCertificationsDraft((prev) => prev.filter((item) => item !== cert));
  }

  function updateEducationItem(index: number, field: keyof EducationItem, value: string) {
    setEducationDraft((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, [field]: value } : item))
    );
  }

  function addEducationItem() {
    setEducationDraft((prev) => [...prev, { school: "", degree: "", year: "" }]);
    setEducationPage((prev) => Math.max(prev, Math.ceil((educationDraft.length + 1) / listPageSize)));
  }

  function removeEducationItem(index: number) {
    setEducationDraft((prev) => prev.filter((_, idx) => idx !== index));
    setEducationPage((prev) => Math.max(1, Math.min(prev, Math.ceil((educationDraft.length - 1) / listPageSize))));
  }

  function updateExperienceItem(index: number, value: string) {
    setExperienceDraft((prev) => prev.map((item, idx) => (idx === index ? value : item)));
  }

  function addExperienceItem() {
    setExperienceDraft((prev) => [...prev, ""]);
    setExperiencePage((prev) => Math.max(prev, Math.ceil((experienceDraft.length + 1) / listPageSize)));
  }

  function removeExperienceItem(index: number) {
    setExperienceDraft((prev) => prev.filter((_, idx) => idx !== index));
    setExperiencePage((prev) => Math.max(1, Math.min(prev, Math.ceil((experienceDraft.length - 1) / listPageSize))));
  }

  async function handleSaveChanges() {
    if (!employeeProfileId) return;
    setIsSaving(true);
    try {
      const existingTags = (profile?.tags && typeof profile.tags === "object")
        ? (profile.tags as Record<string, unknown>)
        : {};
      const updatedTags = {
        ...existingTags,
        core_profile: {
          title: titleDraft,
          department: departmentDraft,
          manager: managerDraft,
          location: locationDraft,
          startDate: startDateDraft,
          employmentType: employmentTypeDraft,
          strengths: strengthsDraft,
          goals: goalsDraft,
        },
      };
      await profileUpdateMutation.mutateAsync({
        profileId: employeeProfileId,
        payload: {
          full_name: fullNameDraft || null,
          email: emailDraft || null,
          phone: phoneDraft || null,
          summary: summaryDraft || null,
          skills: skillsDraft,
          certifications: certificationsDraft,
          education: educationDraft.filter((item) => item.school || item.degree || item.year),
          experience: experienceDraft
            .filter(Boolean)
            .map((item) => ({ description: item })),
          tags: updatedTags,
        },
      });
      queryClient.invalidateQueries({ queryKey: ["employee-profile", employeeProfileId] });
    } finally {
      setIsSaving(false);
    }
  }

  function formatExperienceItem(item: unknown) {
    if (typeof item === "string") return item;
    if (item && typeof item === "object") {
      const record = item as Record<string, unknown>;
      const title = String(record.title ?? "").trim();
      const company = String(record.company ?? "").trim();
      const years = String(record.years ?? "").trim();
      const description = String(record.description ?? "").trim();
      const headerParts = [title, company].filter(Boolean).join(" — ");
      const metaParts = [years].filter(Boolean).join(" ");
      return [headerParts, metaParts, description].filter(Boolean).join(" • ");
    }
    return "";
  }

  function renderEditableText(opts: {
    field: string;
    value: string;
    placeholder?: string;
    onChange: (value: string) => void;
    className?: string;
    displayClassName?: string;
  }) {
    const { field, value, placeholder, onChange, className, displayClassName } = opts;
    if (editingField === field) {
      return (
        <Input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onBlur={() => setEditingField(null)}
          autoFocus
          className={className}
        />
      );
    }
    return (
      <div
        className={`min-h-[40px] rounded-md border border-border px-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate ${
          displayClassName ?? ""
        }`}
        onClick={() => setEditingField(field)}
        title={value}
      >
        {value || <span className="text-muted-foreground">{placeholder ?? "Click to edit"}</span>}
      </div>
    );
  }

  function renderEditableTextarea(opts: {
    field: string;
    value: string;
    placeholder?: string;
    onChange: (value: string) => void;
    className?: string;
    displayClassName?: string;
  }) {
    const { field, value, placeholder, onChange, className, displayClassName } = opts;
    if (editingField === field) {
      return (
        <Textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onBlur={() => setEditingField(null)}
          autoFocus
          className={className}
        />
      );
    }
    return (
      <div
        className={`min-h-[120px] rounded-md border border-border px-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors whitespace-pre-wrap ${
          displayClassName ?? ""
        }`}
        onClick={() => setEditingField(field)}
        title={value}
      >
        {value || <span className="text-muted-foreground">{placeholder ?? "Click to edit"}</span>}
      </div>
    );
  }

  const lastSyncLabel = useMemo(() => {
    if (!profile?.updated_at) return "Last sync: --";
    const date = new Date(profile.updated_at);
    if (Number.isNaN(date.getTime())) return "Last sync: --";
    return `Last sync: ${date.toLocaleDateString("en-US", {
      month: "short",
      day: "2-digit",
      year: "numeric",
    })}`;
  }, [profile?.updated_at]);

  const totalPages = Math.max(1, Math.ceil(documents.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const pagedDocuments = documents.slice(startIndex, startIndex + pageSize);
  const selectedDoc = documents.find((doc) => doc.id === selectedDocId) ?? null;

  const educationTotalPages = Math.max(1, Math.ceil(educationDraft.length / listPageSize));
  const safeEducationPage = Math.min(educationPage, educationTotalPages);
  const educationStart = (safeEducationPage - 1) * listPageSize;
  const pagedEducation = educationDraft.slice(educationStart, educationStart + listPageSize);

  const experienceTotalPages = Math.max(1, Math.ceil(experienceDraft.length / listPageSize));
  const safeExperiencePage = Math.min(experiencePage, experienceTotalPages);
  const experienceStart = (safeExperiencePage - 1) * listPageSize;
  const pagedExperience = experienceDraft.slice(experienceStart, experienceStart + listPageSize);

  return (
    <section className="space-y-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h3 className="text-2xl font-bold">Core Employee Profile</h3>
          <p className="text-muted-foreground mt-1">
            Synced from agent insights and enriched by your edits. {lastSyncLabel}.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            className="font-semibold"
            onClick={() => {
              if (employeeProfileId) {
                queryClient.invalidateQueries({ queryKey: ["employee-profile", employeeProfileId] });
              }
            }}
          >
            <RefreshCw className="size-4 mr-2" />
            Sync From Agent
          </Button>
          <Button className="font-semibold" onClick={handleSaveChanges} disabled={isSaving || !employeeProfileId}>
            {isSaving ? "Saving..." : "Save Changes"}
          </Button>
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
                {renderEditableText({
                  field: "full_name",
                  value: fullNameDraft,
                  placeholder: "Full name",
                  onChange: setFullNameDraft,
                  displayClassName: "max-w-full",
                })}
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Location</label>
              <div className="relative">
                <MapPin className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                {editingField === "location" ? (
                  <Input
                    className="pl-9"
                    value={locationDraft}
                    onChange={(event) => setLocationDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("location")}
                    title={locationDraft}
                  >
                    {locationDraft || <span className="text-muted-foreground">Location</span>}
                  </div>
                )}
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Email</label>
              <div className="relative">
                <Mail className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                {editingField === "email" ? (
                  <Input
                    className="pl-9"
                    value={emailDraft}
                    onChange={(event) => setEmailDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("email")}
                    title={emailDraft}
                  >
                    {emailDraft || <span className="text-muted-foreground">Email</span>}
                  </div>
                )}
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Phone</label>
              <div className="relative">
                <Phone className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                {editingField === "phone" ? (
                  <Input
                    className="pl-9"
                    value={phoneDraft}
                    onChange={(event) => setPhoneDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("phone")}
                    title={phoneDraft}
                  >
                    {phoneDraft || <span className="text-muted-foreground">Phone</span>}
                  </div>
                )}
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
                {editingField === "title" ? (
                  <Input
                    className="pl-9"
                    value={titleDraft}
                    onChange={(event) => setTitleDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("title")}
                    title={titleDraft}
                  >
                    {titleDraft || <span className="text-muted-foreground">Title</span>}
                  </div>
                )}
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Department</label>
              <div className="relative">
                <Building2 className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                {editingField === "department" ? (
                  <Input
                    className="pl-9"
                    value={departmentDraft}
                    onChange={(event) => setDepartmentDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("department")}
                    title={departmentDraft}
                  >
                    {departmentDraft || <span className="text-muted-foreground">Department</span>}
                  </div>
                )}
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Manager</label>
            {renderEditableText({
              field: "manager",
              value: managerDraft,
              placeholder: "Manager",
              onChange: setManagerDraft,
            })}
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase">Start Date</label>
              <div className="relative">
                <Calendar className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                {editingField === "startDate" ? (
                  <Input
                    className="pl-9"
                    value={startDateDraft}
                    onChange={(event) => setStartDateDraft(event.target.value)}
                    onBlur={() => setEditingField(null)}
                    autoFocus
                  />
                ) : (
                  <div
                    className="min-h-[40px] rounded-md border border-border pl-9 pr-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors truncate"
                    onClick={() => setEditingField("startDate")}
                    title={startDateDraft}
                  >
                    {startDateDraft || <span className="text-muted-foreground">Start date</span>}
                  </div>
                )}
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase">Employment Type</label>
              {renderEditableText({
                field: "employmentType",
                value: employmentTypeDraft,
                placeholder: "Employment type",
                onChange: setEmploymentTypeDraft,
              })}
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
            {renderEditableTextarea({
              field: "summary",
              value: summaryDraft,
              placeholder: "Professional summary",
              onChange: setSummaryDraft,
              className: "min-h-[120px]",
            })}
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Career Goals</label>
            {renderEditableTextarea({
              field: "goals",
              value: goalsDraft,
              placeholder: "Career goals",
              onChange: setGoalsDraft,
              className: "min-h-[120px]",
            })}
          </div>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase">Core Strengths</label>
          {renderEditableTextarea({
            field: "strengths",
            value: strengthsDraft,
            placeholder: "Core strengths",
            onChange: setStrengthsDraft,
            className: "min-h-[90px]",
          })}
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
              {skillsDraft.map((skill) => (
                <Badge key={skill} variant="outline" className="flex items-center gap-1">
                  {skill}
                  <button
                    type="button"
                    className="ml-1 text-muted-foreground hover:text-foreground"
                    onClick={() => removeSkill(skill)}
                    aria-label={`Remove ${skill}`}
                  >
                    <X className="size-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-2 mt-3">
              <Input
                value={skillInput}
                onChange={(event) => setSkillInput(event.target.value)}
                placeholder="Add a skill"
              />
              <Button variant="outline" size="sm" className="font-semibold" onClick={addSkill}>
                <Plus className="size-3 mr-2" />
                Add
              </Button>
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase">Certifications</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {certificationsDraft.map((cert) => (
                <Badge key={cert} variant="secondary" className="flex items-center gap-1">
                  {cert}
                  <button
                    type="button"
                    className="ml-1 text-muted-foreground hover:text-foreground"
                    onClick={() => removeCertification(cert)}
                    aria-label={`Remove ${cert}`}
                  >
                    <X className="size-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-2 mt-3">
              <Input
                value={certInput}
                onChange={(event) => setCertInput(event.target.value)}
                placeholder="Add a certification"
              />
              <Button variant="outline" size="sm" className="font-semibold" onClick={addCertification}>
                <Plus className="size-3 mr-2" />
                Add
              </Button>
            </div>
          </div>
        </div>

        <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold">Education</h4>
            <Badge variant="secondary">Editable</Badge>
          </div>
          <div className="space-y-4">
            {pagedEducation.map((item, localIdx) => {
              const idx = educationStart + localIdx;
              const key = `education-${idx}`;
              const label = [item.degree, item.school, item.year].filter(Boolean).join(" • ");
              return (
                <div key={key} className="rounded-xl border border-border p-4 space-y-2">
                  {editingField === key ? (
                    <>
                      <Input
                        placeholder="School"
                        value={item.school}
                        onChange={(event) => updateEducationItem(idx, "school", event.target.value)}
                        onBlur={() => setEditingField(null)}
                        autoFocus
                      />
                      <Input
                        placeholder="Degree"
                        value={item.degree}
                        onChange={(event) => updateEducationItem(idx, "degree", event.target.value)}
                      />
                      <Input
                        placeholder="Year"
                        value={item.year}
                        onChange={(event) => updateEducationItem(idx, "year", event.target.value)}
                      />
                      <div className="flex justify-between">
                        <Button variant="ghost" size="sm" onClick={() => removeEducationItem(idx)}>
                          Remove
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setEditingField(null)}>
                          Done
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div
                      className="min-h-[64px] rounded-md border border-border px-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors whitespace-pre-wrap"
                      onClick={() => setEditingField(key)}
                    >
                      {label || <span className="text-muted-foreground">Click to add education</span>}
                    </div>
                  )}
                </div>
              );
            })}
            <Button variant="outline" className="w-full font-semibold" onClick={addEducationItem}>
              Add Education
            </Button>
            {educationTotalPages > 1 && (
              <div className="flex items-center justify-between">
                <Button
                  variant="link"
                  className="text-sm font-bold text-muted-foreground hover:text-foreground"
                  onClick={() => setEducationPage((prev) => Math.max(1, prev - 1))}
                  disabled={safeEducationPage === 1}
                >
                  Previous
                </Button>
                <span className="text-xs text-muted-foreground">
                  Page {safeEducationPage} of {educationTotalPages}
                </span>
                <Button
                  variant="link"
                  className="text-sm font-bold text-muted-foreground hover:text-foreground"
                  onClick={() => setEducationPage((prev) => Math.min(educationTotalPages, prev + 1))}
                  disabled={safeEducationPage === educationTotalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

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
                        autoFocus
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
                    <div
                      className="min-h-[90px] rounded-md border border-border px-3 py-2 text-sm cursor-text hover:bg-secondary/30 transition-colors whitespace-pre-wrap"
                      onClick={() => setEditingField(key)}
                    >
                      {item || <span className="text-muted-foreground">Click to add highlight</span>}
                    </div>
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
                    // noop
                  });
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
                        {fileItem.size && (
                          <p className="text-xs text-muted-foreground mt-1">{fileItem.size}</p>
                        )}
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
                        onClick={() => handleFileAction(fileItem)}
                      >
                        <Eye className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:text-primary"
                        onClick={() => {
                          documentDeleteMutation
                            .mutateAsync({ documentId: fileItem.id })
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
            <DialogTitle>{selectedDoc?.file_name ?? "Document Preview"}</DialogTitle>
          </DialogHeader>
          <div className="rounded-lg border border-border p-6 text-sm text-muted-foreground max-h-[70vh] overflow-auto whitespace-pre-wrap">
            {previewText
              ? previewText
              : "Preview unavailable. This document does not have extracted text yet."}
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
}
