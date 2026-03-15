"use client";

import * as React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { cn, formatCurrency } from "@/lib/utils";
import type { EstimateLineItem } from "@/lib/types";
import { Trash2, Edit2, Check, X } from "lucide-react";

export interface LineItemEditorProps {
  item: EstimateLineItem;
  onUpdate: (item: EstimateLineItem) => void;
  onDelete: () => void;
  isEditing?: boolean;
  onEditToggle?: () => void;
}

/**
 * Editable line item component for labor or parts
 */
export function LineItemEditor({
  item,
  onUpdate,
  onDelete,
  isEditing = false,
  onEditToggle,
}: LineItemEditorProps) {
  const [editedItem, setEditedItem] = React.useState(item);

  React.useEffect(() => {
    setEditedItem(item);
  }, [item]);

  const handleSave = () => {
    // Recalculate total price
    const updatedItem = {
      ...editedItem,
      total_price: editedItem.quantity * editedItem.unit_price,
    };
    onUpdate(updatedItem);
    onEditToggle?.();
  };

  const handleCancel = () => {
    setEditedItem(item);
    onEditToggle?.();
  };

  const handleChange = (field: keyof EstimateLineItem, value: string | number) => {
    setEditedItem((prev) => ({ ...prev, [field]: value }));
  };

  if (isEditing) {
    return (
      <tr className="bg-marine-50">
        <td className="px-4 py-3">
          <Input
            value={editedItem.description}
            onChange={(e) => handleChange("description", e.target.value)}
            className="w-full"
          />
        </td>
        <td className="px-4 py-3">
          <Input
            type="number"
            step="0.25"
            min="0"
            value={editedItem.quantity}
            onChange={(e) => handleChange("quantity", parseFloat(e.target.value) || 0)}
            className="w-20"
          />
        </td>
        <td className="px-4 py-3 text-sm text-gray-700">{editedItem.unit}</td>
        <td className="px-4 py-3">
          <Input
            type="number"
            step="0.01"
            min="0"
            value={editedItem.unit_price}
            onChange={(e) => handleChange("unit_price", parseFloat(e.target.value) || 0)}
            className="w-24"
          />
        </td>
        <td className="px-4 py-3 text-right font-medium text-gray-900">
          {formatCurrency(editedItem.quantity * editedItem.unit_price)}
        </td>
        <td className="px-4 py-3">
          <ConfidenceIndicator score={editedItem.confidence} size="sm" showProgress={false} />
        </td>
        <td className="px-4 py-3">
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleSave}
              className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-100"
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCancel}
              className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-100"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </td>
      </tr>
    );
  }

  return (
    <tr className="bg-white hover:bg-marine-50 transition-colors">
      <td className="px-4 py-3">
        <div>
          <p className="font-medium text-gray-900">{item.description}</p>
          {item.part_number && (
            <p className="text-xs text-gray-600">Part #: {item.part_number}</p>
          )}
          {item.source_reference && (
            <p className="text-xs text-gray-500 italic">{item.source_reference}</p>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-gray-800">{item.quantity}</td>
      <td className="px-4 py-3 text-sm text-gray-700">{item.unit}</td>
      <td className="px-4 py-3 text-gray-800">{formatCurrency(item.unit_price)}</td>
      <td className="px-4 py-3 text-right font-medium text-gray-900">
        {formatCurrency(item.total_price)}
      </td>
      <td className="px-4 py-3">
        <ConfidenceIndicator score={item.confidence} size="sm" showProgress={false} />
      </td>
      <td className="px-4 py-3">
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={onEditToggle}
            className="h-8 w-8 text-marine-600 hover:text-marine-700 hover:bg-marine-100"
          >
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onDelete}
            className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-100"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </td>
    </tr>
  );
}

export interface LineItemTableProps {
  items: EstimateLineItem[];
  title: string;
  onUpdateItem: (index: number, item: EstimateLineItem) => void;
  onDeleteItem: (index: number) => void;
  className?: string;
}

/**
 * Table of editable line items
 */
export function LineItemTable({
  items,
  title,
  onUpdateItem,
  onDeleteItem,
  className,
}: LineItemTableProps) {
  const [editingIndex, setEditingIndex] = React.useState<number | null>(null);

  const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);

  if (items.length === 0) {
    return (
      <div className={cn("rounded-lg border border-marine-200 p-6 text-center", className)}>
        <p className="text-marine-500">No {title.toLowerCase()} items</p>
      </div>
    );
  }

  return (
    <div className={cn("overflow-hidden rounded-lg border border-marine-200", className)}>
      <table className="w-full">
        <thead>
          <tr className="bg-marine-50 border-b border-marine-200">
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              {title}
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              Qty
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              Unit
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              Price
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-800">
              Total
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              Confidence
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-800">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => (
            <LineItemEditor
              key={`${item.description}-${index}`}
              item={item}
              onUpdate={(updated) => onUpdateItem(index, updated)}
              onDelete={() => onDeleteItem(index)}
              isEditing={editingIndex === index}
              onEditToggle={() =>
                setEditingIndex(editingIndex === index ? null : index)
              }
            />
          ))}
        </tbody>
        <tfoot>
          <tr className="bg-marine-100 border-t-2 border-marine-200">
            <td colSpan={4} className="px-4 py-3 text-right font-semibold text-gray-700">
              Subtotal:
            </td>
            <td className="px-4 py-3 text-right font-bold text-gray-900">
              {formatCurrency(subtotal)}
            </td>
            <td colSpan={2}></td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

export default LineItemEditor;
