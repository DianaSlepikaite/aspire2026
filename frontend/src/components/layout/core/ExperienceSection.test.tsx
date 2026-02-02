import { render, screen, fireEvent } from "@testing-library/react";
import { ExperienceSection } from "@/components/layout/core/ExperienceSection";
import { vi } from "vitest";

describe("ExperienceSection", () => {
  it("renders experiences and triggers edit", () => {
    const setEditingField = vi.fn();
    render(
      <ExperienceSection
        editingField={null}
        setEditingField={setEditingField}
        pagedExperience={["Built platform"]}
        experienceStart={0}
        updateExperienceItem={vi.fn()}
        removeExperienceItem={vi.fn()}
        addExperienceItem={vi.fn()}
        safeExperiencePage={1}
        experienceTotalPages={1}
        setExperiencePage={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Edit experience highlight 1" }));
    expect(setEditingField).toHaveBeenCalledWith("experience-0");
  });
});
