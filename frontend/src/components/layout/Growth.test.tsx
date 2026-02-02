import { render, screen } from "@testing-library/react";
import Growth from "@/components/layout/Growth";

describe("Growth", () => {
  it("renders core sections", () => {
    render(<Growth />);

    expect(screen.getByText("Growth & Learning")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Recommended Learning")).toBeInTheDocument();
    expect(screen.getByText("Mandatory Training")).toBeInTheDocument();
  });
});
