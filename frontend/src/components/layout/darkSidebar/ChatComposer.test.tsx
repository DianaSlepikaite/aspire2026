import { render, screen, fireEvent } from "@testing-library/react";
import { ChatComposer } from "@/components/layout/darkSidebar/ChatComposer";
import { vi } from "vitest";


describe("ChatComposer", () => {
  it("calls onSend on Enter", () => {
    const onSend = vi.fn();
    render(
      <ChatComposer
        isBusiness={false}
        chatInput="Hello"
        onChatInputChange={vi.fn()}
        onSend={onSend}
        isChatBusy={false}
        aiState="idle"
        recognitionAvailable={false}
        onStartListening={vi.fn()}
        onStopListening={vi.fn()}
        onOpenIntake={vi.fn()}
        careerFileInputRef={{ current: null }}
        onCareerFileChange={vi.fn()}
      />
    );

    const input = screen.getByLabelText("Career chat input");
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSend).toHaveBeenCalled();
  });
});
