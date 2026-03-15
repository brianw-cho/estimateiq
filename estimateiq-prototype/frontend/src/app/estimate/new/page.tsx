"use client";

import * as React from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  VesselForm,
  validateVessel,
  ServiceRequestForm,
  validateServiceRequest,
  EstimateDisplay,
} from "@/components/estimate";
import type { ServiceRequestData } from "@/components/estimate";
import type { Vessel, Estimate, ServiceRequest } from "@/lib/types";
import { generateEstimate } from "@/lib/api";
import { ArrowLeft, ArrowRight, Loader2, AlertCircle } from "lucide-react";

// Demo scenario presets
const DEMO_SCENARIOS: Record<string, { vessel: Partial<Vessel>; service: Partial<ServiceRequestData> }> = {
  "oil-change": {
    vessel: {
      loa: 28,
      year: 2019,
      engine_make: "Volvo Penta",
      engine_model: "D4-300",
      hull_type: "fiberglass",
      propulsion_type: "sterndrive",
    },
    service: {
      description: "Annual oil change and filter replacement",
      urgency: "routine",
      region: "Northeast",
    },
  },
  "bottom-paint": {
    vessel: {
      loa: 32,
      year: 2015,
      engine_make: "Yamaha",
      engine_model: "F250",
      hull_type: "fiberglass",
      propulsion_type: "outboard",
    },
    service: {
      description: "Hull cleaning and bottom paint",
      urgency: "routine",
      region: "Southeast",
    },
  },
  winterization: {
    vessel: {
      loa: 22,
      year: 2018,
      engine_make: "MerCruiser",
      engine_model: "4.3L MPI",
      hull_type: "fiberglass",
      propulsion_type: "sterndrive",
    },
    service: {
      description: "Full winterization package including engine and water systems",
      urgency: "routine",
      region: "Northeast",
    },
  },
  diagnostic: {
    vessel: {
      loa: 24,
      year: 2020,
      engine_make: "Yamaha",
      engine_model: "F250",
      hull_type: "fiberglass",
      propulsion_type: "outboard",
    },
    service: {
      description: "Troubleshoot no-start condition, engine cranks but won't fire",
      urgency: "priority",
      region: "Gulf Coast",
    },
  },
  unusual: {
    vessel: {
      loa: 45,
      year: 2010,
      engine_make: "Mercury",
      engine_model: "C9",
      hull_type: "fiberglass",
      propulsion_type: "inboard",
    },
    service: {
      description: "Engine service and inspection",
      urgency: "routine",
      region: "West Coast",
    },
  },
};

type Step = "vessel" | "service" | "generating" | "result";

function NewEstimateContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const demoScenario = searchParams.get("demo");

  // Initialize state with demo data if present
  const getInitialVessel = React.useCallback(() => {
    if (demoScenario && DEMO_SCENARIOS[demoScenario]) {
      return DEMO_SCENARIOS[demoScenario].vessel;
    }
    return {};
  }, [demoScenario]);

  const getInitialService = React.useCallback((): ServiceRequestData => {
    if (demoScenario && DEMO_SCENARIOS[demoScenario]) {
      return {
        ...DEMO_SCENARIOS[demoScenario].service,
        urgency: DEMO_SCENARIOS[demoScenario].service.urgency || "routine",
        region: DEMO_SCENARIOS[demoScenario].service.region || "Northeast",
        description: DEMO_SCENARIOS[demoScenario].service.description || "",
      } as ServiceRequestData;
    }
    return { description: "", urgency: "routine", region: "Northeast" };
  }, [demoScenario]);

  const [step, setStep] = React.useState<Step>("vessel");
  const [vessel, setVessel] = React.useState<Partial<Vessel>>(getInitialVessel);
  const [serviceRequest, setServiceRequest] = React.useState<ServiceRequestData>(getInitialService);
  const [vesselErrors, setVesselErrors] = React.useState<Record<string, string>>({});
  const [serviceErrors, setServiceErrors] = React.useState<Record<string, string>>({});
  const [estimate, setEstimate] = React.useState<Estimate | null>(null);
  const [apiError, setApiError] = React.useState<string | null>(null);

  // Update state when demo scenario changes
  React.useEffect(() => {
    setVessel(getInitialVessel());
    setServiceRequest(getInitialService());
  }, [demoScenario, getInitialVessel, getInitialService]);

  const handleVesselNext = () => {
    const errors = validateVessel(vessel);
    setVesselErrors(errors);
    if (Object.keys(errors).length === 0) {
      setStep("service");
    }
  };

  const handleServiceNext = async () => {
    const errors = validateServiceRequest(serviceRequest);
    setServiceErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setStep("generating");
    setApiError(null);

    try {
      const request: ServiceRequest = {
        vessel: vessel as Vessel,
        description: serviceRequest.description,
        service_category: serviceRequest.service_category || undefined,
        urgency: serviceRequest.urgency,
        region: serviceRequest.region,
      };

      const result = await generateEstimate(request);
      setEstimate(result);
      setStep("result");
    } catch (error) {
      console.error("Failed to generate estimate:", error);
      setApiError(
        error instanceof Error ? error.message : "Failed to generate estimate. Please try again."
      );
      setStep("service");
    }
  };

  const handleBack = () => {
    if (step === "service") {
      setStep("vessel");
    } else if (step === "result") {
      setStep("service");
      setEstimate(null);
    }
  };

  const handleUpdateEstimate = (updated: Estimate) => {
    setEstimate(updated);
  };

  const handleNewEstimate = () => {
    setVessel({});
    setServiceRequest({ description: "", urgency: "routine", region: "Northeast" });
    setEstimate(null);
    setStep("vessel");
    router.push("/estimate/new");
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      <div className="flex items-center space-x-4">
        <div
          className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
            step === "vessel" || step === "service" || step === "result"
              ? "bg-marine-600 text-white"
              : "bg-marine-100 text-marine-500"
          }`}
        >
          1
        </div>
        <div className={`w-16 h-1 ${step !== "vessel" ? "bg-marine-600" : "bg-marine-200"}`} />
        <div
          className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
            step === "service" || step === "result"
              ? "bg-marine-600 text-white"
              : "bg-marine-100 text-marine-500"
          }`}
        >
          2
        </div>
        <div className={`w-16 h-1 ${step === "result" ? "bg-marine-600" : "bg-marine-200"}`} />
        <div
          className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
            step === "result"
              ? "bg-marine-600 text-white"
              : "bg-marine-100 text-marine-500"
          }`}
        >
          3
        </div>
      </div>
    </div>
  );

  return (
    <>
      <h1 className="text-3xl font-bold text-marine-800 mb-2 text-center">
        Create New Estimate
      </h1>
      <p className="text-marine-600 text-center mb-8">
        {step === "vessel" && "Enter vessel information"}
        {step === "service" && "Describe the service needed"}
        {step === "generating" && "Generating your estimate..."}
        {step === "result" && "Review your AI-generated estimate"}
      </p>

      {renderStepIndicator()}

      {/* Vessel Step */}
      {step === "vessel" && (
        <div className="space-y-6">
          <VesselForm vessel={vessel} onChange={setVessel} errors={vesselErrors} />
          <div className="flex justify-end">
            <Button onClick={handleVesselNext}>
              Continue to Service
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Service Step */}
      {step === "service" && (
        <div className="space-y-6">
          <ServiceRequestForm
            data={serviceRequest}
            onChange={setServiceRequest}
            errors={serviceErrors}
          />
          {apiError && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                  <div>
                    <p className="font-medium text-red-800">Error generating estimate</p>
                    <p className="text-sm text-red-600">{apiError}</p>
                    <p className="text-sm text-red-600 mt-2">
                      Make sure the backend server is running on http://localhost:8000
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          <div className="flex justify-between">
            <Button variant="outline" onClick={handleBack}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Vessel
            </Button>
            <Button onClick={handleServiceNext}>
              Generate Estimate
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Generating Step */}
      {step === "generating" && (
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-12 w-12 text-marine-600 animate-spin" />
              <h2 className="text-xl font-semibold text-marine-800">
                Generating Your Estimate
              </h2>
              <p className="text-marine-600 text-center max-w-md">
                Our AI is analyzing similar jobs and calculating labor hours and parts
                recommendations for your vessel...
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Result Step */}
      {step === "result" && estimate && (
        <div className="space-y-6">
          <EstimateDisplay
            estimate={estimate}
            onUpdateEstimate={handleUpdateEstimate}
            onApprove={() => {
              setEstimate({ ...estimate, status: "approved" });
            }}
            onSend={() => {
              setEstimate({ ...estimate, status: "sent" });
              alert("In production, this would send the estimate to the customer.");
            }}
          />
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={handleBack}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Modify Request
            </Button>
            <Button variant="secondary" onClick={handleNewEstimate}>
              Create New Estimate
            </Button>
          </div>
        </div>
      )}
    </>
  );
}

function LoadingFallback() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Loader2 className="h-8 w-8 text-marine-600 animate-spin" />
      <p className="mt-4 text-marine-600">Loading...</p>
    </div>
  );
}

export default function NewEstimatePage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Suspense fallback={<LoadingFallback />}>
        <NewEstimateContent />
      </Suspense>
    </div>
  );
}
