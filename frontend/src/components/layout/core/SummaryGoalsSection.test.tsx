import { render, screen, fireEvent } from "@testing-library/react";
import { SummaryGoalsSection } from "@/components/layout/core/SummaryGoalsSection";
import { vi } from "vitest";

describe("SummaryGoalsSection", () => {
  it("enters edit mode for summary", () => {
    const setEditingField = vi.fn();

    render(
      <SummaryGoalsSection
        editingField={null}
        setEditingField={setEditingField}
        summaryDraft=""
        setSummaryDraft={vi.fn()}
        goalsDraft=""
        setGoalsDraft={vi.fn()}
        strengthsDraft=""
        setStrengthsDraft={vi.fn()}
      />
    );

    fireEvent.click(screen.getByLabelText("Professional summary"));
    expect(setEditingField).toHaveBeenCalledWith("summary");
  });
});
