"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn, formatCurrency } from "@/lib/utils";
import { FileText, TrendingUp } from "lucide-react";

export interface SimilarJobsRefProps {
  count: number;
  summary: string;
  className?: string;
}

/**
 * Displays "Based on X similar jobs" reference for transparency
 */
export function SimilarJobsRef({ count, summary, className }: SimilarJobsRefProps) {
  const getCountBadge = () => {
    if (count >= 10) {
      return <Badge variant="success">{count} jobs</Badge>;
    } else if (count >= 5) {
      return <Badge variant="info">{count} jobs</Badge>;
    } else if (count > 0) {
      return <Badge variant="warning">{count} jobs</Badge>;
    } else {
      return <Badge variant="secondary">No similar jobs</Badge>;
    }
  };

  return (
    <div className={cn("flex items-center gap-2 text-sm", className)}>
      <FileText className="h-4 w-4 text-marine-500" />
      <span className="text-marine-600">{summary}</span>
      {getCountBadge()}
    </div>
  );
}

export interface SimilarJobsCardProps {
  count: number;
  summary: string;
  averageTotal?: number;
  className?: string;
}

/**
 * Card version with more detail about similar jobs
 */
export function SimilarJobsCard({
  count,
  summary,
  averageTotal,
  className,
}: SimilarJobsCardProps) {
  const confidenceLevel = count >= 10 ? "high" : count >= 5 ? "medium" : "low";

  return (
    <Card className={cn("bg-marine-50", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-marine-600" />
            AI Analysis
          </CardTitle>
          <Badge
            variant={
              confidenceLevel === "high"
                ? "success"
                : confidenceLevel === "medium"
                ? "warning"
                : "secondary"
            }
          >
            {count} similar jobs found
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-marine-700">{summary}</p>
        {averageTotal && (
          <p className="mt-2 text-sm text-marine-600">
            Average invoice from similar jobs:{" "}
            <span className="font-semibold">{formatCurrency(averageTotal)}</span>
          </p>
        )}
        {count < 5 && (
          <p className="mt-2 text-xs text-marine-500 italic">
            Note: Limited historical data for this combination. Estimate based primarily on
            service templates with adjustments for vessel specifications.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default SimilarJobsRef;
