import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useEmployeeContext } from "@/context/EmployeeContext";
import {
  AgentResponse,
  type ClientNeed,
  type ClientNeedListResponse,
  extractClientNeedId,
  extractCompletenessScore,
  getClarifyingQuestions,
  updateClientNeedFromMessage,
} from "@/lib/clientNeedApi";
import {
  processEmployeeUpload,
  sendEmployeeMessage,
  startEmployeeConversation,
  synthesizeEmployeeSpeech,
} from "@/lib/employeeApi";

type UploadText = (params: {
  text_content: string;
  client_name?: string;
  client_email?: string;
  source_label?: string;
}) => Promise<{ id: string }>;

type ProcessIntake = (params: { intakeId: string; userQuery?: string }) => Promise<AgentResponse>;

interface UseChatAgentOptions {
  isBusiness: boolean;
  userName: string;
  currentClientNeedId: string | null;
  setCurrentClientNeedId: (id: string | null) => void;
  onClientNeedCreated?: (clientNeedId: string) => void;
  onAgentResult?: (result: AgentResponse) => void;
  uploadText: UploadText;
  processIntake: ProcessIntake;
}

type SpeechRecognitionResultLike = { transcript: string };
type SpeechRecognitionEventLike = { results?: ArrayLike<ArrayLike<SpeechRecognitionResultLike>> };
type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart?: () => void;
  onend?: () => void;
  onerror?: () => void;
  onresult?: (event: SpeechRecognitionEventLike) => void;
  start: () => void;
  stop: () => void;
};

export function useChatAgent({
  isBusiness,
  userName,
  currentClientNeedId,
  setCurrentClientNeedId,
  onClientNeedCreated,
  onAgentResult,
  uploadText,
  processIntake,
}: UseChatAgentOptions) {
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [aiState, setAiState] = useState<"idle" | "listening" | "thinking" | "talking">("idle");
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const handleSendMessageRef = useRef<
    ((messageOverride?: string, messageType?: "text" | "speech") => void) | null
  >(null);
  const isMountedRef = useRef(true);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const careerFileInputRef = useRef<HTMLInputElement | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const queryClient = useQueryClient();
  const {
    employeeProfileId,
    conversationId: employeeConversationId,
    setEmployeeProfileId,
    setConversationId: setEmployeeConversationId,
  } = useEmployeeContext();

  const hasConversationStarted =
    chatMessages.length > 0 || Boolean(currentClientNeedId) || Boolean(employeeProfileId);
  const showWelcome = chatMessages.length === 0;

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognitionImpl =
      (window as Window & {
        SpeechRecognition?: new () => SpeechRecognitionLike;
        webkitSpeechRecognition?: new () => SpeechRecognitionLike;
      }).SpeechRecognition
      ?? (window as Window & { webkitSpeechRecognition?: new () => SpeechRecognitionLike }).webkitSpeechRecognition;
    if (!SpeechRecognitionImpl) return;

    const recognition = new SpeechRecognitionImpl();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setAiState("listening");
    recognition.onend = () => setAiState("idle");
    recognition.onerror = () => setAiState("idle");
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      if (transcript) {
        setChatInput(transcript);
        handleSendMessageRef.current?.(transcript, "speech");
      }
    };

    recognitionRef.current = recognition;
  }, []);

  useEffect(() => {
    if (!hasConversationStarted) return;
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatMessages, aiState, hasConversationStarted]);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // Ignore stop errors on unmount.
        }
      }
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
    };
  }, []);

  async function handleSendMessage(messageOverride?: string, messageType: "text" | "speech" = "text") {
    const message = (messageOverride ?? chatInput).trim();
    if (!message) return;

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
                if (isMountedRef.current) setAiState("idle");
              };
              audio.onerror = () => {
                URL.revokeObjectURL(url);
                if (isMountedRef.current) setAiState("idle");
              };
              void audio.play();
            } catch (error) {
              console.error("Speech synthesis failed.", error);
              setAiState("idle");
            }
          } else {
            setAiState("idle");
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

        const normalizedClientNeed: ClientNeed = {
          ...updateResponse.client_need,
          profile_completeness_score:
            updateResponse.client_need.profile_completeness_score ?? updateResponse.profile_completeness,
        };

        queryClient.setQueryData(["client-need", currentClientNeedId], normalizedClientNeed);
        queryClient.setQueriesData<ClientNeedListResponse>(
          { queryKey: ["client-needs"], exact: false },
          (old) => {
            if (!old?.items) return old;
            return {
              ...old,
              items: old.items.map((item) =>
                item.id === updateResponse.client_need.id ? normalizedClientNeed : item
              ),
            };
          }
        );
        queryClient.invalidateQueries({ queryKey: ["client-need-matches", currentClientNeedId] });

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

        setAiState("idle");
        return;
      }

      const intakeResponse = await uploadText({
        text_content: message,
        client_name: isBusiness ? userName : undefined,
        source_label: isBusiness ? "business_portal_chat" : "career_portal_chat",
      });

      const agentResponse = await processIntake({
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
      setAiState("idle");
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

  handleSendMessageRef.current = handleSendMessage;

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

  function handleCareerFileUpload(files: FileList | null) {
    if (!files || files.length === 0) return;
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

  return {
    chatInput,
    setChatInput,
    chatMessages,
    setChatMessages,
    aiState,
    chatEndRef,
    careerFileInputRef,
    recognitionAvailable: Boolean(recognitionRef.current),
    hasConversationStarted,
    showWelcome,
    handleSendMessage,
    handleStartListening,
    handleStopListening,
    handleCareerFileUpload,
  };
}
