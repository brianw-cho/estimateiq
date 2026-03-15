import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  DemoBanner,
  DemoScenarioSelector,
  DemoModeProvider,
  useDemoMode,
  DEFAULT_DEMO_SCENARIOS,
} from "@/components/ui/demo-banner";

describe("DemoBanner", () => {
  it("should not render when scenarioId is null", () => {
    const { container } = render(<DemoBanner scenarioId={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("should render when scenarioId is provided", () => {
    render(<DemoBanner scenarioId="oil-change" />);
    expect(screen.getByText("Demo Mode")).toBeInTheDocument();
  });

  it("should display the active scenario name", () => {
    render(<DemoBanner scenarioId="oil-change" />);
    expect(screen.getByText("Oil Change")).toBeInTheDocument();
  });

  it("should call onReset when reset button is clicked", () => {
    const onReset = jest.fn();
    render(<DemoBanner scenarioId="oil-change" onReset={onReset} />);

    fireEvent.click(screen.getByText("Reset"));
    expect(onReset).toHaveBeenCalled();
  });

  it("should call onClose when close button is clicked", () => {
    const onClose = jest.fn();
    render(<DemoBanner scenarioId="oil-change" onClose={onClose} />);

    fireEvent.click(screen.getByLabelText("Exit demo mode"));
    expect(onClose).toHaveBeenCalled();
  });

  it("should toggle scenario details when clicked", () => {
    render(<DemoBanner scenarioId="oil-change" />);

    // Initially details should be hidden
    expect(
      screen.queryByText(/Annual oil change and filter replacement/)
    ).not.toBeInTheDocument();

    // Click to show details
    fireEvent.click(screen.getByText("Show details"));
    expect(
      screen.getByText(/Annual oil change and filter replacement/)
    ).toBeInTheDocument();

    // Click to hide details
    fireEvent.click(screen.getByText("Hide details"));
    expect(
      screen.queryByText(/Annual oil change and filter replacement/)
    ).not.toBeInTheDocument();
  });

  it("should have proper accessibility attributes", () => {
    render(<DemoBanner scenarioId="oil-change" />);

    const banner = screen.getByRole("banner");
    expect(banner).toHaveAttribute("aria-label", "Demo mode indicator");
  });

  it("should use custom scenarios when provided", () => {
    const customScenarios = [
      { id: "custom", name: "Custom Scenario", description: "A custom test" },
    ];

    render(<DemoBanner scenarioId="custom" scenarios={customScenarios} />);
    expect(screen.getByText("Custom Scenario")).toBeInTheDocument();
  });

  it("should apply custom className", () => {
    const { container } = render(
      <DemoBanner scenarioId="oil-change" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("should not show reset button when onReset is not provided", () => {
    render(<DemoBanner scenarioId="oil-change" />);
    expect(screen.queryByText("Reset")).not.toBeInTheDocument();
  });

  it("should not show close button when onClose is not provided", () => {
    render(<DemoBanner scenarioId="oil-change" />);
    expect(screen.queryByLabelText("Exit demo mode")).not.toBeInTheDocument();
  });
});

describe("DemoScenarioSelector", () => {
  it("should render all default scenarios", () => {
    render(<DemoScenarioSelector onSelect={jest.fn()} />);

    DEFAULT_DEMO_SCENARIOS.forEach((scenario) => {
      expect(screen.getByText(scenario.name)).toBeInTheDocument();
      expect(screen.getByText(scenario.description)).toBeInTheDocument();
    });
  });

  it("should call onSelect with scenario id when clicked", () => {
    const onSelect = jest.fn();
    render(<DemoScenarioSelector onSelect={onSelect} />);

    fireEvent.click(screen.getByText("Oil Change"));
    expect(onSelect).toHaveBeenCalledWith("oil-change");
  });

  it("should use custom scenarios when provided", () => {
    const customScenarios = [
      { id: "test1", name: "Test 1", description: "First test" },
      { id: "test2", name: "Test 2", description: "Second test" },
    ];
    const onSelect = jest.fn();

    render(
      <DemoScenarioSelector scenarios={customScenarios} onSelect={onSelect} />
    );

    expect(screen.getByText("Test 1")).toBeInTheDocument();
    expect(screen.getByText("Test 2")).toBeInTheDocument();
    expect(screen.queryByText("Oil Change")).not.toBeInTheDocument();
  });

  it("should apply custom className", () => {
    const { container } = render(
      <DemoScenarioSelector onSelect={jest.fn()} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass("custom-class");
  });
});

describe("DemoModeProvider and useDemoMode", () => {
  // Test component that uses the hook
  function TestComponent() {
    const { isDemo, scenarioId, setScenarioId, exitDemo } = useDemoMode();
    return (
      <div>
        <div data-testid="is-demo">{isDemo ? "yes" : "no"}</div>
        <div data-testid="scenario-id">{scenarioId || "none"}</div>
        <button data-testid="set-demo" onClick={() => setScenarioId("test")}>
          Set Demo
        </button>
        <button data-testid="exit-demo" onClick={exitDemo}>
          Exit Demo
        </button>
      </div>
    );
  }

  it("should throw error when used outside provider", () => {
    const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow("useDemoMode must be used within a DemoModeProvider");

    consoleSpy.mockRestore();
  });

  it("should start with no demo when initialScenarioId is not provided", () => {
    render(
      <DemoModeProvider>
        <TestComponent />
      </DemoModeProvider>
    );

    expect(screen.getByTestId("is-demo")).toHaveTextContent("no");
    expect(screen.getByTestId("scenario-id")).toHaveTextContent("none");
  });

  it("should start with demo when initialScenarioId is provided", () => {
    render(
      <DemoModeProvider initialScenarioId="oil-change">
        <TestComponent />
      </DemoModeProvider>
    );

    expect(screen.getByTestId("is-demo")).toHaveTextContent("yes");
    expect(screen.getByTestId("scenario-id")).toHaveTextContent("oil-change");
  });

  it("should allow setting demo scenario", () => {
    render(
      <DemoModeProvider>
        <TestComponent />
      </DemoModeProvider>
    );

    fireEvent.click(screen.getByTestId("set-demo"));

    expect(screen.getByTestId("is-demo")).toHaveTextContent("yes");
    expect(screen.getByTestId("scenario-id")).toHaveTextContent("test");
  });

  it("should allow exiting demo mode", () => {
    render(
      <DemoModeProvider initialScenarioId="oil-change">
        <TestComponent />
      </DemoModeProvider>
    );

    fireEvent.click(screen.getByTestId("exit-demo"));

    expect(screen.getByTestId("is-demo")).toHaveTextContent("no");
    expect(screen.getByTestId("scenario-id")).toHaveTextContent("none");
  });
});

describe("DEFAULT_DEMO_SCENARIOS", () => {
  it("should have the expected number of scenarios", () => {
    expect(DEFAULT_DEMO_SCENARIOS).toHaveLength(5);
  });

  it("should have required fields for each scenario", () => {
    DEFAULT_DEMO_SCENARIOS.forEach((scenario) => {
      expect(scenario).toHaveProperty("id");
      expect(scenario).toHaveProperty("name");
      expect(scenario).toHaveProperty("description");
      expect(typeof scenario.id).toBe("string");
      expect(typeof scenario.name).toBe("string");
      expect(typeof scenario.description).toBe("string");
    });
  });

  it("should have unique IDs", () => {
    const ids = DEFAULT_DEMO_SCENARIOS.map((s) => s.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });
});
