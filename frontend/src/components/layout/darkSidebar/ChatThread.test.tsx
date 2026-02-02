import { render, screen } from "@testing-library/react";
import { ChatThread } from "@/components/layout/darkSidebar/ChatThread";


describe("ChatThread", () => {
  it("renders welcome message when no conversation", () => {
    render(
      <ChatThread
        showWelcome
        userName="Sarah Jenkins"
        isBusiness={false}
        messages={[]}
        aiState="idle"
        hasConversationStarted={false}
        chatEndRef={{ current: null }}
      />
    );

    expect(screen.getByText(/Welcome back, Sarah/)).toBeInTheDocument();
  });

  it("renders messages", () => {
    render(
      <ChatThread
        showWelcome={false}
        userName="Sarah Jenkins"
        isBusiness
        messages={[{ role: "user", content: "Hello" }]}
        aiState="idle"
        hasConversationStarted
        chatEndRef={{ current: null }}
      />
    );

    expect(screen.getByText("Hello")).toBeInTheDocument();
  });
});
