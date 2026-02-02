import { RefObject } from "react";

type ChatMessage = { role: "user" | "assistant"; content: string };
type AiState = "idle" | "listening" | "thinking" | "talking";

interface ChatThreadProps {
  showWelcome: boolean;
  userName: string;
  isBusiness: boolean;
  messages: ChatMessage[];
  aiState: AiState;
  hasConversationStarted: boolean;
  chatEndRef: RefObject<HTMLDivElement>;
}

export function ChatThread({
  showWelcome,
  userName,
  isBusiness,
  messages,
  aiState,
  hasConversationStarted,
  chatEndRef,
}: ChatThreadProps) {
  return (
    <div className="flex-1 min-h-0 overflow-y-auto pr-1" role="log" aria-live="polite" aria-relevant="additions">
      {showWelcome && (
        <div className="flex flex-col">
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

          <div className="flex flex-1 items-center justify-center" />
        </div>
      )}

      <div className="mt-6">
        {hasConversationStarted && (
          <ul className="space-y-3">
            {messages.map((message, idx) => (
              <li
                key={`${message.role}-${idx}`}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                aria-label={message.role === "user" ? "User message" : "Agent message"}
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
              </li>
            ))}
            {hasConversationStarted && aiState !== "idle" && (
              <li className="flex justify-start" aria-label="Agent status">
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
              </li>
            )}
          </ul>
        )}
        <div ref={chatEndRef} />
      </div>
    </div>
  );
}
