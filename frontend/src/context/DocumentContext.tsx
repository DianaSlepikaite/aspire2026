import type { ReactNode } from "react";
import { createContext, useContext, useMemo, useState } from "react";

export type DocumentStatus = "Signed" | "Pending Review" | "Completed" | "Uploaded";

export type DocumentItem = {
  id: string;
  name: string;
  date: string;
  size?: string;
  status?: DocumentStatus;
  type?: string;
  file?: File;
  source?: "profile" | "core" | "chat";
};

type DocumentContextValue = {
  documents: DocumentItem[];
  addFiles: (files: FileList | File[] | null, source?: DocumentItem["source"]) => void;
  removeDocument: (id: string) => void;
};

const DocumentContext = createContext<DocumentContextValue | null>(null);

const seededDocuments: DocumentItem[] = [
  {
    id: "doc-1",
    name: "Employment_Contract_2026.pdf",
    status: "Signed",
    date: "Oct 12, 2023",
    type: "Contract",
  },
  {
    id: "doc-2",
    name: "PMP_Certification_Renewal.pdf",
    status: "Pending Review",
    date: "Jan 05, 2026",
    type: "Certificate",
  },
  {
    id: "doc-3",
    name: "Annual_Performance_Review_Q4.pdf",
    status: "Completed",
    date: "Dec 20, 2023",
    type: "Review",
  },
  {
    id: "doc-4",
    name: "Resume_Sarah_Jenkins.pdf",
    status: "Uploaded",
    date: "Jan 10, 2026",
    type: "Resume",
  },
];

function formatSize(bytes: number) {
  if (!Number.isFinite(bytes)) return "";
  const kb = bytes / 1024;
  if (kb < 1024) return `${Math.max(1, Math.round(kb))} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<DocumentItem[]>(seededDocuments);

  const addFiles: DocumentContextValue["addFiles"] = (files, source) => {
    if (!files || (Array.isArray(files) && files.length === 0)) return;
    const fileArray = Array.isArray(files) ? files : Array.from(files);
    if (fileArray.length === 0) return;
    const dateLabel = formatDate(new Date());
    const nextDocs: DocumentItem[] = fileArray.map((file) => ({
      id: `doc-${crypto.randomUUID()}`,
      name: file.name,
      status: "Pending Review",
      date: dateLabel,
      size: formatSize(file.size),
      type: file.type ? file.type.split("/")[1]?.toUpperCase() || "Document" : "Document",
      file,
      source,
    }));
    setDocuments((prev) => [...nextDocs, ...prev]);
  };

  const removeDocument = (id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const value = useMemo(
    () => ({
      documents,
      addFiles,
      removeDocument,
    }),
    [documents]
  );

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>;
}

export function useDocuments() {
  const ctx = useContext(DocumentContext);
  if (!ctx) {
    throw new Error("useDocuments must be used within a DocumentProvider");
  }
  return ctx;
}
