import { render, screen, fireEvent } from "@testing-library/react";
import { PersonalRoleSection } from "@/components/layout/core/PersonalRoleSection";
import { vi } from "vitest";

describe("PersonalRoleSection", () => {
  it("triggers edit mode for location", () => {
    const setEditingField = vi.fn();
    render(
      <PersonalRoleSection
        editingField={null}
        setEditingField={setEditingField}
        fullNameDraft="Sarah"
        setFullNameDraft={vi.fn()}
        emailDraft="sarah@example.com"
        setEmailDraft={vi.fn()}
        phoneDraft="123"
        setPhoneDraft={vi.fn()}
        locationDraft="Austin"
        setLocationDraft={vi.fn()}
        titleDraft="Manager"
        setTitleDraft={vi.fn()}
        departmentDraft="Tech"
        setDepartmentDraft={vi.fn()}
        managerDraft="Boss"
        setManagerDraft={vi.fn()}
        startDateDraft="2021"
        setStartDateDraft={vi.fn()}
        employmentTypeDraft="Full-time"
        setEmploymentTypeDraft={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Location" }));
    expect(setEditingField).toHaveBeenCalledWith("location");
  });
});
