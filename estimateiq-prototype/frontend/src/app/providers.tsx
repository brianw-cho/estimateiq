"use client";

import { ToastProvider } from "@/components/ui/toast";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ToastProvider maxToasts={5}>
      {children}
    </ToastProvider>
  );
}
