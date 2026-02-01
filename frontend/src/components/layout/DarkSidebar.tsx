import { useEffect, useRef, useState } from "react";
import { Mic, FileUp, PlusCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from "react-router-dom";
import { useProcessIntake, useUploadIntakeFile, useUploadIntakeText } from "@/hooks/useClientNeeds";
import { AgentResponse } from "@/lib/clientNeedApi";
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
  onClientNeedCreated?: (clientNeedId: string) => void;
  onAgentResult?: (result: AgentResponse) => void;
}

export function DarkSidebar({ 
  userName = "Sarah Jenkins",
  userRole = "Senior Project Manager",
  userImage = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face",
  variant = "career",
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
  const recognitionRef = useRef<any>(null);

  const uploadText = useUploadIntakeText();
  const uploadFile = useUploadIntakeFile();
  const processIntake = useProcessIntake();

  const isSubmitting = uploadText.isPending || uploadFile.isPending || processIntake.isPending;
  const isChatBusy = isSubmitting;

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
        void handleSendMessage(transcript);
      }
    };

    recognitionRef.current = recognition;
  }, []);

  async function handleSendMessage(messageOverride?: string) {
    const message = (messageOverride ?? chatInput).trim();
    if (!message) return;

    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatInput("");
    setAiState("thinking");

    try {
      const intakeResponse = await uploadText.mutateAsync({
        text_content: message,
        client_name: isBusiness ? userName : undefined,
        source_label: isBusiness ? "business_portal_chat" : "career_portal_chat",
      });

      const agentResponse = await processIntake.mutateAsync({
        intakeId: intakeResponse.id,
        userQuery: message,
      });

      setChatMessages((prev) => [...prev, { role: "assistant", content: agentResponse.output }]);
      onAgentResult?.(agentResponse);
      if (agentResponse.client_need_id) {
        onClientNeedCreated?.(agentResponse.client_need_id);
      }
      setAiState("talking");
      window.setTimeout(() => setAiState("idle"), 1500);
    } catch {
      setAiState("idle");
    }
  }

  function handleStartListening() {
    if (!recognitionRef.current) return;
    recognitionRef.current.start();
  }

  function extractClientNeedId(intermediateSteps: Array<{ step: string; details?: Record<string, unknown> }>) {
    const saved = intermediateSteps.find((step) => step.step === "save_client_need");
    const id = saved?.details?.client_need_id;
    return typeof id === "string" ? id : null;
  }

  async function handleSubmitIntake() {
    setStatusMessage(null);
    try {
      let intakeId: string | null = null;
      if (intakeFile) {
        const response = await uploadFile.mutateAsync({
          file: intakeFile,
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
        });
        intakeId = response.id;
      } else if (briefText.trim()) {
        const response = await uploadText.mutateAsync({
          text_content: briefText.trim(),
          client_name: clientName || undefined,
          client_email: clientEmail || undefined,
          source_label: "business_portal",
        });
        intakeId = response.id;
      } else {
        setStatusMessage("Add a brief or upload a file to start intake.");
        return;
      }

      const agentResponse = await processIntake.mutateAsync({
        intakeId,
        userQuery: briefText.trim() || undefined,
      });
      const clientNeedId = extractClientNeedId(agentResponse.intermediate_steps);

      if (clientNeedId) {
        onClientNeedCreated?.(clientNeedId);
        setStatusMessage("Client need created and ready for review.");
        setIntakeOpen(false);
      } else {
        setStatusMessage("Intake processed, but client need ID was not returned.");
      }

      setBriefText("");
      setIntakeFile(null);
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Failed to process intake.");
    }
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
      <div className="flex-1 flex flex-col justify-between gap-8">
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

        {/* AI Pulse Visualizer */}
        <div className="h-24 flex items-center justify-center gap-1">
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

        <div className="bg-card border border-border rounded-xl p-4 space-y-3 max-h-64 overflow-y-auto">
          {chatMessages.length === 0 && (
            <p className="text-xs text-muted-foreground">
              Start a conversation to build a profile or clarify staffing needs.
            </p>
          )}
          {chatMessages.map((message, idx) => (
            <div
              key={`${message.role}-${idx}`}
              className={`text-sm p-3 rounded-lg ${
                message.role === "user" ? "bg-secondary/60 text-foreground" : "bg-primary/10 text-foreground"
              }`}
            >
              <span className="block text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                {message.role === "user" ? "You" : "AI"}
              </span>
              {message.content}
            </div>
          ))}
        </div>

        {/* AI Interaction Composer */}
        <div className="bg-card border border-border rounded-xl p-4">
          <Textarea
            className="w-full bg-transparent border-none resize-none h-32 text-base placeholder:text-muted-foreground focus-visible:ring-0"
            placeholder={
              isBusiness
                ? "Ask AI to analyze staffing gaps, prioritize roles, or draft a project request..."
                : "Ask AI to analyze your recent project or update your CV..."
            }
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
          />
          <div className="flex items-center justify-between pt-2 border-t border-border mt-4">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-foreground"
                onClick={handleStartListening}
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
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
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
                onChange={(event) => setIntakeFile(event.target.files?.[0] || null)}
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
