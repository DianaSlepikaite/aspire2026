import { render, screen, fireEvent } from "@testing-library/react";
import { EditableTextareaField } from "@/components/layout/core/EditableTextareaField";
import { vi } from "vitest";

describe("EditableTextareaField", () => {
  it("enters edit mode on click", () => {
    const setEditingField = vi.fn();

    render(
      <EditableTextareaField
        field="summary"
        value=""
        placeholder="Professional summary"
        onChange={vi.fn()}
        editingField={null}
        setEditingField={setEditingField}
        ariaLabel="Professional summary"
      />
    );

    fireEvent.click(screen.getByLabelText("Professional summary"));
    expect(setEditingField).toHaveBeenCalledWith("summary");
  });

  it("renders textarea when editing and exits on blur", () => {
    const setEditingField = vi.fn();

    render(
      <EditableTextareaField
        field="summary"
        value="Hello"
        onChange={vi.fn()}
        editingField="summary"
        setEditingField={setEditingField}
        ariaLabel="Professional summary"
      />
    );

    const textarea = screen.getByLabelText("Professional summary");
    fireEvent.blur(textarea);
    expect(setEditingField).toHaveBeenCalledWith(null);
  });
});
