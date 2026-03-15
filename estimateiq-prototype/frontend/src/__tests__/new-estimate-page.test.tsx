import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import NewEstimatePage from "@/app/estimate/new/page";
import { ToastProvider } from "@/components/ui/toast";
import * as api from "@/lib/api";

// Mock the API module
jest.mock("@/lib/api", () => ({
  generateEstimate: jest.fn(),
  checkHealth: jest.fn(),
}));

// Mock next/navigation
const mockPush = jest.fn();
let mockSearchParamsValue = new URLSearchParams();

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => mockSearchParamsValue,
  useParams: () => ({}),
  usePathname: () => "/estimate/new",
}));

const mockCheckHealth = api.checkHealth as jest.MockedFunction<
  typeof api.checkHealth
>;

// Wrapper with providers
function renderWithProviders(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

describe("NewEstimatePage - Basic Rendering", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCheckHealth.mockResolvedValue({ status: "healthy" });
    mockSearchParamsValue = new URLSearchParams();
  });

  it("should render vessel form initially", () => {
    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Create New Estimate")).toBeInTheDocument();
    expect(screen.getByText("Enter vessel information")).toBeInTheDocument();
  });

  it("should render step indicator with 3 steps", () => {
    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("should render vessel form fields", () => {
    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Vessel Information")).toBeInTheDocument();
    expect(screen.getByText(/Length Overall/)).toBeInTheDocument();
    expect(screen.getByText(/Year Built/)).toBeInTheDocument();
    expect(screen.getByText(/Engine Make/)).toBeInTheDocument();
    expect(screen.getByText(/Engine Model/)).toBeInTheDocument();
  });

  it("should render continue button", () => {
    renderWithProviders(<NewEstimatePage />);

    expect(
      screen.getByRole("button", { name: /continue to service/i })
    ).toBeInTheDocument();
  });
});

describe("NewEstimatePage - Demo Mode", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCheckHealth.mockResolvedValue({ status: "healthy" });
  });

  it("should show demo banner when demo param is present", () => {
    mockSearchParamsValue = new URLSearchParams("demo=oil-change");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Demo Mode")).toBeInTheDocument();
    expect(screen.getByText("Oil Change")).toBeInTheDocument();
  });

  it("should show Show details link in demo banner", () => {
    mockSearchParamsValue = new URLSearchParams("demo=oil-change");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Show details")).toBeInTheDocument();
  });

  it("should show Reset button in demo mode", () => {
    mockSearchParamsValue = new URLSearchParams("demo=oil-change");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Reset")).toBeInTheDocument();
  });

  it("should show Exit demo button in demo mode", () => {
    mockSearchParamsValue = new URLSearchParams("demo=oil-change");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByLabelText("Exit demo mode")).toBeInTheDocument();
  });

  it("should not show demo banner without demo param", () => {
    mockSearchParamsValue = new URLSearchParams();

    renderWithProviders(<NewEstimatePage />);

    expect(screen.queryByText("Demo Mode")).not.toBeInTheDocument();
  });

  it("should pre-fill vessel data in demo mode", async () => {
    mockSearchParamsValue = new URLSearchParams("demo=oil-change");

    renderWithProviders(<NewEstimatePage />);

    // Oil change demo should pre-fill LOA of 28
    const loaInput = screen.getByPlaceholderText("e.g., 28") as HTMLInputElement;
    await waitFor(() => {
      expect(loaInput.value).toBe("28");
    });
  });
});

describe("NewEstimatePage - Different Demo Scenarios", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCheckHealth.mockResolvedValue({ status: "healthy" });
  });

  it("should handle bottom-paint demo", () => {
    mockSearchParamsValue = new URLSearchParams("demo=bottom-paint");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Bottom Paint")).toBeInTheDocument();
  });

  it("should handle winterization demo", () => {
    mockSearchParamsValue = new URLSearchParams("demo=winterization");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Winterization")).toBeInTheDocument();
  });

  it("should handle diagnostic demo", () => {
    mockSearchParamsValue = new URLSearchParams("demo=diagnostic");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Diagnostic")).toBeInTheDocument();
  });

  it("should handle unusual demo", () => {
    mockSearchParamsValue = new URLSearchParams("demo=unusual");

    renderWithProviders(<NewEstimatePage />);

    expect(screen.getByText("Unusual Vessel")).toBeInTheDocument();
  });
});
