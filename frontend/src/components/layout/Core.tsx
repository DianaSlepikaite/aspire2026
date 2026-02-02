import { useCoreProfile } from "@/hooks/useCoreProfile";
import { CoreHeader } from "@/components/layout/core/CoreHeader";
import { PersonalRoleSection } from "@/components/layout/core/PersonalRoleSection";
import { SummaryGoalsSection } from "@/components/layout/core/SummaryGoalsSection";
import { SkillsCertificationsSection } from "@/components/layout/core/SkillsCertificationsSection";
import { EducationSection } from "@/components/layout/core/EducationSection";
import { ExperienceSection } from "@/components/layout/core/ExperienceSection";
import { DocumentsSection } from "@/components/layout/core/DocumentsSection";
import { IntegrationsSection } from "@/components/layout/core/IntegrationsSection";
import { PreviewDialog } from "@/components/layout/core/PreviewDialog";
import { integrations } from "@/components/layout/core/coreData";

export default function Core() {
  const {
    employeeProfileId,
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
  } = useCoreProfile();

  return (
    <section className="space-y-8">
      <CoreHeader
        lastSyncLabel={lastSyncLabel}
        isSaving={isSaving}
        canSave={Boolean(employeeProfileId)}
        onSync={handleSyncFromAgent}
        onSave={handleSaveChanges}
      />

      <PersonalRoleSection
        editingField={editingField}
        setEditingField={setEditingField}
        fullNameDraft={fullNameDraft}
        setFullNameDraft={setFullNameDraft}
        emailDraft={emailDraft}
        setEmailDraft={setEmailDraft}
        phoneDraft={phoneDraft}
        setPhoneDraft={setPhoneDraft}
        locationDraft={locationDraft}
        setLocationDraft={setLocationDraft}
        titleDraft={titleDraft}
        setTitleDraft={setTitleDraft}
        departmentDraft={departmentDraft}
        setDepartmentDraft={setDepartmentDraft}
        managerDraft={managerDraft}
        setManagerDraft={setManagerDraft}
        startDateDraft={startDateDraft}
        setStartDateDraft={setStartDateDraft}
        employmentTypeDraft={employmentTypeDraft}
        setEmploymentTypeDraft={setEmploymentTypeDraft}
      />

      <SummaryGoalsSection
        editingField={editingField}
        setEditingField={setEditingField}
        summaryDraft={summaryDraft}
        setSummaryDraft={setSummaryDraft}
        goalsDraft={goalsDraft}
        setGoalsDraft={setGoalsDraft}
        strengthsDraft={strengthsDraft}
        setStrengthsDraft={setStrengthsDraft}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkillsCertificationsSection
          skillsDraft={skillsDraft}
          certificationsDraft={certificationsDraft}
          skillInput={skillInput}
          certInput={certInput}
          setSkillInput={setSkillInput}
          setCertInput={setCertInput}
          addSkill={addSkill}
          removeSkill={removeSkill}
          addCertification={addCertification}
          removeCertification={removeCertification}
        />
        <EducationSection
          editingField={editingField}
          setEditingField={setEditingField}
          pagedEducation={pagedEducation}
          educationStart={educationStart}
          updateEducationItem={updateEducationItem}
          removeEducationItem={removeEducationItem}
          addEducationItem={addEducationItem}
          safeEducationPage={safeEducationPage}
          educationTotalPages={educationTotalPages}
          setEducationPage={setEducationPage}
        />
      </div>

      <ExperienceSection
        editingField={editingField}
        setEditingField={setEditingField}
        pagedExperience={pagedExperience}
        experienceStart={experienceStart}
        updateExperienceItem={updateExperienceItem}
        removeExperienceItem={removeExperienceItem}
        addExperienceItem={addExperienceItem}
        safeExperiencePage={safeExperiencePage}
        experienceTotalPages={experienceTotalPages}
        setExperiencePage={setExperiencePage}
      />

      <DocumentsSection
        fileInputRef={fileInputRef}
        pagedDocuments={pagedDocuments}
        safePage={safePage}
        totalPages={totalPages}
        onUploadClick={() => fileInputRef.current?.click()}
        onUploadFile={handleUploadFile}
        onView={handleFileAction}
        onDelete={handleDeleteDocument}
        onPrevPage={() => setPage((prev) => Math.max(1, prev - 1))}
        onNextPage={() => setPage((prev) => Math.min(totalPages, prev + 1))}
      />

      <IntegrationsSection integrations={integrations} />

      <PreviewDialog
        open={Boolean(selectedDocId)}
        fileName={selectedDoc?.file_name}
        previewText={previewText}
        onClose={closePreview}
      />
    </section>
  );
}
