import { render, screen } from "@testing-library/react";
import { SidebarHeader } from "@/components/layout/darkSidebar/SidebarHeader";

describe("SidebarHeader", () => {
  it("renders brand and variant badge", () => {
    render(<SidebarHeader isBusiness />);
    expect(screen.getByText("TalentMatch")).toBeInTheDocument();
    expect(screen.getByText("Business")).toBeInTheDocument();
  });
});
