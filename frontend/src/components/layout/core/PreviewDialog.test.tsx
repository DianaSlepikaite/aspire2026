import { render, screen } from "@testing-library/react";
import { PreviewDialog } from "@/components/layout/core/PreviewDialog";


describe("PreviewDialog", () => {
  it("shows preview text when open", () => {
    render(
      <PreviewDialog
        open
        fileName="doc.pdf"
        previewText="Preview content"
        onClose={() => {}}
      />
    );

    expect(screen.getByText("doc.pdf")).toBeInTheDocument();
    expect(screen.getByText("Preview content")).toBeInTheDocument();
  });
});
