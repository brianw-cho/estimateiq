"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ConfidenceIndicator, ConfidenceBadge } from "./ConfidenceIndicator";
import { EstimateRangeTable } from "./EstimateRange";
import { LineItemTable } from "./LineItemEditor";
import { SimilarJobsCard } from "./SimilarJobsRef";
import { cn, formatCurrency, formatDate } from "@/lib/utils";
import type { Estimate, EstimateLineItem } from "@/lib/types";
import { Printer, Download, Send, Edit, CheckCircle } from "lucide-react";

export interface EstimateDisplayProps {
  estimate: Estimate;
  onUpdateEstimate?: (estimate: Estimate) => void;
  onApprove?: () => void;
  onSend?: () => void;
  isEditable?: boolean;
  className?: string;
}

/**
 * Full estimate display component with all details and editing capability
 */
export function EstimateDisplay({
  estimate,
  onUpdateEstimate,
  onApprove,
  onSend,
  isEditable = true,
  className,
}: EstimateDisplayProps) {
  const handleUpdateLaborItem = (index: number, item: EstimateLineItem) => {
    if (!onUpdateEstimate) return;
    const updatedLabor = [...estimate.labor_items];
    updatedLabor[index] = item;
    const laborSubtotal = updatedLabor.reduce((sum, i) => sum + i.total_price, 0);
    const totalEstimate = laborSubtotal + estimate.parts_subtotal;
    onUpdateEstimate({
      ...estimate,
      labor_items: updatedLabor,
      labor_subtotal: laborSubtotal,
      total_estimate: totalEstimate,
      estimate_range: {
        low: totalEstimate * 0.85,
        expected: totalEstimate,
        high: totalEstimate * 1.2,
      },
    });
  };

  const handleDeleteLaborItem = (index: number) => {
    if (!onUpdateEstimate) return;
    const updatedLabor = estimate.labor_items.filter((_, i) => i !== index);
    const laborSubtotal = updatedLabor.reduce((sum, i) => sum + i.total_price, 0);
    const totalEstimate = laborSubtotal + estimate.parts_subtotal;
    onUpdateEstimate({
      ...estimate,
      labor_items: updatedLabor,
      labor_subtotal: laborSubtotal,
      total_estimate: totalEstimate,
      estimate_range: {
        low: totalEstimate * 0.85,
        expected: totalEstimate,
        high: totalEstimate * 1.2,
      },
    });
  };

  const handleUpdatePartsItem = (index: number, item: EstimateLineItem) => {
    if (!onUpdateEstimate) return;
    const updatedParts = [...estimate.parts_items];
    updatedParts[index] = item;
    const partsSubtotal = updatedParts.reduce((sum, i) => sum + i.total_price, 0);
    const totalEstimate = estimate.labor_subtotal + partsSubtotal;
    onUpdateEstimate({
      ...estimate,
      parts_items: updatedParts,
      parts_subtotal: partsSubtotal,
      total_estimate: totalEstimate,
      estimate_range: {
        low: totalEstimate * 0.85,
        expected: totalEstimate,
        high: totalEstimate * 1.2,
      },
    });
  };

  const handleDeletePartsItem = (index: number) => {
    if (!onUpdateEstimate) return;
    const updatedParts = estimate.parts_items.filter((_, i) => i !== index);
    const partsSubtotal = updatedParts.reduce((sum, i) => sum + i.total_price, 0);
    const totalEstimate = estimate.labor_subtotal + partsSubtotal;
    onUpdateEstimate({
      ...estimate,
      parts_items: updatedParts,
      parts_subtotal: partsSubtotal,
      total_estimate: totalEstimate,
      estimate_range: {
        low: totalEstimate * 0.85,
        expected: totalEstimate,
        high: totalEstimate * 1.2,
      },
    });
  };

  const statusBadge = {
    draft: <Badge variant="secondary">Draft</Badge>,
    reviewed: <Badge variant="info">Reviewed</Badge>,
    approved: <Badge variant="success">Approved</Badge>,
    sent: <Badge variant="default">Sent</Badge>,
  }[estimate.status];

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-3">
                Estimate #{estimate.estimate_id.slice(-8).toUpperCase()}
                {statusBadge}
              </CardTitle>
              <CardDescription className="mt-1">
                Generated {formatDate(estimate.generated_at)}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Printer className="h-4 w-4 mr-2" />
                Print
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              {estimate.status === "draft" && onApprove && (
                <Button variant="secondary" size="sm" onClick={onApprove}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </Button>
              )}
              {(estimate.status === "approved" || estimate.status === "reviewed") && onSend && (
                <Button size="sm" onClick={onSend}>
                  <Send className="h-4 w-4 mr-2" />
                  Send to Customer
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Vessel and Service Info */}
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-900">Vessel</h3>
              <div className="text-sm text-gray-700 space-y-1">
                {estimate.vessel.name && <p className="font-medium">{estimate.vessel.name}</p>}
                <p>{estimate.vessel.loa}&apos; {estimate.vessel.hull_type || "fiberglass"}</p>
                <p>
                  {estimate.vessel.engine_make} {estimate.vessel.engine_model} ({estimate.vessel.year})
                </p>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-900">Service Request</h3>
              <p className="text-sm text-gray-700">{estimate.service_description}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Analysis */}
      <SimilarJobsCard
        count={estimate.similar_jobs_count}
        summary={estimate.similar_jobs_summary}
      />

      {/* Overall Confidence */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Estimate Confidence</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <ConfidenceIndicator
              score={estimate.confidence_score}
              size="lg"
              className="flex-1 max-w-md"
            />
            <ConfidenceBadge score={estimate.confidence_score} />
          </div>
        </CardContent>
      </Card>

      {/* Estimate Range */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Estimate Range</CardTitle>
        </CardHeader>
        <CardContent>
          <EstimateRangeTable range={estimate.estimate_range} />
        </CardContent>
      </Card>

      {/* Labor Items */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-gray-900">Labor</h2>
        <LineItemTable
          items={estimate.labor_items}
          title="Labor Tasks"
          onUpdateItem={handleUpdateLaborItem}
          onDeleteItem={handleDeleteLaborItem}
        />
      </div>

      {/* Parts Items */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-gray-900">Parts</h2>
        <LineItemTable
          items={estimate.parts_items}
          title="Parts & Materials"
          onUpdateItem={handleUpdatePartsItem}
          onDeleteItem={handleDeletePartsItem}
        />
      </div>

      {/* Totals */}
      <Card className="bg-marine-50">
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-gray-700">
              <span>Labor Subtotal:</span>
              <span className="font-medium">{formatCurrency(estimate.labor_subtotal)}</span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Parts Subtotal:</span>
              <span className="font-medium">{formatCurrency(estimate.parts_subtotal)}</span>
            </div>
            <div className="border-t border-marine-200 pt-2 mt-2">
              <div className="flex justify-between text-xl font-bold text-gray-900">
                <span>Total Estimate:</span>
                <span>{formatCurrency(estimate.total_estimate)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default EstimateDisplay;
