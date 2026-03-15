"use client";

import * as React from "react";
import { X, RotateCcw, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

// ============================================================================
// Demo Banner Types
// ============================================================================

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
}

interface DemoBannerProps {
  /** The active demo scenario ID */
  scenarioId: string | null;
  /** Available demo scenarios */
  scenarios?: DemoScenario[];
  /** Callback when reset is clicked */
  onReset?: () => void;
  /** Callback when close is clicked */
  onClose?: () => void;
  /** Custom class name */
  className?: string;
}

// ============================================================================
// Default Demo Scenarios
// ============================================================================

export const DEFAULT_DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "oil-change",
    name: "Oil Change",
    description: "Annual oil change and filter replacement for a 28' Volvo D4 cabin cruiser",
  },
  {
    id: "bottom-paint",
    name: "Bottom Paint",
    description: "Hull cleaning and bottom paint for a 32' sailboat",
  },
  {
    id: "winterization",
    name: "Winterization",
    description: "Full winterization package for a 22' MerCruiser runabout",
  },
  {
    id: "diagnostic",
    name: "Diagnostic",
    description: "Troubleshoot no-start condition on a 24' Yamaha center console",
  },
  {
    id: "unusual",
    name: "Unusual Vessel",
    description: "Engine service for a 45' custom vessel with Mercury C9",
  },
];

// ============================================================================
// Demo Banner Component
// ============================================================================

export function DemoBanner({
  scenarioId,
  scenarios = DEFAULT_DEMO_SCENARIOS,
  onReset,
  onClose,
  className,
}: DemoBannerProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  
  // Don't render if no demo is active
  if (!scenarioId) return null;
  
  const activeScenario = scenarios.find((s) => s.id === scenarioId);

  return (
    <div
      className={cn(
        "demo-banner relative",
        className
      )}
      role="banner"
      aria-label="Demo mode indicator"
    >
      <div className="container mx-auto flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Info className="h-4 w-4" />
          <span className="font-semibold">Demo Mode</span>
          {activeScenario && (
            <>
              <span className="text-marine-200">|</span>
              <span className="text-white/90">{activeScenario.name}</span>
            </>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-white/80 hover:text-white underline"
          >
            {isExpanded ? "Hide details" : "Show details"}
          </button>
        </div>
        <div className="flex items-center gap-2">
          {onReset && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              className="h-7 px-2 text-white hover:text-white hover:bg-white/20"
            >
              <RotateCcw className="h-3.5 w-3.5 mr-1" />
              Reset
            </Button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white"
              aria-label="Exit demo mode"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
      
      {/* Expanded details */}
      {isExpanded && activeScenario && (
        <div className="bg-marine-700 py-2 px-4">
          <div className="container mx-auto">
            <p className="text-sm text-white/90">
              {activeScenario.description}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Demo Mode Context
// ============================================================================

interface DemoModeContextValue {
  isDemo: boolean;
  scenarioId: string | null;
  setScenarioId: (id: string | null) => void;
  exitDemo: () => void;
}

const DemoModeContext = React.createContext<DemoModeContextValue | null>(null);

export function useDemoMode() {
  const context = React.useContext(DemoModeContext);
  if (!context) {
    throw new Error("useDemoMode must be used within a DemoModeProvider");
  }
  return context;
}

interface DemoModeProviderProps {
  children: React.ReactNode;
  initialScenarioId?: string | null;
}

export function DemoModeProvider({
  children,
  initialScenarioId = null,
}: DemoModeProviderProps) {
  const [scenarioId, setScenarioId] = React.useState<string | null>(
    initialScenarioId
  );

  const exitDemo = React.useCallback(() => {
    setScenarioId(null);
  }, []);

  const value = React.useMemo(
    () => ({
      isDemo: scenarioId !== null,
      scenarioId,
      setScenarioId,
      exitDemo,
    }),
    [scenarioId, exitDemo]
  );

  return (
    <DemoModeContext.Provider value={value}>
      {children}
    </DemoModeContext.Provider>
  );
}

// ============================================================================
// Demo Scenario Selector
// ============================================================================

interface DemoScenarioSelectorProps {
  scenarios?: DemoScenario[];
  onSelect: (scenarioId: string) => void;
  className?: string;
}

export function DemoScenarioSelector({
  scenarios = DEFAULT_DEMO_SCENARIOS,
  onSelect,
  className,
}: DemoScenarioSelectorProps) {
  return (
    <div className={cn("grid gap-3 sm:grid-cols-2 lg:grid-cols-3", className)}>
      {scenarios.map((scenario) => (
        <button
          key={scenario.id}
          onClick={() => onSelect(scenario.id)}
          className="p-4 text-left border border-marine-200 rounded-lg hover:border-marine-400 hover:bg-marine-50 transition-colors"
        >
          <h3 className="font-medium text-marine-800">{scenario.name}</h3>
          <p className="text-sm text-marine-600 mt-1">{scenario.description}</p>
        </button>
      ))}
    </div>
  );
}
