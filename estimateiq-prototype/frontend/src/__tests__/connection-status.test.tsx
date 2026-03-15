import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import {
  ConnectionStatus,
  ConnectionIndicator,
  useConnectionStatus,
} from "@/components/ui/connection-status";
import * as api from "@/lib/api";

// Mock the API module
jest.mock("@/lib/api", () => ({
  checkHealth: jest.fn(),
}));

const mockCheckHealth = api.checkHealth as jest.MockedFunction<
  typeof api.checkHealth
>;

// Test component for the hook
function TestHookComponent({
  onStateChange,
}: {
  onStateChange?: (state: "connected" | "disconnected" | "checking") => void;
}) {
  const { state, lastChecked, error, refresh } = useConnectionStatus(
    0, // disable automatic checks for testing
    onStateChange
  );

  return (
    <div>
      <div data-testid="state">{state}</div>
      <div data-testid="error">{error || "none"}</div>
      <div data-testid="lastChecked">
        {lastChecked ? "checked" : "not checked"}
      </div>
      <button data-testid="refresh" onClick={refresh}>
        Refresh
      </button>
    </div>
  );
}

describe("useConnectionStatus", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("should start in checking state", async () => {
    mockCheckHealth.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ status: "healthy" }), 100))
    );

    render(<TestHookComponent />);

    // Initially should be checking
    expect(screen.getByTestId("state")).toHaveTextContent("checking");
  });

  it("should transition to connected on successful health check", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<TestHookComponent />);

    await waitFor(() => {
      expect(screen.getByTestId("state")).toHaveTextContent("connected");
    });
    expect(screen.getByTestId("error")).toHaveTextContent("none");
    expect(screen.getByTestId("lastChecked")).toHaveTextContent("checked");
  });

  it("should transition to disconnected on failed health check", async () => {
    mockCheckHealth.mockRejectedValueOnce(new Error("Connection refused"));

    render(<TestHookComponent />);

    await waitFor(() => {
      expect(screen.getByTestId("state")).toHaveTextContent("disconnected");
    });
    expect(screen.getByTestId("error")).toHaveTextContent("Connection refused");
    expect(screen.getByTestId("lastChecked")).toHaveTextContent("checked");
  });

  it("should call onStateChange callback", async () => {
    const onStateChange = jest.fn();
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<TestHookComponent onStateChange={onStateChange} />);

    await waitFor(() => {
      expect(onStateChange).toHaveBeenCalledWith("connected");
    });
  });

  it("should refresh connection on button click", async () => {
    mockCheckHealth
      .mockRejectedValueOnce(new Error("First check failed"))
      .mockResolvedValueOnce({ status: "healthy" });

    render(<TestHookComponent />);

    // Wait for initial disconnected state
    await waitFor(() => {
      expect(screen.getByTestId("state")).toHaveTextContent("disconnected");
    });

    // Click refresh
    await act(async () => {
      screen.getByTestId("refresh").click();
    });

    // Should now be connected
    await waitFor(() => {
      expect(screen.getByTestId("state")).toHaveTextContent("connected");
    });
  });
});

describe("ConnectionStatus", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render with label by default", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<ConnectionStatus checkInterval={0} />);

    await waitFor(() => {
      expect(screen.getByText("Connected")).toBeInTheDocument();
    });
  });

  it("should hide label when showLabel is false", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<ConnectionStatus checkInterval={0} showLabel={false} />);

    await waitFor(() => {
      expect(screen.queryByText("Connected")).not.toBeInTheDocument();
    });
  });

  it("should show retry button when disconnected", async () => {
    mockCheckHealth.mockRejectedValueOnce(new Error("Failed"));

    render(<ConnectionStatus checkInterval={0} />);

    await waitFor(() => {
      expect(screen.getByText("Retry")).toBeInTheDocument();
    });
  });

  it("should apply custom className", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    const { container } = render(
      <ConnectionStatus checkInterval={0} className="custom-class" />
    );

    await waitFor(() => {
      expect(container.firstChild).toHaveClass("custom-class");
    });
  });
});

describe("ConnectionIndicator", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render compact indicator", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<ConnectionIndicator />);

    await waitFor(() => {
      expect(screen.getByText("connected")).toBeInTheDocument();
    });
  });

  it("should have proper accessibility attributes", async () => {
    mockCheckHealth.mockResolvedValueOnce({ status: "healthy" });

    render(<ConnectionIndicator />);

    await waitFor(() => {
      const indicator = screen.getByRole("status");
      expect(indicator).toBeInTheDocument();
      expect(indicator).toHaveAttribute(
        "aria-label",
        "API connection status: connected"
      );
    });
  });

  it("should show disconnected state", async () => {
    mockCheckHealth.mockRejectedValueOnce(new Error("Failed"));

    render(<ConnectionIndicator />);

    await waitFor(() => {
      expect(screen.getByText("disconnected")).toBeInTheDocument();
    });
  });
});
