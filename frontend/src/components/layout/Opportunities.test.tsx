import { render, screen } from "@testing-library/react";
import Opportunities from "@/components/layout/Opportunities";

describe("Opportunities", () => {
  it("renders the section heading and action", () => {
    render(<Opportunities />);

    expect(screen.getByText("Opportunities")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Explore Matches" })).toBeInTheDocument();
  });
});
