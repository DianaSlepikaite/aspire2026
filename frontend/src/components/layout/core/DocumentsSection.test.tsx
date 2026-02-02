import { render, screen, fireEvent } from "@testing-library/react";
import { DocumentsSection } from "@/components/layout/core/DocumentsSection";
import { vi } from "vitest";

const doc = {
  id: "doc-1",
  file_name: "doc.pdf",
  mime_type: "application/pdf",
  created_at: "2026-02-01T00:00:00.000Z",
};

describe("DocumentsSection", () => {
  it("renders documents and pagination", () => {
    render(
      <DocumentsSection
        fileInputRef={{ current: null }}
        pagedDocuments={[doc]}
        safePage={1}
        totalPages={1}
        onUploadClick={vi.fn()}
        onUploadFile={vi.fn()}
        onView={vi.fn()}
        onDelete={vi.fn()}
        onPrevPage={vi.fn()}
        onNextPage={vi.fn()}
      />
    );

    expect(screen.getByText("doc.pdf")).toBeInTheDocument();
    expect(screen.getByText("Page 1 of 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("calls view and delete actions", () => {
    const onView = vi.fn();
    const onDelete = vi.fn();
    render(
      <DocumentsSection
        fileInputRef={{ current: null }}
        pagedDocuments={[doc]}
        safePage={1}
        totalPages={1}
        onUploadClick={vi.fn()}
        onUploadFile={vi.fn()}
        onView={onView}
        onDelete={onDelete}
        onPrevPage={vi.fn()}
        onNextPage={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "View doc.pdf" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete doc.pdf" }));

    expect(onView).toHaveBeenCalledWith(doc);
    expect(onDelete).toHaveBeenCalledWith("doc-1");
  });
});
