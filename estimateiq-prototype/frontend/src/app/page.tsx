import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-marine-700 via-marine-600 to-marine-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              AI-Powered Marine Service Estimates
            </h1>
            <p className="text-xl text-marine-100 mb-8">
              Transform your service department&apos;s collective experience into instant, 
              accurate estimates. EstimateIQ analyzes thousands of similar jobs to recommend 
              the right labor hours and parts for every vessel.
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/estimate/new">
                <Button size="lg" className="bg-white text-marine-700 hover:bg-marine-100">
                  Create New Estimate
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="border-white bg-transparent text-white hover:bg-marine-600">
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why EstimateIQ?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="card-hover">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-marine-100 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-marine-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <CardTitle>80% Faster Estimates</CardTitle>
                <CardDescription>
                  Create accurate estimates in 5 minutes instead of 25+ minutes manually
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Our AI analyzes your service request and vessel specifications to instantly 
                  recommend labor hours and parts based on thousands of historical jobs.
                </p>
              </CardContent>
            </Card>

            <Card className="card-hover">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-marine-100 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-marine-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <CardTitle>Data-Driven Accuracy</CardTitle>
                <CardDescription>
                  Confidence scores show you how reliable each recommendation is
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  Every estimate shows &quot;Based on X similar jobs&quot; so you know exactly 
                  how much historical data supports the recommendation.
                </p>
              </CardContent>
            </Card>

            <Card className="card-hover">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-marine-100 flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-marine-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <CardTitle>Human-in-the-Loop</CardTitle>
                <CardDescription>
                  AI recommends, you decide - edit any line item before sending
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">
                  EstimateIQ augments your expertise, not replaces it. Review, adjust, 
                  and approve every estimate before it goes to the customer.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-marine-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-marine-600 text-white flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  1
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Enter Vessel &amp; Service
                </h3>
                <p className="text-gray-700">
                  Input vessel specs (LOA, engine, year) and describe the service needed
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-marine-600 text-white flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  2
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  AI Generates Estimate
                </h3>
                <p className="text-gray-700">
                  Our AI analyzes similar jobs and recommends labor hours and parts
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-marine-600 text-white flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  3
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Review &amp; Send
                </h3>
                <p className="text-gray-700">
                  Edit as needed, then approve and send to your customer
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Scenarios Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
            Try Demo Scenarios
          </h2>
          <p className="text-center text-gray-700 mb-12 max-w-2xl mx-auto">
            Experience EstimateIQ with pre-configured demo scenarios representing 
            common marine service requests.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <Link href="/estimate/new?demo=oil-change" className="block">
              <Card className="card-hover h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Oil Change</CardTitle>
                  <CardDescription>28&apos; Cabin Cruiser, Volvo D4, 2019</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">High confidence estimate</p>
                </CardContent>
              </Card>
            </Link>
            <Link href="/estimate/new?demo=bottom-paint" className="block">
              <Card className="card-hover h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Bottom Paint</CardTitle>
                  <CardDescription>32&apos; Sailboat, 2015</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Hull service estimate</p>
                </CardContent>
              </Card>
            </Link>
            <Link href="/estimate/new?demo=winterization" className="block">
              <Card className="card-hover h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Winterization</CardTitle>
                  <CardDescription>22&apos; Runabout, MerCruiser 4.3, 2018</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Annual service estimate</p>
                </CardContent>
              </Card>
            </Link>
            <Link href="/estimate/new?demo=diagnostic" className="block">
              <Card className="card-hover h-full">
                <CardHeader>
                  <CardTitle className="text-lg">No-Start Diagnosis</CardTitle>
                  <CardDescription>24&apos; Center Console, Yamaha F250, 2020</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Medium confidence estimate</p>
                </CardContent>
              </Card>
            </Link>
            <Link href="/estimate/new?demo=unusual" className="block">
              <Card className="card-hover h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Engine Service (Complex)</CardTitle>
                  <CardDescription>45&apos; Custom, Caterpillar C9, 2010</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Lower confidence - unusual vessel</p>
                </CardContent>
              </Card>
            </Link>
            <Link href="/estimate/new" className="block">
              <Card className="card-hover h-full border-dashed border-2 border-marine-300 bg-marine-50">
                <CardHeader>
                  <CardTitle className="text-lg text-gray-800">Custom Estimate</CardTitle>
                  <CardDescription>Enter your own vessel and service</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Start from scratch</p>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-marine-800 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your Estimates?
          </h2>
          <p className="text-xl text-marine-200 mb-8 max-w-2xl mx-auto">
            Join 1,000+ marinas using DockMaster. EstimateIQ turns 25 minutes into 5 minutes 
            for every estimate you create.
          </p>
          <Link href="/estimate/new">
            <Button size="lg" className="bg-white text-marine-700 hover:bg-marine-100">
              Create Your First Estimate
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
