import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/tests/test-utils";
import userEvent from "@testing-library/user-event";
import { InteractionsContent } from "./interactions-content";
import { useAuthStore } from "@/stores/auth.store";

const EMPLOYEE_ID = "33333333-3333-3333-3333-333333333333";
const mockEmployeeUser = {
  id: EMPLOYEE_ID,
  email: "agent@lumay.test",
  full_name: "Test Agent",
  is_active: true,
  is_verified: true,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

// jsdom performs no real layout, so @tanstack/react-virtual would compute a
// zero-height scroll container and render nothing — stub it to render every
// item, which is how the real virtualizer behaves once mounted with real
// dimensions in a browser.
vi.mock("@tanstack/react-virtual", () => ({
  useVirtualizer: ({ count }: { count: number }) => ({
    getTotalSize: () => count * 140,
    getVirtualItems: () =>
      Array.from({ length: count }, (_, index) => ({ index, start: index * 140, key: index })),
  }),
}));

const CONVERSATION_ID = "11111111-1111-1111-1111-111111111111";
const CUSTOMER_ID = "22222222-2222-2222-2222-222222222222";

const mockConversation = {
  id: CONVERSATION_ID,
  created_at: "2026-07-20T10:00:00Z",
  updated_at: "2026-07-20T10:05:00Z",
  customer_id: CUSTOMER_ID,
  policy_id: null,
  complaint_id: null,
  current_status: "active",
  current_channel: "web_chat",
  assigned_employee_id: null,
  ai_handling: true,
  human_handling: false,
  priority: "medium",
};

const mockSummary = {
  id: CONVERSATION_ID,
  customer_id: CUSTOMER_ID,
  complaint_id: null,
  current_status: "active",
  current_channel: "web_chat",
  assigned_employee_id: null,
  priority: "medium",
  updated_at: mockConversation.updated_at,
  customer_name: "Test Customer",
  last_message_preview: "Hello, I need help",
};

const mockTimelineItems = [
  {
    type: "message",
    id: "m1",
    timestamp: "2026-07-20T10:01:00Z",
    sender_type: "customer",
    channel: "web_chat",
    message_type: "text",
    content: "Hello, I need help",
    event_type: null,
    source_domain: null,
    payload: null,
  },
  {
    type: "event",
    id: "e1",
    timestamp: "2026-07-20T10:02:00Z",
    sender_type: null,
    channel: null,
    message_type: null,
    content: null,
    event_type: "complaint.created",
    source_domain: "complaint",
    payload: { complaint_number: "COMP-001" },
  },
];

// vi.mock factories are hoisted above module-level code, so the mock object
// must be created via vi.hoisted rather than referenced from a plain const.
// Method behavior (resolved values) is filled in per-test via beforeEach.
const conversationsServiceMock = vi.hoisted(() => ({
  list: vi.fn(),
  getById: vi.fn(),
  getTimeline: vi.fn(),
  getParticipants: vi.fn().mockResolvedValue({ data: { success: true, data: [] } }),
  getChannels: vi.fn().mockResolvedValue({ data: { success: true, data: [] } }),
  assign: vi.fn(),
  updateStatus: vi.fn(),
  close: vi.fn(),
  setPriority: vi.fn(),
  addMessage: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  addEvent: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  // Phase 4 — ownership, notes, presence/typing
  takeOver: vi.fn(),
  release: vi.fn(),
  transfer: vi.fn(),
  accept: vi.fn(),
  supervisorJoin: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  supervisorLeave: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  getAssignmentHistory: vi.fn().mockResolvedValue({ data: { success: true, data: [] } }),
  updateMessage: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  deleteMessage: vi.fn().mockResolvedValue({ data: { success: true, data: {} } }),
  getPresence: vi.fn().mockResolvedValue({
    data: {
      success: true,
      data: { presence: {}, typing: {}, ai_active: true, conversation_live: true, voice_active: false },
    },
  }),
  postPresence: vi.fn(),
  postTyping: vi.fn(),
  getByExternalRef: vi.fn(),
  streamUrl: () => "http://localhost:8001/api/v1/conversations/stream",
  conversationStreamUrl: (id: string) => `http://localhost:8001/api/v1/conversations/${id}/stream`,
}));

vi.mock("@/services/conversations.service", () => ({
  conversationsService: conversationsServiceMock,
}));

vi.mock("@/services/users.service", () => ({
  usersService: { listByIds: vi.fn().mockResolvedValue({ data: { success: true, data: [] } }) },
}));

vi.mock("@/services/reporting.service", () => ({
  reportingService: {
    getCustomer360: vi.fn().mockResolvedValue({
      data: {
        success: true,
        data: {
          overview: {
            open_complaints: 0,
            conversation_count: 0,
            avg_resolution_seconds: null,
            escalation_count: 0,
          },
        },
      },
    }),
    getCustomerActivity: vi.fn().mockResolvedValue({ data: { success: true, data: { items: [], total: 0, page: 1, page_size: 50 } } }),
    getConversationSummary: vi.fn(),
    getDistributions: vi.fn(),
    getTrends: vi.fn(),
    getEmployeeAnalytics: vi.fn(),
    getSupervisorDashboard: vi.fn(),
    exportUrl: vi.fn().mockReturnValue("#"),
  },
}));

const mockAgentAssistInsight = {
  id: "aa11111-1111-1111-1111-111111111111",
  created_at: "2026-07-20T10:10:00Z",
  updated_at: "2026-07-20T10:10:00Z",
  conversation_id: CONVERSATION_ID,
  message_count_at_generation: 2,
  summary: "Customer is asking about auto insurance coverage options.",
  intent: "Product Inquiry",
  intent_confidence: 0.85,
  sentiment: "neutral",
  sentiment_polarity: 0.1,
  escalation_risk_score: 5,
  escalation_risk_level: "low",
  next_best_actions: [{ action: "Offer Quote", rationale: "Customer wants pricing." }],
  knowledge_articles: [
    { source: "product", id: "p1", title: "Auto Shield", snippet: "Complete auto insurance...", score: 1 },
  ],
  suggested_replies: [
    { type: "clarification", content: "Could you share your vehicle's make and model?" },
  ],
  insights: { repeated_questions: [], missing_info: [], compliance_risks: [], unanswered_questions: [] },
  alerts: [],
  complaint_severity_at_generation: null,
  duration_minutes: 5,
  minutes_since_last_message: 1,
  stalled: false,
};

const agentAssistServiceMock = vi.hoisted(() => ({
  getLatest: vi.fn(),
  getHistory: vi.fn().mockResolvedValue({ data: { success: true, data: [] } }),
  regenerate: vi.fn(),
}));

vi.mock("@/services/agent-assist.service", () => ({
  agentAssistService: agentAssistServiceMock,
}));

vi.mock("@/features/customers/hooks/use-customers", () => ({
  useCustomerProfile: () => ({ data: null, isLoading: false }),
  useCustomerComplaints: () => ({ data: { items: [], total: 0 }, isLoading: false }),
}));

class MockEventSource {
  static instances: MockEventSource[] = [];
  onerror: (() => void) | null = null;
  constructor(public url: string) {
    MockEventSource.instances.push(this);
  }
  addEventListener() {
    /* no-op — SSE push is exercised separately from these render tests */
  }
  close() {
    /* no-op */
  }
}
// @ts-expect-error jsdom has no EventSource implementation
global.EventSource = MockEventSource;

describe("InteractionsContent — Omnichannel Interaction Center", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockEventSource.instances = [];
    useAuthStore.setState({ user: null, isAuthenticated: false });

    conversationsServiceMock.list.mockResolvedValue({
      data: { success: true, data: [mockSummary], total: 1, page: 1, page_size: 100, total_pages: 1 },
    });
    conversationsServiceMock.getById.mockResolvedValue({ data: { success: true, data: mockConversation } });
    conversationsServiceMock.getTimeline.mockResolvedValue({
      data: {
        success: true,
        data: mockTimelineItems,
        total: mockTimelineItems.length,
        page: 1,
        page_size: 200,
        total_pages: 1,
      },
    });
    conversationsServiceMock.assign.mockResolvedValue({ data: { success: true, data: mockConversation } });
    conversationsServiceMock.updateStatus.mockResolvedValue({
      data: { success: true, data: { ...mockConversation, current_status: "resolved" } },
    });
    conversationsServiceMock.close.mockResolvedValue({
      data: { success: true, data: { ...mockConversation, current_status: "closed" } },
    });
    conversationsServiceMock.setPriority.mockResolvedValue({ data: { success: true, data: mockConversation } });
    agentAssistServiceMock.getLatest.mockResolvedValue({
      data: { success: true, data: mockAgentAssistInsight },
    });
    conversationsServiceMock.takeOver.mockResolvedValue({
      data: {
        success: true,
        data: {
          ...mockConversation,
          current_status: "human_handling",
          ai_handling: false,
          human_handling: true,
          assigned_employee_id: "33333333-3333-3333-3333-333333333333",
        },
      },
    });
    conversationsServiceMock.release.mockResolvedValue({
      data: {
        success: true,
        data: { ...mockConversation, current_status: "ai_handling", ai_handling: true, human_handling: false, assigned_employee_id: null },
      },
    });
    conversationsServiceMock.transfer.mockResolvedValue({ data: { success: true, data: mockConversation } });
    conversationsServiceMock.accept.mockResolvedValue({ data: { success: true, data: mockConversation } });
  });

  it("renders the page header", () => {
    render(<InteractionsContent />);
    expect(screen.getByRole("heading", { name: /Interactions/i })).toBeInTheDocument();
  });

  it("renders all 8 spec'd status tabs in the queue panel", () => {
    render(<InteractionsContent />);
    for (const label of [
      "Live",
      "Active",
      "Waiting for Agent",
      "AI Handling",
      "Human Handling",
      "Escalated",
      "Resolved",
      "Closed",
    ]) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }
  });

  it("loads conversations from the real API, not mock data", async () => {
    render(<InteractionsContent />);
    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    expect(conversationsServiceMock.list).toHaveBeenCalled();
    expect(screen.getByText(/Hello, I need help/)).toBeInTheDocument();
  });

  it("selecting a conversation shows its merged timeline — messages and complaint events together", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));

    await waitFor(() => {
      expect(conversationsServiceMock.getTimeline).toHaveBeenCalledWith(CONVERSATION_ID);
    });
    // The customer message and the complaint event render in the SAME
    // timeline — never a separate voice/complaint panel.
    await waitFor(() => {
      expect(screen.getAllByText(/Hello, I need help/).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Complaint.*Created/i)).toBeInTheDocument();
  });

  it("switching status tabs re-queries the API with the new status filter", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: "Escalated" }));

    await waitFor(() => {
      expect(conversationsServiceMock.list).toHaveBeenCalledWith(
        expect.objectContaining({ status: "escalated" }),
      );
    });
  });

  it("assigning an unowned conversation via Assign/Transfer takes it over (AI→Human)", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));
    await waitFor(() => expect(screen.getByRole("button", { name: /Assign \/ Transfer/i })).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /Assign \/ Transfer/i }));
    const input = screen.getByPlaceholderText("employee-uuid");
    await user.type(input, EMPLOYEE_ID);
    await user.click(screen.getByRole("button", { name: "Go" }));

    // mockConversation has no assigned_employee_id yet, so the toolbar
    // routes to take-over (AI→Human), not the bare transfer endpoint.
    await waitFor(() => {
      expect(conversationsServiceMock.takeOver).toHaveBeenCalledWith(CONVERSATION_ID, {
        employee_id: EMPLOYEE_ID,
      });
    });
  });

  it("assigning an already-owned conversation via Assign/Transfer calls transfer", async () => {
    conversationsServiceMock.getById.mockResolvedValue({
      data: { success: true, data: { ...mockConversation, assigned_employee_id: EMPLOYEE_ID, human_handling: true, ai_handling: false, current_status: "human_handling" } },
    });
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));
    await waitFor(() => expect(screen.getByRole("button", { name: /Assign \/ Transfer/i })).toBeInTheDocument());

    const otherEmployeeId = "44444444-4444-4444-4444-444444444444";
    await user.click(screen.getByRole("button", { name: /Assign \/ Transfer/i }));
    const input = screen.getByPlaceholderText("employee-uuid");
    await user.type(input, otherEmployeeId);
    await user.click(screen.getByRole("button", { name: "Go" }));

    await waitFor(() => {
      expect(conversationsServiceMock.transfer).toHaveBeenCalledWith(CONVERSATION_ID, {
        employee_id: otherEmployeeId,
      });
    });
  });

  it("Take Over calls the take-over API and Release calls the release API", async () => {
    useAuthStore.setState({ user: mockEmployeeUser, isAuthenticated: true });
    // Initial load is unowned/AI-handled; after take-over's invalidation
    // triggers a refetch, the conversation comes back human-handled and
    // owned by the current user — the toolbar swaps to Release.
    conversationsServiceMock.getById
      .mockResolvedValueOnce({ data: { success: true, data: mockConversation } })
      .mockResolvedValue({
        data: {
          success: true,
          data: {
            ...mockConversation,
            current_status: "human_handling",
            ai_handling: false,
            human_handling: true,
            assigned_employee_id: EMPLOYEE_ID,
          },
        },
      });

    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));

    const takeOverButton = await screen.findByRole("button", { name: /Take Over/i });
    await user.click(takeOverButton);

    await waitFor(() => {
      expect(conversationsServiceMock.takeOver).toHaveBeenCalledWith(CONVERSATION_ID, {
        employee_id: EMPLOYEE_ID,
      });
    });

    const releaseButton = await screen.findByRole("button", { name: /Release to AI/i });
    await user.click(releaseButton);

    await waitFor(() => {
      expect(conversationsServiceMock.release).toHaveBeenCalledWith(CONVERSATION_ID);
    });
  });

  it("closing a conversation calls the close API and the timeline stays visible", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));
    await waitFor(() => expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: "Close" }));

    await waitFor(() => {
      expect(conversationsServiceMock.close).toHaveBeenCalledWith(CONVERSATION_ID);
    });
    // Timeline content remains rendered/accessible after closing.
    expect(screen.getAllByText(/Hello, I need help/).length).toBeGreaterThan(0);
  });

  it("Agent Assist tab shows the AI copilot's summary, intent, and suggested replies", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));
    await waitFor(() => expect(screen.getByText("Customer 360")).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /Agent Assist/i }));

    await waitFor(() => {
      expect(agentAssistServiceMock.getLatest).toHaveBeenCalledWith(CONVERSATION_ID);
    });
    expect(await screen.findByText(mockAgentAssistInsight.summary)).toBeInTheDocument();
    expect(screen.getByText("Product Inquiry")).toBeInTheDocument();
    expect(screen.getByText(mockAgentAssistInsight.suggested_replies[0].content)).toBeInTheDocument();
  });

  it("accepting a suggested reply populates the compose bar (never sends automatically)", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);

    await waitFor(() => expect(screen.getByText("Test Customer")).toBeInTheDocument());
    await user.click(screen.getByText("Test Customer"));
    await user.click(screen.getByRole("button", { name: /Agent Assist/i }));

    const draft = mockAgentAssistInsight.suggested_replies[0].content;
    await waitFor(() => expect(screen.getByText(draft)).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: /Accept/i }));

    const composeInput = screen.getByPlaceholderText(/Type a reply to the customer/i) as HTMLTextAreaElement;
    await waitFor(() => expect(composeInput.value).toBe(draft));
    // Populating the draft must not itself call addMessage — sending is
    // still a separate, explicit employee action.
    expect(conversationsServiceMock.addMessage).not.toHaveBeenCalled();
  });
});
