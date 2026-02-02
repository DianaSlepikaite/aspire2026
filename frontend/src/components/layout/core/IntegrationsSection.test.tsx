import { render, screen } from "@testing-library/react";
import { IntegrationsSection } from "@/components/layout/core/IntegrationsSection";

const integrations = [
  {
    name: "LinkedIn",
    description: "Sync roles",
    icon: () => <span data-testid="icon" />,
    connected: true,
    handle: "linkedin.com/in/user",
  },
];

describe("IntegrationsSection", () => {
  it("renders integration cards", () => {
    render(<IntegrationsSection integrations={integrations} />);

    expect(screen.getByText("LinkedIn")).toBeInTheDocument();
    expect(screen.getByText("Sync roles")).toBeInTheDocument();
    expect(screen.getByText("linkedin.com/in/user")).toBeInTheDocument();
    expect(screen.getByText("Disconnect")).toBeInTheDocument();
  });
});
