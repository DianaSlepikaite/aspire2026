import { render, screen, fireEvent } from "@testing-library/react";
import { EditableTextField } from "@/components/layout/core/EditableTextField";
import { vi } from "vitest";

describe("EditableTextField", () => {
  it("shows display mode and enters edit on click", () => {
    const setEditingField = vi.fn();

    render(
      <EditableTextField
        field="email"
        value="user@example.com"
        onChange={vi.fn()}
        editingField={null}
        setEditingField={setEditingField}
        ariaLabel="Email"
      />
    );

    fireEvent.click(screen.getByLabelText("Email"));
    expect(setEditingField).toHaveBeenCalledWith("email");
  });

  it("renders input when editing and exits on blur", () => {
    const setEditingField = vi.fn();

    render(
      <EditableTextField
        field="email"
        value="user@example.com"
        onChange={vi.fn()}
        editingField="email"
        setEditingField={setEditingField}
        ariaLabel="Email"
      />
    );

    const input = screen.getByLabelText("Email");
    fireEvent.blur(input);
    expect(setEditingField).toHaveBeenCalledWith(null);
  });
});
