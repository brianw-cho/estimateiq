"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Vessel, HullType, PropulsionType } from "@/lib/types";
import { ENGINE_MAKES, HULL_TYPES, PROPULSION_TYPES } from "@/lib/types";

export interface VesselFormProps {
  vessel: Partial<Vessel>;
  onChange: (vessel: Partial<Vessel>) => void;
  errors?: Record<string, string>;
}

export function VesselForm({ vessel, onChange, errors = {} }: VesselFormProps) {
  const handleChange = (field: keyof Vessel, value: string | number) => {
    onChange({ ...vessel, [field]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Vessel Information</CardTitle>
        <CardDescription>
          Enter the vessel specifications for the estimate
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Row 1: Name (optional) and LOA */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="vessel-name">Vessel Name (Optional)</Label>
            <Input
              id="vessel-name"
              placeholder="e.g., Sea Breeze"
              value={vessel.name || ""}
              onChange={(e) => handleChange("name", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="vessel-loa">
              Length Overall (feet) <span className="text-red-500">*</span>
            </Label>
            <Input
              id="vessel-loa"
              type="number"
              min={10}
              max={200}
              placeholder="e.g., 28"
              value={vessel.loa || ""}
              onChange={(e) => handleChange("loa", parseFloat(e.target.value) || 0)}
              className={errors.loa ? "border-red-500" : ""}
            />
            {errors.loa && (
              <p className="text-sm text-red-500">{errors.loa}</p>
            )}
          </div>
        </div>

        {/* Row 2: Year and Beam */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="vessel-year">
              Year Built <span className="text-red-500">*</span>
            </Label>
            <Input
              id="vessel-year"
              type="number"
              min={1950}
              max={new Date().getFullYear()}
              placeholder="e.g., 2019"
              value={vessel.year || ""}
              onChange={(e) => handleChange("year", parseInt(e.target.value) || 0)}
              className={errors.year ? "border-red-500" : ""}
            />
            {errors.year && (
              <p className="text-sm text-red-500">{errors.year}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="vessel-beam">Beam (feet)</Label>
            <Input
              id="vessel-beam"
              type="number"
              min={4}
              max={50}
              placeholder="e.g., 10"
              value={vessel.beam || ""}
              onChange={(e) => handleChange("beam", parseFloat(e.target.value) || 0)}
            />
          </div>
        </div>

        {/* Row 3: Engine Make and Model */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="engine-make">
              Engine Make <span className="text-red-500">*</span>
            </Label>
            <Select
              value={vessel.engine_make || ""}
              onValueChange={(value) => handleChange("engine_make", value)}
            >
              <SelectTrigger className={errors.engine_make ? "border-red-500" : ""}>
                <SelectValue placeholder="Select engine make" />
              </SelectTrigger>
              <SelectContent>
                {ENGINE_MAKES.map((make) => (
                  <SelectItem key={make} value={make}>
                    {make}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.engine_make && (
              <p className="text-sm text-red-500">{errors.engine_make}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="engine-model">
              Engine Model <span className="text-red-500">*</span>
            </Label>
            <Input
              id="engine-model"
              placeholder="e.g., D4-300, F250"
              value={vessel.engine_model || ""}
              onChange={(e) => handleChange("engine_model", e.target.value)}
              className={errors.engine_model ? "border-red-500" : ""}
            />
            {errors.engine_model && (
              <p className="text-sm text-red-500">{errors.engine_model}</p>
            )}
          </div>
        </div>

        {/* Row 4: Hull Type and Propulsion Type */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="hull-type">Hull Type</Label>
            <Select
              value={vessel.hull_type || "fiberglass"}
              onValueChange={(value) => handleChange("hull_type", value as HullType)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select hull type" />
              </SelectTrigger>
              <SelectContent>
                {HULL_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="propulsion-type">Propulsion Type</Label>
            <Select
              value={vessel.propulsion_type || ""}
              onValueChange={(value) => handleChange("propulsion_type", value as PropulsionType)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select propulsion type" />
              </SelectTrigger>
              <SelectContent>
                {PROPULSION_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Validate vessel form data
 */
export function validateVessel(vessel: Partial<Vessel>): Record<string, string> {
  const errors: Record<string, string> = {};

  if (!vessel.loa || vessel.loa < 10 || vessel.loa > 200) {
    errors.loa = "Length must be between 10 and 200 feet";
  }

  if (!vessel.year || vessel.year < 1950 || vessel.year > new Date().getFullYear()) {
    errors.year = "Year must be between 1950 and " + new Date().getFullYear();
  }

  if (!vessel.engine_make || vessel.engine_make.length === 0) {
    errors.engine_make = "Engine make is required";
  }

  if (!vessel.engine_model || vessel.engine_model.length === 0) {
    errors.engine_model = "Engine model is required";
  }

  return errors;
}

export default VesselForm;
