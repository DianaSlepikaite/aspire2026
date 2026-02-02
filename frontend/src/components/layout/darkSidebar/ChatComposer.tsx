import { RefObject } from "react";
import { Mic, FileUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type AiState = "idle" | "listening" | "thinking" | "talking";

interface ChatComposerProps {
  isBusiness: boolean;
  chatInput: string;
  onChatInputChange: (value: string) => void;
  onSend: () => void;
  isChatBusy: boolean;
  aiState: AiState;
  recognitionAvailable: boolean;
  onStartListening: () => void;
  onStopListening: () => void;
  onOpenIntake: () => void;
  careerFileInputRef: RefObject<HTMLInputElement>;
  onCareerFileChange: (files: FileList | null) => void;
}

export function ChatComposer({
  isBusiness,
  chatInput,
  onChatInputChange,
  onSend,
  isChatBusy,
  aiState,
  recognitionAvailable,
  onStartListening,
  onStopListening,
  onOpenIntake,
  careerFileInputRef,
  onCareerFileChange,
}: ChatComposerProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-4 shrink-0">
      <p className="sr-only" role="status" aria-live="polite">
        {isChatBusy
          ? "Sending message."
          : aiState === "listening"
          ? "Listening."
          : aiState === "thinking"
          ? "Thinking."
          : aiState === "talking"
          ? "Talking."
          : "Ready."}
      </p>
      <p id="chat-input-hint" className="sr-only">
        Press Enter to send. Press Shift plus Enter for a new line.
      </p>
      <Textarea
        className="w-full bg-transparent border-none resize-none h-32 text-base placeholder:text-muted-foreground "
        placeholder={
          isBusiness
            ? "Ask AI to analyze staffing gaps, prioritize roles, or draft a project request..."
            : "Ask AI to analyze your recent project or update your CV..."
        }
        aria-label={isBusiness ? "Business chat input" : "Career chat input"}
        aria-describedby="chat-input-hint"
        value={chatInput}
        onChange={(event) => onChatInputChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!isChatBusy) {
              onSend();
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
              aria-label="Upload document"
              onChange={(event) => {
                onCareerFileChange(event.target.files);
                event.currentTarget.value = "";
              }}
            />
          )}
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-foreground"
            onClick={aiState === "listening" ? onStopListening : onStartListening}
            disabled={!recognitionAvailable}
            aria-label={aiState === "listening" ? "Stop voice input" : "Start voice input"}
            aria-pressed={aiState === "listening"}
          >
            <Mic className="size-5" />
          </Button>
          {isBusiness ? (
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-foreground"
              onClick={onOpenIntake}
              aria-label="Upload client brief"
            >
              <FileUp className="size-5" />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-foreground"
              onClick={() => careerFileInputRef.current?.click()}
              aria-label="Upload document"
            >
              <FileUp className="size-5" />
            </Button>
          )}
        </div>
        <Button className="font-semibold" onClick={onSend} disabled={isChatBusy}>
          {isChatBusy ? "Sending..." : "Send Command"}
        </Button>
      </div>
    </div>
  );
}
