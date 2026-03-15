"use client";

import { ConnectionIndicator } from "@/components/ui/connection-status";

export function HeaderConnectionStatus() {
  return <ConnectionIndicator className="hidden sm:flex" />;
}
