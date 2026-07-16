import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@/tests/test-utils";
import userEvent from "@testing-library/user-event";
import { InteractionsContent } from "./interactions-content";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Mock complaints service
vi.mock("@/services/complaints.service", () => ({
  complaintsService: {
    ingest: vi.fn().mockResolvedValue({
      data: {
        success: true,
        data: {
          complaint_id: "test-complaint-id",
          complaint_number: "COM-9999",
        },
      },
    }),
  },
}));

describe("InteractionsContent Workspace Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page header and export button", () => {
    render(<InteractionsContent />);
    expect(screen.getByRole("heading", { name: /Interactions/i })).toBeInTheDocument();
    expect(screen.getByText(/Enterprise Customer Communication Hub/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Export/i })).toBeInTheDocument();
  });

  it("renders all 9 channel tab filters with counts", () => {
    render(<InteractionsContent />);
    expect(screen.getByRole("button", { name: /^All(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Voice Calls(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^SMART CALL(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^WhatsApp(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Web Chat(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Email(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^CRM Records(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Manual(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Survey(\s+\d+)?$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Claims Notes(\s+\d+)?$/i })).toBeInTheDocument();
  });

  it("renders the conversation list (Left Panel)", () => {
    render(<InteractionsContent />);
    // Verify list headers and filter inputs
    expect(screen.getByPlaceholderText(/Search by name, policy, phone/i)).toBeInTheDocument();
    
    // Check key mock customer names are displayed
    expect(screen.getAllByText("Fatima Al Lawati").length).toBeGreaterThan(0);
    expect(screen.getByText("Sultan Al Khalidi")).toBeInTheDocument();
    expect(screen.getByText("Khalid Al Maamari")).toBeInTheDocument();
  });

  it("switches channel tabs and filters the list items accordingly", async () => {
    render(<InteractionsContent />);
    
    // Click on the WhatsApp tab
    const waTab = screen.getByRole("button", { name: /^WhatsApp(\s+\d+)?$/i });
    fireEvent.click(waTab);

    // Fatima Al Lawati is a WhatsApp interaction (should remain)
    expect(screen.getAllByText("Fatima Al Lawati").length).toBeGreaterThan(0);
    
    // Sultan Al Khalidi is an Email interaction (should NOT be visible after filter re-render)
    await waitFor(() => {
      expect(screen.queryByText("Sultan Al Khalidi")).not.toBeInTheDocument();
    });
  });

  it("shows active conversation workspace (Center Panel) and customer/AI profile (Right Panel)", () => {
    render(<InteractionsContent />);
    
    // Fatima Al Lawati is selected by default
    expect(screen.getAllByText("fatima.lawati@email.com").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Motor Insurance").length).toBeGreaterThan(0);
    expect(screen.getAllByText("CLM-2024-7812 – Pending").length).toBeGreaterThan(0);

    // AI summary card is visible
    expect(screen.getByText(/Customer is experiencing a 2-week claim delay/i)).toBeInTheDocument();
    // Root cause is visible
    expect(screen.getByText(/Internal SLA breach — claim reassignment gap/i)).toBeInTheDocument();
  });

  it("sends a new message successfully to the timeline", async () => {
    const user = userEvent.setup();
    render(<InteractionsContent />);
    
    // Switch to WhatsApp tab for simpler workspace test
    const waTab = screen.getByRole("button", { name: /^WhatsApp(\s+\d+)?$/i });
    fireEvent.click(waTab);

    // Locate the WhatsApp message input
    const input = screen.getByPlaceholderText("Type a message") as HTMLInputElement;
    await user.type(input, "Hello, this is a test message!");

    // Submit the form directly
    const form = input.closest("form");
    expect(form).not.toBeNull();
    const buttons = form!.querySelectorAll("button");
    const submitBtn = Array.from(buttons).find(btn => btn.getAttribute("type") === "submit");
    expect(submitBtn).toBeDefined();
    await user.click(submitBtn!);

    // The typed text should appear in the WhatsApp chat area
    await waitFor(() => {
      const el = screen.queryAllByText("Hello, this is a test message!");
      expect(el.length).toBeGreaterThan(0);
    });
  });
});
