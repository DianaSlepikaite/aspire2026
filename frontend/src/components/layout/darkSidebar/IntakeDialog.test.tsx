import { render, screen } from "@testing-library/react";
import { IntakeDialog } from "@/components/layout/darkSidebar/IntakeDialog";


describe("IntakeDialog", () => {
  it("renders dialog content when open", () => {
    render(
      <IntakeDialog
        open
        onOpenChange={() => {}}
        clientName=""
        clientEmail=""
        briefText=""
        intakeFile={null}
        statusMessage={null}
        statusIsError={false}
        isSubmitting={false}
        onClientNameChange={() => {}}
        onClientEmailChange={() => {}}
        onBriefTextChange={() => {}}
        onFileChange={() => {}}
        onSubmit={() => {}}
      />
    );

    expect(screen.getByText("Client Need Intake")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Process Client Need" })).toBeInTheDocument();
  });
});
