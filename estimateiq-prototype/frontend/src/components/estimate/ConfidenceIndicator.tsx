"use client";

import * as React from "react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn, formatPercent, getConfidenceLevel } from "@/lib/utils";

export interface ConfidenceIndicatorProps {
  score: number;
  showLabel?: boolean;
  showProgress?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

/**
 * Displays a confidence score with visual indicator
 * Can show as badge, progress bar, or both
 */
export function ConfidenceIndicator({
  score,
  showLabel = true,
  showProgress = true,
  size = "md",
  className,
}: ConfidenceIndicatorProps) {
  const { level, text, color } = getConfidenceLevel(score);
  
  const badgeVariant = {
    high: "success" as const,
    medium: "warning" as const,
    low: "destructive" as const,
  }[level];

  const progressColor = {
    high: "bg-green-500",
    medium: "bg-yellow-500",
    low: "bg-orange-500",
  }[level];

  const sizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  }[size];

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {showProgress && (
        <Progress
          value={score * 100}
          className={cn(
            "flex-1",
            size === "sm" && "h-1.5",
            size === "md" && "h-2",
            size === "lg" && "h-3"
          )}
          indicatorClassName={progressColor}
        />
      )}
      {showLabel && (
        <Badge variant={badgeVariant} className={sizeClasses}>
          {formatPercent(score)}
        </Badge>
      )}
    </div>
  );
}

export interface ConfidenceBadgeProps {
  score: number;
  className?: string;
}

/**
 * Simple confidence badge without progress bar
 */
export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  const { level, text } = getConfidenceLevel(score);
  
  const badgeVariant = {
    high: "success" as const,
    medium: "warning" as const,
    low: "destructive" as const,
  }[level];

  return (
    <Badge variant={badgeVariant} className={className}>
      {text}
    </Badge>
  );
}

export interface ConfidenceTextProps {
  score: number;
  showPercent?: boolean;
  className?: string;
}

/**
 * Text-only confidence indicator
 */
export function ConfidenceText({ score, showPercent = true, className }: ConfidenceTextProps) {
  const { level, text, color } = getConfidenceLevel(score);
  
  return (
    <span className={cn(color, className)}>
      {text}
      {showPercent && ` (${formatPercent(score)})`}
    </span>
  );
}

export default ConfidenceIndicator;
