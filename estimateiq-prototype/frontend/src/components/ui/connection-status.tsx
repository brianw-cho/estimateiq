"use client";

import * as React from "react";
import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { checkHealth } from "@/lib/api";

// ============================================================================
// Types
// ============================================================================

export type ConnectionState = "connected" | "disconnected" | "checking";

interface ConnectionStatusProps {
  /** How often to check connection (in ms). Default: 30000 (30 seconds) */
  checkInterval?: number;
  /** Whether to show the label text. Default: true */
  showLabel?: boolean;
  /** Custom class name */
  className?: string;
  /** Callback when connection state changes */
  onStateChange?: (state: ConnectionState) => void;
}

// ============================================================================
// Hook: useConnectionStatus
// ============================================================================

export function useConnectionStatus(
  checkInterval: number = 30000,
  onStateChange?: (state: ConnectionState) => void
) {
  const [state, setState] = React.useState<ConnectionState>("checking");
  const [lastChecked, setLastChecked] = React.useState<Date | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const checkConnection = React.useCallback(async () => {
    setState("checking");
    try {
      await checkHealth();
      setState("connected");
      setError(null);
      setLastChecked(new Date());
      onStateChange?.("connected");
    } catch (err) {
      setState("disconnected");
      setError(err instanceof Error ? err.message : "Connection failed");
      setLastChecked(new Date());
      onStateChange?.("disconnected");
    }
  }, [onStateChange]);

  // Initial check
  React.useEffect(() => {
    checkConnection();
  }, [checkConnection]);

  // Periodic checks
  React.useEffect(() => {
    if (checkInterval <= 0) return;
    
    const intervalId = setInterval(checkConnection, checkInterval);
    return () => clearInterval(intervalId);
  }, [checkConnection, checkInterval]);

  return {
    state,
    lastChecked,
    error,
    refresh: checkConnection,
  };
}

// ============================================================================
// Connection Status Component
// ============================================================================

export function ConnectionStatus({
  checkInterval = 30000,
  showLabel = true,
  className,
  onStateChange,
}: ConnectionStatusProps) {
  const { state, error, refresh } = useConnectionStatus(checkInterval, onStateChange);

  const stateConfig = {
    connected: {
      icon: Wifi,
      label: "Connected",
      dotClass: "connected",
      textClass: "text-green-600",
    },
    disconnected: {
      icon: WifiOff,
      label: "Disconnected",
      dotClass: "disconnected",
      textClass: "text-red-600",
    },
    checking: {
      icon: Loader2,
      label: "Checking...",
      dotClass: "checking",
      textClass: "text-yellow-600",
    },
  };

  const config = stateConfig[state];
  const Icon = config.icon;

  return (
    <div
      className={cn("connection-status", className)}
      title={error || `API Status: ${config.label}`}
    >
      <span className={cn("connection-dot", config.dotClass)} />
      {state === "checking" ? (
        <Icon className={cn("h-4 w-4 animate-spin", config.textClass)} />
      ) : (
        <Icon className={cn("h-4 w-4", config.textClass)} />
      )}
      {showLabel && (
        <span className={cn("text-sm", config.textClass)}>{config.label}</span>
      )}
      {state === "disconnected" && (
        <button
          onClick={refresh}
          className="text-xs text-marine-600 hover:text-marine-800 underline ml-2"
        >
          Retry
        </button>
      )}
    </div>
  );
}

// ============================================================================
// Compact Connection Indicator (for header)
// ============================================================================

export function ConnectionIndicator({ className }: { className?: string }) {
  const { state } = useConnectionStatus(30000);

  const dotClass = {
    connected: "bg-green-500",
    disconnected: "bg-red-500",
    checking: "bg-yellow-500 animate-pulse",
  }[state];

  return (
    <div
      className={cn("flex items-center gap-1.5", className)}
      title={`API: ${state}`}
      role="status"
      aria-label={`API connection status: ${state}`}
    >
      <span className={cn("w-2 h-2 rounded-full", dotClass)} />
      <span className="text-xs text-gray-500 capitalize">{state}</span>
    </div>
  );
}
