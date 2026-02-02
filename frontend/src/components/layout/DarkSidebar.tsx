import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useProcessIntake, useUploadIntakeFile, useUploadIntakeText } from "@/hooks/useClientNeeds";
import { useChatAgent } from "@/hooks/useChatAgent";
import { AgentResponse, extractClientNeedId, extractCompletenessScore, getClarifyingQuestions } from "@/lib/clientNeedApi";
import { useQueryClient } from "@tanstack/react-query";
import { SidebarHeader } from "@/components/layout/darkSidebar/SidebarHeader";
import { ChatThread } from "@/components/layout/darkSidebar/ChatThread";
import { ChatComposer } from "@/components/layout/darkSidebar/ChatComposer";
import { IntakeDialog } from "@/components/layout/darkSidebar/IntakeDialog";
import { SidebarProfile } from "@/components/layout/darkSidebar/SidebarProfile";

interface DarkSidebarProps {
  userName?: string;
  userRole?: string;
  userImage?: string;
  variant?: "career" | "business";
  activeClientNeedId?: string | null;
  onClientNeedCreated?: (clientNeedId: string) => void;
  onAgentResult?: (result: AgentResponse) => void;
}

export function DarkSidebar({ 
  userName = "Sarah Jenkins",
  userRole = "Senior Project Manager",
  userImage = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face",
  variant = "career",
  activeClientNeedId,
  onClientNeedCreated,
  onAgentResult,
}: DarkSidebarProps) {
  const navigate = useNavigate();
  const isBusiness = variant === "business";
  const [clientName, setClientName] = useState("");
  const [clientEmail, setClientEmail] = useState("");
  const [briefText, setBriefText] = useState("");
  const [intakeFile, setIntakeFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusIsError, setStatusIsError] = useState(false);
  const [intakeOpen, setIntakeOpen] = useState(false);
  const [currentClientNeedId, setCurrentClientNeedId] = useState<string | null>(null);
  const isMountedRef = useRef(true);
  const queryClient = useQueryClient();

  const uploadText = useUploadIntakeText();
  const uploadFile = useUploadIntakeFile();
  const processIntake = useProcessIntake();

  const isSubmitting = uploadText.isPending || uploadFile.isPending || processIntake.isPending;
  const {
    chatInput,
    setChatInput,
    chatMessages,
    setChatMessages,
    aiState,
    chatEndRef,
    careerFileInputRef,
    recognitionAvailable,
    hasConversationStarted,
    showWelcome,
    handleSendMessage,
    handleStartListening,
    handleStopListening,
    handleCareerFileUpload,
  } = useChatAgent({
    isBusiness,
    userName,
    currentClientNeedId,
    setCurrentClientNeedId,
    onClientNeedCreated,
    onAgentResult,
    uploadText: uploadText.mutateAsync,
    processIntake: ({ intakeId, userQuery }) => processIntake.mutateAsync({ intakeId, userQuery }),
  });

  const isChatBusy = isSubmitting || aiState === "thinking";

  const setStatus = (message: string | null, isError: boolean) => {
    if (!isMountedRef.current) return;
    setStatusMessage(message);
    setStatusIsError(isError);
  };

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (activeClientNeedId) {
      setCurrentClientNeedId(activeClientNeedId);
    }
  }, [activeClientNeedId]);

  async function handleSubmitIntake() {
    setStatus(null, false);
    try {
      let intakeId: string | null = null;
      let uploadLabel: string | null = null;
      if (currentClientNeedId) {
        setCurrentClientNeedId(null);
      }
      if (intakeFile) {
        const response = await uploadFile.mutateAsync({
          file: intakeFile,
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
        });
        intakeId = response.id;
        uploadLabel = `Uploaded file: ${intakeFile.name}`;
      } else if (briefText.trim()) {
        const response = await uploadText.mutateAsync({
          text_content: briefText.trim(),
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
          source_label: "business_portal",
        });
        intakeId = response.id;
        uploadLabel = "Uploaded brief text";
      } else {
        setStatus("Add a brief or upload a file to start intake.", true);
        return;
      }

      if (uploadLabel) {
        setChatMessages((prev) => [...prev, { role: "user", content: uploadLabel }]);
      }
      setIntakeOpen(false);
      setBriefText("");
      setIntakeFile(null);

      try {
        const agentResponse = await processIntake.mutateAsync({
          intakeId,
          userQuery: briefText.trim() || undefined,
        });
        const clientNeedId = extractClientNeedId(agentResponse.intermediate_steps);
        const derivedCompleteness = extractCompletenessScore(agentResponse.intermediate_steps);

        if (clientNeedId) {
          let clarifyingQuestions: string | undefined;
          try {
            const questionsResponse = await getClarifyingQuestions({ client_need_id: clientNeedId });
            clarifyingQuestions = questionsResponse.questions;
          } catch {
            // Non-critical: clarifying questions may not be available yet
          }

          const enrichedResponse: AgentResponse = {
            ...agentResponse,
            client_need_id: clientNeedId,
            completeness_score: derivedCompleteness ?? agentResponse.completeness_score,
            clarifying_questions: clarifyingQuestions,
          };
          onAgentResult?.(enrichedResponse);

          setCurrentClientNeedId(clientNeedId);
          onClientNeedCreated?.(clientNeedId);
          queryClient.invalidateQueries({ queryKey: ["client-needs"] });
          queryClient.invalidateQueries({ queryKey: ["client-need", clientNeedId] });
          queryClient.invalidateQueries({ queryKey: ["client-need-matches", clientNeedId] });
          setStatus("Client need created and ready for review.", false);
        } else {
          setStatus("Intake processed, but client need ID was not returned.", true);
        }
      } catch (agentError) {
        console.error("Agent processing failed after upload.", agentError);
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Your upload was received, but the agent could not process it right now. Please try again in a moment.",
            },
          ]);
        setStatus("Upload succeeded, but agent processing failed.", true);
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to process intake.", true);
    }
  }
  return (
    <aside className="w-1/2 min-w-[400px] h-full bg-background flex flex-col border-r border-border p-8">
      <SidebarHeader isBusiness={isBusiness} />

      <div className="flex-1 min-h-0 flex flex-col gap-6">
        <ChatThread
          showWelcome={showWelcome}
          userName={userName}
          isBusiness={isBusiness}
          messages={chatMessages}
          aiState={aiState}
          hasConversationStarted={hasConversationStarted}
          chatEndRef={chatEndRef}
        />

        <ChatComposer
          isBusiness={isBusiness}
          chatInput={chatInput}
          onChatInputChange={setChatInput}
          onSend={() => void handleSendMessage()}
          isChatBusy={isChatBusy}
          aiState={aiState}
          recognitionAvailable={recognitionAvailable}
          onStartListening={handleStartListening}
          onStopListening={handleStopListening}
          onOpenIntake={() => setIntakeOpen(true)}
          careerFileInputRef={careerFileInputRef}
          onCareerFileChange={handleCareerFileUpload}
        />
      </div>

      {isBusiness && (
        <IntakeDialog
          open={intakeOpen}
          onOpenChange={setIntakeOpen}
          clientName={clientName}
          clientEmail={clientEmail}
          briefText={briefText}
          intakeFile={intakeFile}
          statusMessage={statusMessage}
          statusIsError={statusIsError}
          isSubmitting={isSubmitting}
          onClientNameChange={setClientName}
          onClientEmailChange={setClientEmail}
          onBriefTextChange={setBriefText}
          onFileChange={setIntakeFile}
          onSubmit={handleSubmitIntake}
        />
      )}

      <SidebarProfile
        userName={userName}
        userRole={userRole}
        userImage={userImage}
        onExit={() => navigate("/", { replace: true })}
      />
    </aside>
  );
}
