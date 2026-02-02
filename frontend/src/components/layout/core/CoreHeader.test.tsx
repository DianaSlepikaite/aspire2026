import { render, screen, fireEvent } from "@testing-library/react";
import { CoreHeader } from "@/components/layout/core/CoreHeader";
import { vi } from "vitest";

describe("CoreHeader", () => {
  it("fires sync and save callbacks", () => {
    const onSync = vi.fn();
    const onSave = vi.fn();

    render(
      <CoreHeader
        lastSyncLabel="Last sync: Feb 2, 2026"
        isSaving={false}
        canSave={true}
        onSync={onSync}
        onSave={onSave}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Sync From Agent" }));
    fireEvent.click(screen.getByRole("button", { name: "Save Changes" }));

    expect(onSync).toHaveBeenCalledTimes(1);
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it("disables save when saving or no changes", () => {
    const { rerender } = render(
      <CoreHeader
        lastSyncLabel="Last sync: Feb 2, 2026"
        isSaving={true}
        canSave={true}
        onSync={() => {}}
        onSave={() => {}}
      />
    );

    expect(screen.getByRole("button", { name: "Saving..." })).toBeDisabled();

    rerender(
      <CoreHeader
        lastSyncLabel="Last sync: Feb 2, 2026"
        isSaving={false}
        canSave={false}
        onSync={() => {}}
        onSave={() => {}}
      />
    );

    expect(screen.getByRole("button", { name: "Save Changes" })).toBeDisabled();
  });
});
