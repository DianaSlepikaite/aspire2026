/* eslint-disable react-refresh/only-export-components */
import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

type EmployeeContextValue = {
  employeeProfileId: string | null;
  conversationId: string | null;
  setEmployeeProfileId: (id: string | null) => void;
  setConversationId: (id: string | null) => void;
};

const EmployeeContext = createContext<EmployeeContextValue | null>(null);

export function EmployeeProvider({ children }: { children: ReactNode }) {
  const [employeeProfileId, setEmployeeProfileIdState] = useState<string | null>(
    () => window.localStorage.getItem("career.employeeProfileId")
  );
  const [conversationId, setConversationIdState] = useState<string | null>(
    () => window.localStorage.getItem("career.employeeConversationId")
  );

  const setEmployeeProfileId = (id: string | null) => {
    if (id) {
      window.localStorage.setItem("career.employeeProfileId", id);
    } else {
      window.localStorage.removeItem("career.employeeProfileId");
    }
    setEmployeeProfileIdState(id);
  };

  const setConversationId = (id: string | null) => {
    if (id) {
      window.localStorage.setItem("career.employeeConversationId", id);
    } else {
      window.localStorage.removeItem("career.employeeConversationId");
    }
    setConversationIdState(id);
  };

  useEffect(() => {
    const handler = () => {
      setEmployeeProfileIdState(window.localStorage.getItem("career.employeeProfileId"));
      setConversationIdState(window.localStorage.getItem("career.employeeConversationId"));
    };
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  const value = useMemo(
    () => ({
      employeeProfileId,
      conversationId,
      setEmployeeProfileId,
      setConversationId,
    }),
    [employeeProfileId, conversationId]
  );

  return <EmployeeContext.Provider value={value}>{children}</EmployeeContext.Provider>;
}

export function useEmployeeContext() {
  const ctx = useContext(EmployeeContext);
  if (!ctx) {
    throw new Error("useEmployeeContext must be used within EmployeeProvider");
  }
  return ctx;
}
