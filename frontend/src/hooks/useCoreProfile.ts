import { useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useEmployeeDocuments,
  useEmployeeDocumentDelete,
  useEmployeeProfile,
  useEmployeeProfileUpdate,
  useEmployeeUpload,
} from "@/hooks/useEmployee";
import { useEmployeeContext } from "@/context/EmployeeContext";
import { coreProfile } from "@/components/layout/core/coreData";

export type EducationItem = {
  school: string;
  degree: string;
  year: string;
};

const PAGE_SIZE = 5;
const LIST_PAGE_SIZE = 5;

export function useCoreProfile() {
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

  const coreTags = useMemo(() => {
    const tags = profile?.tags ?? {};
    const coreTag = (tags as Record<string, unknown>)?.core_profile;
    return (coreTag && typeof coreTag === "object" ? (coreTag as Record<string, unknown>) : {}) as Record<string, unknown>;
  }, [profile?.tags]);

  const displayProfile = useMemo(
    () => ({
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
    }),
    [coreTags, profile],
  );

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
      ? displayProfile.education.map((item) => {
          const record = item && typeof item === "object" ? (item as Record<string, unknown>) : {};
          return {
            school: String(record.school ?? ""),
            degree: String(record.degree ?? ""),
            year: String(record.year ?? ""),
          };
        })
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
  }, [displayProfile]);

  const totalPages = Math.max(1, Math.ceil(documents.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const pagedDocuments = documents.slice(startIndex, startIndex + PAGE_SIZE);
  const selectedDoc = documents.find((doc) => doc.id === selectedDocId) ?? null;

  const educationTotalPages = Math.max(1, Math.ceil(educationDraft.length / LIST_PAGE_SIZE));
  const safeEducationPage = Math.min(educationPage, educationTotalPages);
  const educationStart = (safeEducationPage - 1) * LIST_PAGE_SIZE;
  const pagedEducation = educationDraft.slice(educationStart, educationStart + LIST_PAGE_SIZE);

  const experienceTotalPages = Math.max(1, Math.ceil(experienceDraft.length / LIST_PAGE_SIZE));
  const safeExperiencePage = Math.min(experiencePage, experienceTotalPages);
  const experienceStart = (safeExperiencePage - 1) * LIST_PAGE_SIZE;
  const pagedExperience = experienceDraft.slice(experienceStart, experienceStart + LIST_PAGE_SIZE);

  const lastSyncLabel = useMemo(() => {
    if (!profile?.updated_at) return "Last sync: N/A";
    return `Last sync: ${new Date(profile.updated_at).toLocaleDateString("en-US", {
      month: "short",
      day: "2-digit",
      year: "numeric",
    })}`;
  }, [profile?.updated_at]);

  function handleFileAction(fileItem: (typeof documents)[number]) {
    setSelectedDocId(fileItem.id);
    setPreviewText(fileItem.raw_text ?? null);
  }

  function closePreview() {
    setPreviewText(null);
    setSelectedDocId(null);
  }

  function addSkill() {
    const value = skillInput.trim();
    if (!value) return;
    setSkillsDraft((prev) => [...prev, value]);
    setSkillInput("");
  }

  function removeSkill(skill: string) {
    setSkillsDraft((prev) => prev.filter((item) => item !== skill));
  }

  function addCertification() {
    const value = certInput.trim();
    if (!value) return;
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
    setEducationPage((prev) => Math.max(prev, Math.ceil((educationDraft.length + 1) / LIST_PAGE_SIZE)));
  }

  function removeEducationItem(index: number) {
    setEducationDraft((prev) => prev.filter((_, idx) => idx !== index));
    setEducationPage((prev) => Math.max(1, Math.min(prev, Math.ceil((educationDraft.length - 1) / LIST_PAGE_SIZE))));
  }

  function updateExperienceItem(index: number, value: string) {
    setExperienceDraft((prev) => prev.map((item, idx) => (idx === index ? value : item)));
  }

  function addExperienceItem() {
    setExperienceDraft((prev) => [...prev, ""]);
    setExperiencePage((prev) => Math.max(prev, Math.ceil((experienceDraft.length + 1) / LIST_PAGE_SIZE)));
  }

  function removeExperienceItem(index: number) {
    setExperienceDraft((prev) => prev.filter((_, idx) => idx !== index));
    setExperiencePage((prev) => Math.max(1, Math.min(prev, Math.ceil((experienceDraft.length - 1) / LIST_PAGE_SIZE))));
  }

  async function handleSaveChanges() {
    if (!employeeProfileId) return;
    setIsSaving(true);
    try {
      const existingTags = profile?.tags && typeof profile.tags === "object" ? (profile.tags as Record<string, unknown>) : {};
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
          experience: experienceDraft.filter(Boolean).map((item) => ({ description: item })),
          tags: updatedTags,
        },
      });
      queryClient.invalidateQueries({ queryKey: ["employee-profile", employeeProfileId] });
    } finally {
      setIsSaving(false);
    }
  }

  const handleSyncFromAgent = () => {
    if (employeeProfileId) {
      queryClient.invalidateQueries({ queryKey: ["employee-profile", employeeProfileId] });
    }
  };

  const handleUploadFile = (file: File) => {
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
  };

  const handleDeleteDocument = (documentId: string) => {
    documentDeleteMutation
      .mutateAsync({ documentId })
      .then(() => {
        if (employeeProfileId) {
          queryClient.invalidateQueries({ queryKey: ["employee-documents", employeeProfileId] });
        }
      })
      .catch(() => {
        // noop
      });
  };

  return {
    employeeProfileId,
    documents,
    profile,
    fileInputRef,
    selectedDocId,
    previewText,
    page,
    educationPage,
    experiencePage,
    skillsDraft,
    certificationsDraft,
    educationDraft,
    experienceDraft,
    fullNameDraft,
    emailDraft,
    phoneDraft,
    summaryDraft,
    titleDraft,
    departmentDraft,
    managerDraft,
    locationDraft,
    startDateDraft,
    employmentTypeDraft,
    strengthsDraft,
    goalsDraft,
    skillInput,
    certInput,
    isSaving,
    editingField,
    totalPages,
    safePage,
    pagedDocuments,
    selectedDoc,
    lastSyncLabel,
    educationTotalPages,
    safeEducationPage,
    educationStart,
    pagedEducation,
    experienceTotalPages,
    safeExperiencePage,
    experienceStart,
    pagedExperience,
    setPage,
    setEducationPage,
    setExperiencePage,
    setSkillsDraft,
    setCertificationsDraft,
    setEducationDraft,
    setExperienceDraft,
    setFullNameDraft,
    setEmailDraft,
    setPhoneDraft,
    setSummaryDraft,
    setTitleDraft,
    setDepartmentDraft,
    setManagerDraft,
    setLocationDraft,
    setStartDateDraft,
    setEmploymentTypeDraft,
    setStrengthsDraft,
    setGoalsDraft,
    setSkillInput,
    setCertInput,
    setEditingField,
    setSelectedDocId,
    setPreviewText,
    handleFileAction,
    closePreview,
    addSkill,
    removeSkill,
    addCertification,
    removeCertification,
    updateEducationItem,
    addEducationItem,
    removeEducationItem,
    updateExperienceItem,
    addExperienceItem,
    removeExperienceItem,
    handleSaveChanges,
    handleSyncFromAgent,
    handleUploadFile,
    handleDeleteDocument,
  };
}
