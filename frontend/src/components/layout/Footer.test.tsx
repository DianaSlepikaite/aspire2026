import { render, screen } from "@testing-library/react";
import { Footer } from "@/components/layout/Footer";

describe("Footer", () => {
  it("renders default variant content", () => {
    render(<Footer />);

    expect(screen.getByText("AI Sync Active")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Platform Status" })).toBeInTheDocument();
  });

  it("renders minimal variant content", () => {
    render(<Footer variant="minimal" />);

    expect(screen.getByText("Privacy Policy")).toBeInTheDocument();
    expect(screen.getByText("© 2026 TalentMatch Platform. All rights reserved.")).toBeInTheDocument();
  });
});
