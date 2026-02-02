import { render, screen, fireEvent } from "@testing-library/react";
import { EducationSection } from "@/components/layout/core/EducationSection";
import { vi } from "vitest";

const items = [
  { school: "UT", degree: "BS", year: "2016" },
  { school: "MIT", degree: "MS", year: "2018" },
];

describe("EducationSection", () => {
  it("renders items and pagination", () => {
    render(
      <EducationSection
        editingField={null}
        setEditingField={vi.fn()}
        pagedEducation={items}
        educationStart={0}
        updateEducationItem={vi.fn()}
        removeEducationItem={vi.fn()}
        addEducationItem={vi.fn()}
        safeEducationPage={1}
        educationTotalPages={1}
        setEducationPage={vi.fn()}
      />
    );

    expect(screen.getByText(/UT/)).toBeInTheDocument();
    expect(screen.getByText(/MIT/)).toBeInTheDocument();
    expect(screen.getByText("Add Education")).toBeInTheDocument();
  });

  it("enters edit mode on click", () => {
    const setEditingField = vi.fn();
    render(
      <EducationSection
        editingField={null}
        setEditingField={setEditingField}
        pagedEducation={items.slice(0, 1)}
        educationStart={0}
        updateEducationItem={vi.fn()}
        removeEducationItem={vi.fn()}
        addEducationItem={vi.fn()}
        safeEducationPage={1}
        educationTotalPages={1}
        setEducationPage={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Edit education entry 1" }));
    expect(setEditingField).toHaveBeenCalledWith("education-0");
  });
});
