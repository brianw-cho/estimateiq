import React from "react";
import { render, screen, fireEvent, act, waitFor } from "@testing-library/react";
import { ToastProvider, useToast } from "@/components/ui/toast";

// Test component that uses the toast hook
function ToastTestComponent({
  onMount,
}: {
  onMount?: (addToast: ReturnType<typeof useToast>["addToast"]) => void;
}) {
  const { addToast, removeToast, clearToasts, toasts } = useToast();

  React.useEffect(() => {
    if (onMount) {
      onMount(addToast);
    }
  }, [onMount, addToast]);

  return (
    <div>
      <div data-testid="toast-count">{toasts.length}</div>
      <button
        data-testid="add-success"
        onClick={() =>
          addToast({ type: "success", title: "Success!", message: "It worked" })
        }
      >
        Add Success
      </button>
      <button
        data-testid="add-error"
        onClick={() =>
          addToast({ type: "error", title: "Error!", message: "Something failed" })
        }
      >
        Add Error
      </button>
      <button
        data-testid="add-warning"
        onClick={() =>
          addToast({ type: "warning", title: "Warning!", message: "Be careful" })
        }
      >
        Add Warning
      </button>
      <button
        data-testid="add-info"
        onClick={() =>
          addToast({ type: "info", title: "Info!", message: "FYI" })
        }
      >
        Add Info
      </button>
      <button data-testid="clear-all" onClick={clearToasts}>
        Clear All
      </button>
      {toasts.length > 0 && (
        <button
          data-testid="remove-first"
          onClick={() => removeToast(toasts[0].id)}
        >
          Remove First
        </button>
      )}
    </div>
  );
}

describe("ToastProvider", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("should render children", () => {
    render(
      <ToastProvider>
        <div data-testid="child">Hello</div>
      </ToastProvider>
    );

    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("should throw error when useToast is used outside provider", () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      render(<ToastTestComponent />);
    }).toThrow("useToast must be used within a ToastProvider");

    consoleSpy.mockRestore();
  });

  it("should add a toast", () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    expect(screen.getByTestId("toast-count")).toHaveTextContent("0");

    fireEvent.click(screen.getByTestId("add-success"));

    expect(screen.getByTestId("toast-count")).toHaveTextContent("1");
    expect(screen.getByText("Success!")).toBeInTheDocument();
    expect(screen.getByText("It worked")).toBeInTheDocument();
  });

  it("should render different toast types", () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    expect(screen.getByText("Success!")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("add-error"));
    expect(screen.getByText("Error!")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("add-warning"));
    expect(screen.getByText("Warning!")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("add-info"));
    expect(screen.getByText("Info!")).toBeInTheDocument();

    expect(screen.getByTestId("toast-count")).toHaveTextContent("4");
  });

  it("should remove a toast", () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("1");

    fireEvent.click(screen.getByTestId("remove-first"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("0");
  });

  it("should clear all toasts", () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    fireEvent.click(screen.getByTestId("add-error"));
    fireEvent.click(screen.getByTestId("add-warning"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("3");

    fireEvent.click(screen.getByTestId("clear-all"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("0");
  });

  it("should auto-dismiss toast after duration", async () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("1");

    // Fast-forward past the default duration (5000ms)
    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.getByTestId("toast-count")).toHaveTextContent("0");
  });

  it("should respect maxToasts limit", () => {
    render(
      <ToastProvider maxToasts={2}>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    fireEvent.click(screen.getByTestId("add-error"));
    fireEvent.click(screen.getByTestId("add-warning"));

    // Should only have 2 toasts (the most recent ones)
    expect(screen.getByTestId("toast-count")).toHaveTextContent("2");
    expect(screen.queryByText("Success!")).not.toBeInTheDocument();
    expect(screen.getByText("Error!")).toBeInTheDocument();
    expect(screen.getByText("Warning!")).toBeInTheDocument();
  });

  it("should render toast with action button", () => {
    const handleAction = jest.fn();

    function TestWithAction() {
      const { addToast } = useToast();
      return (
        <button
          onClick={() =>
            addToast({
              type: "info",
              title: "Action Toast",
              action: { label: "Click me", onClick: handleAction },
            })
          }
        >
          Add
        </button>
      );
    }

    render(
      <ToastProvider>
        <TestWithAction />
      </ToastProvider>
    );

    fireEvent.click(screen.getByText("Add"));
    expect(screen.getByText("Click me")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Click me"));
    expect(handleAction).toHaveBeenCalled();
  });

  it("should dismiss toast when X button is clicked", () => {
    render(
      <ToastProvider>
        <ToastTestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByTestId("add-success"));
    expect(screen.getByTestId("toast-count")).toHaveTextContent("1");

    // Click the dismiss button
    const dismissButton = screen.getByLabelText("Dismiss notification");
    fireEvent.click(dismissButton);

    expect(screen.getByTestId("toast-count")).toHaveTextContent("0");
  });

  it("should return toast ID from addToast", () => {
    let toastId: string | undefined;

    function TestGetId() {
      const { addToast } = useToast();
      return (
        <button
          onClick={() => {
            toastId = addToast({ type: "success", title: "Test" });
          }}
        >
          Add
        </button>
      );
    }

    render(
      <ToastProvider>
        <TestGetId />
      </ToastProvider>
    );

    fireEvent.click(screen.getByText("Add"));
    expect(toastId).toBeDefined();
    expect(toastId).toMatch(/^toast-/);
  });
});
