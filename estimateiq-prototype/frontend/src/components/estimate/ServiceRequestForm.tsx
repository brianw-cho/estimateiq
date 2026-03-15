"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ServiceCategory, Urgency } from "@/lib/types";
import { SERVICE_CATEGORIES, URGENCY_LEVELS, REGIONS } from "@/lib/types";

export interface ServiceRequestData {
  description: string;
  service_category?: ServiceCategory;
  urgency: Urgency;
  region: string;
}

export interface ServiceRequestFormProps {
  data: ServiceRequestData;
  onChange: (data: ServiceRequestData) => void;
  errors?: Record<string, string>;
}

const SERVICE_CATEGORY_LABELS: Record<ServiceCategory, string> = {
  engine: "Engine Service",
  hull: "Hull & Bottom",
  electrical: "Electrical",
  mechanical: "Mechanical",
  outboard: "Outboard Service",
  inboard: "Inboard Service",
  annual: "Annual Service",
  diagnostic: "Diagnostic",
};

const URGENCY_LABELS: Record<Urgency, string> = {
  routine: "Routine - Standard scheduling",
  priority: "Priority - Within 1-2 days",
  emergency: "Emergency - Same day",
};

export function ServiceRequestForm({ data, onChange, errors = {} }: ServiceRequestFormProps) {
  const handleChange = (field: keyof ServiceRequestData, value: string) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Service Request</CardTitle>
        <CardDescription>
          Describe the service needed - our AI will analyze and recommend labor and parts
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Service Description */}
        <div className="space-y-2">
          <Label htmlFor="service-description">
            Service Description <span className="text-red-500">*</span>
          </Label>
          <Textarea
            id="service-description"
            placeholder="Describe the service needed, e.g., 'Annual oil change and filter replacement' or 'Engine won't start, need diagnosis'"
            value={data.description}
            onChange={(e) => handleChange("description", e.target.value)}
            rows={4}
            className={errors.description ? "border-red-500" : ""}
          />
          {errors.description && (
            <p className="text-sm text-red-500">{errors.description}</p>
          )}
          <p className="text-sm text-marine-500">
            Be specific about symptoms, requested services, or issues to get the most accurate estimate.
          </p>
        </div>

        {/* Service Category and Urgency */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="service-category">Service Category (Optional)</Label>
            <Select
              value={data.service_category || "__auto__"}
              onValueChange={(value) => handleChange("service_category", value === "__auto__" ? "" : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Auto-detect from description" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__auto__">Auto-detect from description</SelectItem>
                {SERVICE_CATEGORIES.map((category) => (
                  <SelectItem key={category} value={category}>
                    {SERVICE_CATEGORY_LABELS[category]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-sm text-marine-500">
              Leave empty to let AI categorize the service
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="urgency">Urgency Level</Label>
            <Select
              value={data.urgency}
              onValueChange={(value) => handleChange("urgency", value as Urgency)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select urgency" />
              </SelectTrigger>
              <SelectContent>
                {URGENCY_LEVELS.map((level) => (
                  <SelectItem key={level} value={level}>
                    {URGENCY_LABELS[level]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Region */}
        <div className="space-y-2">
          <Label htmlFor="region">Region</Label>
          <Select
            value={data.region}
            onValueChange={(value) => handleChange("region", value)}
          >
            <SelectTrigger className="w-full md:w-1/2">
              <SelectValue placeholder="Select region" />
            </SelectTrigger>
            <SelectContent>
              {REGIONS.map((region) => (
                <SelectItem key={region} value={region}>
                  {region}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-marine-500">
            Regional pricing may affect labor rates and parts availability
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Validate service request form data
 */
export function validateServiceRequest(data: ServiceRequestData): Record<string, string> {
  const errors: Record<string, string> = {};

  if (!data.description || data.description.trim().length < 5) {
    errors.description = "Please provide a service description (at least 5 characters)";
  }

  return errors;
}

export default ServiceRequestForm;
