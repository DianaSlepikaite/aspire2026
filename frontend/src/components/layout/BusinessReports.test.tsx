import { render, screen } from "@testing-library/react";
import BusinessReports from "@/components/layout/BusinessReports";
import { vi } from "vitest";
import { useClientNeedsList } from "@/hooks/useClientNeeds";

vi.mock("@/hooks/useClientNeeds", () => ({
  useClientNeedsList: vi.fn(),
}));

describe("BusinessReports", () => {
  it("renders summary metrics from client needs", () => {
    vi.mocked(useClientNeedsList).mockReturnValue({
      data: {
        items: [
          {
            id: "need-1",
            profile_completeness_score: 40,
            missing_information: ["budget"],
          },
          {
            id: "need-2",
            profile_completeness: 80,
            missing_information: ["timeline", "location"],
          },
        ],
        total: 2,
      },
    });

    render(<BusinessReports agentRuns={[]} />);

    expect(screen.getByText("Client Needs")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("Avg Completeness")).toBeInTheDocument();
    expect(screen.getByText("60%")).toBeInTheDocument();
    expect(screen.getByText("Critical Gaps")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });
});
