"use client";

import * as React from "react";
import { cn, formatCurrency } from "@/lib/utils";
import type { EstimateRange as EstimateRangeType } from "@/lib/types";

export interface EstimateRangeProps {
  range: EstimateRangeType;
  className?: string;
}

/**
 * Displays low/expected/high estimate range with visual indicator
 */
export function EstimateRange({ range, className }: EstimateRangeProps) {
  const { low, expected, high } = range;
  const total = high - low;
  const expectedPosition = total > 0 ? ((expected - low) / total) * 100 : 50;

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex justify-between text-sm">
        <span className="text-marine-500">Low</span>
        <span className="font-semibold text-marine-700">Expected</span>
        <span className="text-marine-500">High</span>
      </div>
      
      {/* Visual range bar */}
      <div className="relative">
        <div className="h-3 rounded-full bg-gradient-to-r from-marine-200 via-marine-400 to-marine-200" />
        <div
          className="absolute top-1/2 h-5 w-1 -translate-y-1/2 rounded-sm bg-marine-800"
          style={{ left: `${expectedPosition}%` }}
        />
      </div>
      
      {/* Values */}
      <div className="flex justify-between text-sm">
        <span className="text-marine-600">{formatCurrency(low)}</span>
        <span className="text-lg font-bold text-marine-800">
          {formatCurrency(expected)}
        </span>
        <span className="text-marine-600">{formatCurrency(high)}</span>
      </div>
    </div>
  );
}

export interface EstimateRangeCompactProps {
  range: EstimateRangeType;
  className?: string;
}

/**
 * Compact single-line version of estimate range
 */
export function EstimateRangeCompact({ range, className }: EstimateRangeCompactProps) {
  const { low, expected, high } = range;

  return (
    <div className={cn("flex items-baseline gap-2", className)}>
      <span className="text-2xl font-bold text-marine-800">
        {formatCurrency(expected)}
      </span>
      <span className="text-sm text-marine-500">
        ({formatCurrency(low)} - {formatCurrency(high)})
      </span>
    </div>
  );
}

export interface EstimateRangeTableProps {
  range: EstimateRangeType;
  className?: string;
}

/**
 * Table format estimate range display
 */
export function EstimateRangeTable({ range, className }: EstimateRangeTableProps) {
  const { low, expected, high } = range;

  return (
    <div className={cn("grid grid-cols-3 gap-4 text-center", className)}>
      <div className="space-y-1 rounded-lg bg-marine-50 p-3">
        <p className="text-xs font-medium uppercase tracking-wide text-marine-500">
          Low Estimate
        </p>
        <p className="text-lg font-semibold text-marine-600">
          {formatCurrency(low)}
        </p>
      </div>
      <div className="space-y-1 rounded-lg bg-marine-100 p-3 ring-2 ring-marine-500">
        <p className="text-xs font-medium uppercase tracking-wide text-marine-600">
          Expected
        </p>
        <p className="text-xl font-bold text-marine-800">
          {formatCurrency(expected)}
        </p>
      </div>
      <div className="space-y-1 rounded-lg bg-marine-50 p-3">
        <p className="text-xs font-medium uppercase tracking-wide text-marine-500">
          High Estimate
        </p>
        <p className="text-lg font-semibold text-marine-600">
          {formatCurrency(high)}
        </p>
      </div>
    </div>
  );
}

export default EstimateRange;
