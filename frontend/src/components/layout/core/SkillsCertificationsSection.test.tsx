import { render, screen, fireEvent } from "@testing-library/react";
import { SkillsCertificationsSection } from "@/components/layout/core/SkillsCertificationsSection";
import { vi } from "vitest";

describe("SkillsCertificationsSection", () => {
  it("renders skills and certifications and triggers actions", () => {
    const addSkill = vi.fn();
    const removeSkill = vi.fn();
    const addCertification = vi.fn();
    const removeCertification = vi.fn();

    render(
      <SkillsCertificationsSection
        skillsDraft={["Agile", "SQL"]}
        certificationsDraft={["PMP"]}
        skillInput=""
        certInput=""
        setSkillInput={vi.fn()}
        setCertInput={vi.fn()}
        addSkill={addSkill}
        removeSkill={removeSkill}
        addCertification={addCertification}
        removeCertification={removeCertification}
      />
    );

    expect(screen.getByText("Agile")).toBeInTheDocument();
    expect(screen.getByText("SQL")).toBeInTheDocument();
    expect(screen.getByText("PMP")).toBeInTheDocument();

    const addButtons = screen.getAllByRole("button", { name: "Add" });
    fireEvent.click(addButtons[0]);
    expect(addSkill).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Remove Agile" }));
    expect(removeSkill).toHaveBeenCalledWith("Agile");

    fireEvent.click(screen.getByRole("button", { name: "Remove PMP" }));
    expect(removeCertification).toHaveBeenCalledWith("PMP");

    fireEvent.click(addButtons[1]);
    expect(addCertification).toHaveBeenCalled();
  });
});
