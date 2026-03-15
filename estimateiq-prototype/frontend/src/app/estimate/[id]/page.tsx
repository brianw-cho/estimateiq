"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EstimateDisplay } from "@/components/estimate";
import { getEstimate } from "@/lib/api";
import type { Estimate } from "@/lib/types";
import { ArrowLeft, Loader2, AlertCircle } from "lucide-react";

export default function ViewEstimatePage() {
  const params = useParams();
  const router = useRouter();
  const estimateId = params.id as string;

  const [estimate, setEstimate] = React.useState<Estimate | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchEstimate = async () => {
      try {
        setLoading(true);
        const data = await getEstimate(estimateId);
        setEstimate(data);
      } catch (err) {
        console.error("Failed to fetch estimate:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load estimate"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchEstimate();
  }, [estimateId]);

  const handleUpdateEstimate = (updated: Estimate) => {
    setEstimate(updated);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-12 w-12 text-marine-600 animate-spin" />
              <h2 className="text-xl font-semibold text-marine-800">
                Loading Estimate
              </h2>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-8">
            <div className="flex flex-col items-center justify-center space-y-4">
              <AlertCircle className="h-12 w-12 text-red-500" />
              <h2 className="text-xl font-semibold text-red-800">
                Error Loading Estimate
              </h2>
              <p className="text-red-600 text-center">{error}</p>
              <p className="text-sm text-red-500">
                Note: Individual estimate retrieval is not yet implemented in the backend.
                Please create a new estimate instead.
              </p>
              <div className="flex gap-4 mt-4">
                <Button variant="outline" onClick={() => router.back()}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Go Back
                </Button>
                <Link href="/estimate/new">
                  <Button>Create New Estimate</Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!estimate) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card>
          <CardContent className="py-8">
            <div className="flex flex-col items-center justify-center space-y-4">
              <AlertCircle className="h-12 w-12 text-marine-400" />
              <h2 className="text-xl font-semibold text-marine-800">
                Estimate Not Found
              </h2>
              <p className="text-marine-600">
                The estimate you&apos;re looking for doesn&apos;t exist or has been deleted.
              </p>
              <Link href="/estimate/new">
                <Button>Create New Estimate</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </div>

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
    </div>
  );
}
