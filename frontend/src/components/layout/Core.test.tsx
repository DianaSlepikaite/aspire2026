import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import Core from "@/components/layout/Core";

vi.mock("@/hooks/useCoreProfile", () => ({
  useCoreProfile: () => ({
    employeeProfileId: "profile-1",
    fileInputRef: { current: null },
    selectedDocId: null,
    previewText: null,
    page: 1,
    educationPage: 1,
    experiencePage: 1,
    skillsDraft: ["Agile"],
    certificationsDraft: ["PMP"],
    educationDraft: [{ school: "UT", degree: "BS", year: "2016" }],
    experienceDraft: ["Did a thing"],
    fullNameDraft: "Sarah",
    emailDraft: "sarah@example.com",
    phoneDraft: "123",
    summaryDraft: "Summary",
    titleDraft: "Manager",
    departmentDraft: "Tech",
    managerDraft: "Boss",
    locationDraft: "Austin",
    startDateDraft: "2021-01-01",
    employmentTypeDraft: "Full-time",
    strengthsDraft: "Strengths",
    goalsDraft: "Goals",
    skillInput: "",
    certInput: "",
    isSaving: false,
    editingField: null,
    totalPages: 1,
    safePage: 1,
    pagedDocuments: [
      { id: "doc-1", file_name: "doc.pdf", mime_type: "application/pdf", created_at: new Date().toISOString() },
    ],
    selectedDoc: { id: "doc-1", file_name: "doc.pdf", mime_type: "application/pdf", created_at: new Date().toISOString() },
    lastSyncLabel: "Last sync: Jan 01, 2026",
    educationTotalPages: 1,
    safeEducationPage: 1,
    educationStart: 0,
    pagedEducation: [{ school: "UT", degree: "BS", year: "2016" }],
    experienceTotalPages: 1,
    safeExperiencePage: 1,
    experienceStart: 0,
    pagedExperience: ["Did a thing"],
    setPage: vi.fn(),
    setEducationPage: vi.fn(),
    setExperiencePage: vi.fn(),
    setFullNameDraft: vi.fn(),
    setEmailDraft: vi.fn(),
    setPhoneDraft: vi.fn(),
    setSummaryDraft: vi.fn(),
    setTitleDraft: vi.fn(),
    setDepartmentDraft: vi.fn(),
    setManagerDraft: vi.fn(),
    setLocationDraft: vi.fn(),
    setStartDateDraft: vi.fn(),
    setEmploymentTypeDraft: vi.fn(),
    setStrengthsDraft: vi.fn(),
    setGoalsDraft: vi.fn(),
    setSkillInput: vi.fn(),
    setCertInput: vi.fn(),
    setEditingField: vi.fn(),
    handleFileAction: vi.fn(),
    closePreview: vi.fn(),
    addSkill: vi.fn(),
    removeSkill: vi.fn(),
    addCertification: vi.fn(),
    removeCertification: vi.fn(),
    updateEducationItem: vi.fn(),
    addEducationItem: vi.fn(),
    removeEducationItem: vi.fn(),
    updateExperienceItem: vi.fn(),
    addExperienceItem: vi.fn(),
    removeExperienceItem: vi.fn(),
    handleSaveChanges: vi.fn(),
    handleSyncFromAgent: vi.fn(),
    handleUploadFile: vi.fn(),
    handleDeleteDocument: vi.fn(),
  }),
}));

describe("Core", () => {
  it("renders main sections and actions", () => {
    render(<Core />);

    expect(screen.getByText("Core Employee Profile")).toBeInTheDocument();
    expect(screen.getByText("Personal & Contact")).toBeInTheDocument();
    expect(screen.getByText("Role & Org")).toBeInTheDocument();
    expect(screen.getByText("Summary & Goals")).toBeInTheDocument();
    expect(screen.getByText("Skills & Certifications")).toBeInTheDocument();
    expect(screen.getByText("Education")).toBeInTheDocument();
    expect(screen.getByText("Experience Highlights")).toBeInTheDocument();
    expect(screen.getByText("Context Files")).toBeInTheDocument();
    expect(screen.getByText("Integrations")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: "Sync From Agent" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Save Changes" })).toBeEnabled();
  });
});
