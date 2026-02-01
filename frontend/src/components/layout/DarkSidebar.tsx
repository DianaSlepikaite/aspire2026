import { useEffect, useRef, useState } from "react";
import { Mic, FileUp, PlusCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from "react-router-dom";
import { useProcessIntake, useUploadIntakeFile, useUploadIntakeText } from "@/hooks/useClientNeeds";
import {
  AgentResponse,
  extractClientNeedId,
  extractCompletenessScore,
  getClarifyingQuestions,
  sendConversationMessage,
  startConversation,
  updateClientNeedFromMessage,
} from "@/lib/clientNeedApi";
import {
  processEmployeeUpload,
  sendEmployeeMessage,
  startEmployeeConversation,
  synthesizeEmployeeSpeech,
} from "@/lib/employeeApi";
import { useQueryClient } from "@tanstack/react-query";
import { useEmployeeContext } from "@/context/EmployeeContext";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

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
  const [intakeOpen, setIntakeOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [aiState, setAiState] = useState<"idle" | "listening" | "thinking" | "talking">("idle");
  const [hasConversationStarted, setHasConversationStarted] = useState(false);
  const [currentClientNeedId, setCurrentClientNeedId] = useState<string | null>(null);
  const {
    employeeProfileId,
    conversationId: employeeConversationId,
    setEmployeeProfileId,
    setConversationId: setEmployeeConversationId,
  } = useEmployeeContext();
  const recognitionRef = useRef<any>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const careerFileInputRef = useRef<HTMLInputElement | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const queryClient = useQueryClient();

  const uploadText = useUploadIntakeText();
  const uploadFile = useUploadIntakeFile();
  const processIntake = useProcessIntake();

  const isSubmitting = uploadText.isPending || uploadFile.isPending || processIntake.isPending;
  const isChatBusy = isSubmitting || aiState === "thinking";

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognitionImpl = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionImpl) return;

    const recognition = new SpeechRecognitionImpl();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setAiState("listening");
    recognition.onend = () => setAiState("idle");
    recognition.onerror = () => setAiState("idle");
    recognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      if (transcript) {
        setChatInput(transcript);
        void handleSendMessage(transcript, "speech");
      }
    };

    recognitionRef.current = recognition;
  }, []);

  useEffect(() => {
    if (!isBusiness && employeeProfileId) {
      setHasConversationStarted(true);
    }
  }, [isBusiness, employeeProfileId]);

  useEffect(() => {
    if (activeClientNeedId) {
      setCurrentClientNeedId(activeClientNeedId);
      setHasConversationStarted(true);
    }
  }, [activeClientNeedId]);

  useEffect(() => {
    if (!hasConversationStarted) return;
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatMessages, aiState, hasConversationStarted]);

  useEffect(() => {
    return () => {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
    };
  }, []);

  async function handleSendMessage(messageOverride?: string, messageType: "text" | "speech" = "text") {
    const message = (messageOverride ?? chatInput).trim();
    if (!message) return;

    setHasConversationStarted(true);
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatInput("");
    setAiState("thinking");

    try {
      if (!isBusiness) {
        try {
          let activeConversationId = employeeConversationId;
          let activeProfileId = employeeProfileId;
          if (!activeConversationId) {
            const start = await startEmployeeConversation({
              employee_name: userName,
              source_channel: "career_portal_chat",
            });
            activeConversationId = start.conversation_id;
            setEmployeeConversationId(start.conversation_id);
            if (start.employee_profile_id) {
              setEmployeeProfileId(start.employee_profile_id);
              activeProfileId = start.employee_profile_id;
            }
            if (start.greeting_message) {
              setChatMessages((prev) => [...prev, { role: "assistant", content: start.greeting_message }]);
            }
          }

          const response = await sendEmployeeMessage(activeConversationId, { message, message_type: messageType });
          setChatMessages((prev) => [...prev, { role: "assistant", content: response.assistant_message }]);
          if (response.employee_profile_id) {
            setEmployeeProfileId(response.employee_profile_id);
            activeProfileId = response.employee_profile_id;
          }
          if (activeProfileId) {
            queryClient.invalidateQueries({ queryKey: ["employee-profile", activeProfileId] });
            queryClient.invalidateQueries({ queryKey: ["employee-documents", activeProfileId] });
          }
          if (messageType === "speech") {
            setAiState("talking");
            try {
              const audioBlob = await synthesizeEmployeeSpeech(response.assistant_message);
              if (audioPlayerRef.current) {
                audioPlayerRef.current.pause();
                audioPlayerRef.current = null;
              }
              const url = URL.createObjectURL(audioBlob);
              const audio = new Audio(url);
              audioPlayerRef.current = audio;
              audio.onended = () => {
                URL.revokeObjectURL(url);
                setAiState("idle");
              };
              audio.onerror = () => {
                URL.revokeObjectURL(url);
                setAiState("idle");
              };
              void audio.play();
            } catch (error) {
              console.error("Speech synthesis failed.", error);
              setAiState("idle");
            }
          } else {
            setAiState("talking");
            window.setTimeout(() => setAiState("idle"), 1200);
          }
          return;
        } catch (conversationError) {
          console.error("Employee conversation failed.", conversationError);
          setChatMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content:
                "I couldn’t reach the employee agent service. Please confirm it’s running on port 8001 and try again.",
            },
          ]);
          setAiState("idle");
          return;
        }
      }

      if (isBusiness && currentClientNeedId) {
        const updateResponse = await updateClientNeedFromMessage({
          client_need_id: currentClientNeedId,
          message,
        });
        const questionsResponse = await getClarifyingQuestions({
          client_need_id: currentClientNeedId,
          context: message,
        });

        queryClient.setQueryData(["client-need", currentClientNeedId], updateResponse.client_need);
        queryClient.setQueriesData(
          { queryKey: ["client-needs"], exact: false },
          (old: any) => {
            if (!old?.items) return old;
            return {
              ...old,
              items: old.items.map((item: any) =>
                item.id === updateResponse.client_need.id ? updateResponse.client_need : item
              ),
            };
          }
        );

        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              `Updated client need #${currentClientNeedId.slice(0, 8)}. ` +
              `Completeness: ${updateResponse.profile_completeness}%.`,
          },
        ]);
        if (questionsResponse.questions) {
          setChatMessages((prev) => [...prev, { role: "assistant", content: questionsResponse.questions }]);
        }

        const enrichedResponse: AgentResponse = {
          output: updateResponse.client_need.needs_summary
            ?? updateResponse.client_need.project_description
            ?? "Client need updated.",
          intermediate_steps: [],
          client_need_id: currentClientNeedId,
          completeness_score: updateResponse.profile_completeness,
          missing_fields: updateResponse.missing_fields,
          critical_missing_fields: updateResponse.critical_missing_fields,
          clarifying_questions: questionsResponse.questions || undefined,
        };
        onAgentResult?.(enrichedResponse);
        queryClient.invalidateQueries({ queryKey: ["client-needs"] });
        queryClient.invalidateQueries({ queryKey: ["client-need", currentClientNeedId] });

        setAiState("talking");
        window.setTimeout(() => setAiState("idle"), 1200);
        return;
      }

      const intakeResponse = await uploadText.mutateAsync({
        text_content: message,
        client_name: isBusiness ? userName : undefined,
        source_label: isBusiness ? "business_portal_chat" : "career_portal_chat",
      });

      const agentResponse = await processIntake.mutateAsync({
        intakeId: intakeResponse.id,
        userQuery: message,
      });

      const derivedClientNeedId = extractClientNeedId(agentResponse.intermediate_steps);
      const derivedCompleteness = extractCompletenessScore(agentResponse.intermediate_steps);
      let clarifyingQuestions: string | undefined;
      if (derivedClientNeedId) {
        try {
          const questionsResponse = await getClarifyingQuestions({ client_need_id: derivedClientNeedId });
          clarifyingQuestions = questionsResponse.questions;
        } catch (questionError) {
          console.error("Failed to load clarifying questions.", questionError);
        }
      }
      const enrichedResponse: AgentResponse = {
        ...agentResponse,
        client_need_id: derivedClientNeedId ?? agentResponse.client_need_id,
        completeness_score: derivedCompleteness ?? agentResponse.completeness_score,
        clarifying_questions: clarifyingQuestions,
      };
      setChatMessages((prev) => [...prev, { role: "assistant", content: agentResponse.output }]);
      onAgentResult?.(enrichedResponse);
      if (derivedClientNeedId) {
        setCurrentClientNeedId(derivedClientNeedId);
        onClientNeedCreated?.(derivedClientNeedId);
        queryClient.invalidateQueries({ queryKey: ["client-need", derivedClientNeedId] });
      }
      setAiState("talking");
      window.setTimeout(() => setAiState("idle"), 1500);
    } catch (error) {
      console.error("Chat request failed.", error);
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn’t reach the agent service. Please check the backend is running and try again.",
        },
      ]);
      setAiState("idle");
    }
  }

  function handleStartListening() {
    if (!recognitionRef.current) return;
    recognitionRef.current.start();
  }

  function handleStopListening() {
    if (!recognitionRef.current) return;
    try {
      recognitionRef.current.stop();
    } catch {
      // No-op: stop can throw if not actively listening.
    }
    setAiState("idle");
  }

  async function handleSubmitIntake() {
    setStatusMessage(null);
    try {
      let intakeId: string | null = null;
      let uploadLabel: string | null = null;
      if (currentClientNeedId) {
        setCurrentClientNeedId(null);
      }
      if (intakeFile) {
        setHasConversationStarted(true);
        const response = await uploadFile.mutateAsync({
          file: intakeFile,
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
        });
        intakeId = response.id;
        uploadLabel = `Uploaded file: ${intakeFile.name}`;
      } else if (briefText.trim()) {
        setHasConversationStarted(true);
        const response = await uploadText.mutateAsync({
          text_content: briefText.trim(),
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
          source_label: "business_portal",
        });
        intakeId = response.id;
        uploadLabel = "Uploaded brief text";
      } else {
        setStatusMessage("Add a brief or upload a file to start intake.");
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
          setStatusMessage("Client need created and ready for review.");
        } else {
          setStatusMessage("Intake processed, but client need ID was not returned.");
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
        setStatusMessage("Upload succeeded, but agent processing failed.");
      }
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Failed to process intake.");
    }
  }

  function handleCareerFileUpload(files: FileList | null) {
    if (!files || files.length === 0) return;
    setHasConversationStarted(true);
    const file = files[0];
    setChatMessages((prev) => [...prev, { role: "user", content: `Uploaded file: ${file.name}` }]);
    processEmployeeUpload({
      file,
      employeeProfileId,
      conversationId: employeeConversationId,
    })
      .then((result) => {
        if (result.employee_profile_id) {
          setEmployeeProfileId(result.employee_profile_id);
          queryClient.invalidateQueries({ queryKey: ["employee-profile", result.employee_profile_id] });
          queryClient.invalidateQueries({ queryKey: ["employee-documents", result.employee_profile_id] });
        }
        if (result.output) {
          setChatMessages((prev) => [...prev, { role: "assistant", content: result.output }]);
        }
      })
      .catch((error) => {
        console.error("Employee upload failed.", error);
        setChatMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Failed to process your document. Please try again." },
        ]);
      });
  }
  return (
    <aside className="w-1/2 min-w-[400px] h-full bg-background flex flex-col border-r border-border p-8">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-12">
        <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
          <Zap className="size-4 text-primary-foreground" />
        </div>
        <h2 className="text-foreground text-xl font-bold tracking-tight">Talent Orchestration</h2>
        <span className="bg-success/10 text-success text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
          {isBusiness ? "Business" : "Career"}
        </span>
      </div>

      {/* Welcome Message */}
      <div className="flex-1 min-h-0 flex flex-col gap-6">
        <div className="flex-1 min-h-0 overflow-y-auto pr-1">
          {!hasConversationStarted && (
            <div className="space-y-4">
              <h1 className="text-4xl font-extrabold text-foreground leading-tight">
                Welcome back, {userName.split(" ")[0]}.
              </h1>
              <p className="text-muted-foreground text-lg">
                {isBusiness
                  ? "Your AI business agent is ready. How can I help you staff today?"
                  : "Your AI career assistant is ready. How can I help you grow today?"}
              </p>
            </div>
          )}

          {!hasConversationStarted && (
            <>
              {/* AI Pulse Visualizer */}
              <div className="h-24 flex items-center justify-center gap-1 mt-6">
                {[40, 60, 100, 80, 50, 70].map((height, i) => (
                  <div
                    key={i}
                    className={`w-1 rounded-full transition-colors ${
                      aiState === "listening"
                        ? "bg-success animate-pulse"
                        : aiState === "thinking"
                        ? "bg-warning animate-pulse"
                        : aiState === "talking"
                        ? "bg-primary animate-pulse"
                        : "bg-primary/60"
                    }`}
                    style={{
                      height: `${height}%`,
                      opacity: height / 100,
                      animationDelay: `${i * 0.1}s`,
                    }}
                  />
                ))}
              </div>
              <div className="text-center text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                {aiState === "listening" && "Listening"}
                {aiState === "thinking" && "Thinking"}
                {aiState === "talking" && "Talking"}
                {aiState === "idle" && "Ready"}
              </div>
            </>
          )}

          <div className="mt-6">
            {hasConversationStarted &&
              chatMessages.map((message, idx) => (
                <div
                  key={`${message.role}-${idx}`}
                  className={`flex my-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-card text-foreground border border-border/70"
                    }`}
                  >
                    <span className="block text-[10px] uppercase tracking-wider opacity-70 mb-2">
                      {message.role === "user" ? "You" : "Agent"}
                    </span>
                    <p className="leading-relaxed whitespace-pre-line">{message.content}</p>
                  </div>
              </div>
            ))}
            {hasConversationStarted && aiState !== "idle" && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm bg-card text-foreground border border-border/70">
                  <span className="block text-[10px] uppercase tracking-wider opacity-70 mb-2">Agent</span>
                  <div className="flex items-center gap-4">
                    <div className="h-8 flex items-center gap-1">
                      {[40, 60, 100, 80, 50].map((height, i) => (
                        <div
                          key={i}
                          className={`w-1 rounded-full transition-colors ${
                            aiState === "listening"
                              ? "bg-success animate-pulse"
                              : aiState === "thinking"
                              ? "bg-warning animate-pulse"
                              : "bg-primary animate-pulse"
                          }`}
                          style={{
                            height: `${height}%`,
                            opacity: height / 100,
                            animationDelay: `${i * 0.1}s`,
                          }}
                        />
                      ))}
                    </div>
                    <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                      {aiState === "listening" && "Listening"}
                      {aiState === "thinking" && "Thinking"}
                      {aiState === "talking" && "Talking"}
                    </p>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </div>

        {/* AI Interaction Composer */}
        <div className="bg-card border border-border rounded-xl p-4 shrink-0">
          <Textarea
            className="w-full bg-transparent border-none resize-none h-32 text-base placeholder:text-muted-foreground "
            placeholder={
              isBusiness
                ? "Ask AI to analyze staffing gaps, prioritize roles, or draft a project request..."
                : "Ask AI to analyze your recent project or update your CV..."
            }
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                if (!isChatBusy) {
                  void handleSendMessage();
                }
              }
            }}
          />
          <div className="flex items-center justify-between pt-2 border-t border-border mt-4">
            <div className="flex items-center gap-2">
              {!isBusiness && (
                <input
                  ref={careerFileInputRef}
                  type="file"
                  multiple
                  className="hidden"
                  onChange={(event) => {
                    handleCareerFileUpload(event.target.files);
                    event.currentTarget.value = "";
                  }}
                />
              )}
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-foreground"
                onClick={aiState === "listening" ? handleStopListening : handleStartListening}
                disabled={!recognitionRef.current}
              >
                <Mic className="size-5" />
              </Button>
              {isBusiness ? (
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-foreground"
                  onClick={() => setIntakeOpen(true)}
                >
                  <FileUp className="size-5" />
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-foreground"
                  onClick={() => careerFileInputRef.current?.click()}
                >
                  <FileUp className="size-5" />
                </Button>
              )}
            </div>
            <Button className="font-semibold" onClick={() => handleSendMessage()} disabled={isChatBusy}>
              {isChatBusy ? "Sending..." : "Send Command"}
            </Button>
          </div>
        </div>
        
      </div>

      {isBusiness && (
        <Dialog open={intakeOpen} onOpenChange={setIntakeOpen}>
          <DialogContent className="max-w-xl">
            <DialogHeader>
              <DialogTitle>Client Need Intake</DialogTitle>
              <DialogDescription>
                Upload a brief or paste requirements to create a client need.
              </DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-1 gap-3">
              <Input
                placeholder="Client name (optional)"
                value={clientName}
                onChange={(event) => setClientName(event.target.value)}
              />
              <Input
                placeholder="Client email (optional)"
                value={clientEmail}
                onChange={(event) => setClientEmail(event.target.value)}
              />
              <Textarea
                className="min-h-[140px]"
                placeholder="Paste the project brief or key requirements..."
                value={briefText}
                onChange={(event) => setBriefText(event.target.value)}
              />
              <Input
                type="file"
                accept=".pdf,.wav,.mp3,.ogg,.m4a"
                onChange={(event) => {
                  const file = event.target.files?.[0] || null;
                  setIntakeFile(file);
                  if (file) {
                    setHasConversationStarted(true);
                  }
                }}
              />
              {intakeFile && (
                <p className="text-xs text-muted-foreground">Selected file: {intakeFile.name}</p>
              )}
            </div>
            {statusMessage && <p className="text-xs text-muted-foreground">{statusMessage}</p>}
            <div className="flex items-center justify-end gap-3 pt-2">
              <Button variant="outline" onClick={() => setIntakeOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSubmitIntake} disabled={isSubmitting}>
                {isSubmitting ? "Processing Intake..." : "Process Client Need"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
      

      {/* User Profile */}
      <div className="mt-auto pt-8 flex items-center gap-4 border-t border-border">
        <div 
          className="size-10 rounded-full bg-cover bg-center border border-border"
          style={{ backgroundImage: `url('${userImage}')` }}
        />
        <div className="flex-1 min-w-0">
          <p className="text-foreground text-sm font-semibold truncate">{userName}</p>
          <p className="text-muted-foreground text-xs truncate">{userRole}</p>
        </div>
        <Button onClick={() => navigate("/", { replace: true })} variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="size-5">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" x2="9" y1="12" y2="12" />
          </svg>
        </Button>
      </div>
    </aside>
  );
}
