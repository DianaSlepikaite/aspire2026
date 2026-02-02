import { render, screen, fireEvent } from "@testing-library/react";
import { SidebarProfile } from "@/components/layout/darkSidebar/SidebarProfile";
import { vi } from "vitest";

describe("SidebarProfile", () => {
  it("renders user info and triggers exit", () => {
    const onExit = vi.fn();

    render(
      <SidebarProfile
        userName="Alex Morgan"
        userRole="Product Manager"
        userImage="/avatar.png"
        onExit={onExit}
      />
    );

    expect(screen.getByText("Alex Morgan")).toBeInTheDocument();
    expect(screen.getByText("Product Manager")).toBeInTheDocument();
    expect(screen.getByLabelText("Alex Morgan avatar")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Return to portal selection"));
    expect(onExit).toHaveBeenCalledTimes(1);
  });
});
