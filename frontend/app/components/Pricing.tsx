import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  CheckCircle,
  Star,
  Zap,
  Crown,
  Building,
} from "lucide-react"

interface PricingProps {
  onGetStarted?: (plan: string) => void
}

export default function Pricing({ onGetStarted }: PricingProps) {
  const handlePlanSelect = (plan: string) => {
    if (onGetStarted) {
      onGetStarted(plan)
    }
  }

  return (
    <section id="pricing" className="w-full py-16 md:py-24 lg:py-32 bg-brand-timberwolf/20">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-6 text-center mb-16">
          <Badge
            variant="secondary"
            className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 font-medium"
          >
            <Zap className="w-3 h-3 mr-1" />
            Simple Pricing
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold tracking-tight text-brand-black">
            Choose Your{" "}
            <span className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean bg-clip-text text-transparent">
              Perfect Plan
            </span>
          </h2>
          <p className="max-w-3xl text-lg md:text-xl text-brand-midnight/80 leading-relaxed">
            Start free and scale as you grow. All plans include our core AI features with no setup fees or hidden costs.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3 max-w-6xl mx-auto mb-16">
          {/* Starter Plan */}
          <Card className="relative border-brand-timberwolf/50 hover:shadow-xl transition-all duration-300">
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 p-3 bg-brand-dark-cyan/10 rounded-full w-fit">
                <Star className="h-6 w-6 text-brand-dark-cyan" />
              </div>
              <CardTitle className="text-2xl font-display font-bold text-brand-black">Free</CardTitle>
              <CardDescription className="text-brand-midnight/70">Perfect for small businesses</CardDescription>
              <div className="mt-4">
                <div className="text-4xl font-display font-bold text-brand-black">$0</div>
                <div className="text-sm text-brand-midnight/60">per month</div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">300 conversations/month</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Unlimited knowledge bases</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">150 data chunks limit</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Email support</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Standard branding</span>
                </div>
              </div>
              <Button 
                className="w-full mt-6 bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-semibold"
                onClick={() => handlePlanSelect('starter')}
              >
                Start Free Trial
              </Button>
              <p className="text-xs text-brand-midnight/60 text-center">14-day free trial included</p>
            </CardContent>
          </Card>

          {/* Pro Plan */}
          <Card className="relative border-brand-dark-cyan shadow-xl scale-105 bg-white">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-brand-dark-cyan text-white px-4 py-1 font-semibold">
                Most Popular
              </Badge>
            </div>
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 p-3 bg-brand-cerulean/10 rounded-full w-fit">
                <Crown className="h-6 w-6 text-brand-cerulean" />
              </div>
              <CardTitle className="text-2xl font-display font-bold text-brand-black">Pro</CardTitle>
              <CardDescription className="text-brand-midnight/70">For growing businesses</CardDescription>
              <div className="mt-4">
                <div className="text-4xl font-display font-bold text-brand-black">$25</div>
                <div className="text-sm text-brand-midnight/60">per month</div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">5,000 conversations/month</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">30 knowledge bases</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">750 data chunks limit</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Priority support</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Custom branding</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">API access</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Integrations</span>
                </div>
              </div>
              <Button 
                className="w-full mt-6 bg-brand-cerulean hover:bg-brand-midnight text-white font-semibold"
                onClick={() => handlePlanSelect('pro')}
              >
                Start Free Trial
              </Button>
              <p className="text-xs text-brand-midnight/60 text-center">14-day free trial included</p>
            </CardContent>
          </Card>

          {/* Enterprise Plan */}
          <Card className="relative border-brand-timberwolf/50 hover:shadow-xl transition-all duration-300">
            <CardHeader className="text-center pb-8">
              <div className="mx-auto mb-4 p-3 bg-brand-midnight/10 rounded-full w-fit">
                <Building className="h-6 w-6 text-brand-midnight" />
              </div>
              <CardTitle className="text-2xl font-display font-bold text-brand-black">Enterprise</CardTitle>
              <CardDescription className="text-brand-midnight/70">For large organizations</CardDescription>
              <div className="mt-4">
                <div className="text-4xl font-display font-bold text-brand-black">$200</div>
                <div className="text-sm text-brand-midnight/60">per month</div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Unlimited conversations</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Unlimited knowledge bases</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Unlimited data chunks</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Dedicated support</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">White-label solution</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">SSO & SAML</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-brand-midnight/80">Custom integrations</span>
                </div>
              </div>
              <Button 
                variant="outline"
                className="w-full mt-6 border-brand-midnight text-brand-midnight hover:bg-brand-midnight hover:text-white bg-transparent font-semibold"
                onClick={() => handlePlanSelect('enterprise')}
              >
                Contact Sales
              </Button>
              <p className="text-xs text-brand-midnight/60 text-center">Custom pricing available</p>
            </CardContent>
          </Card>
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl font-display font-bold text-center text-brand-black mb-8">
            Frequently Asked Questions
          </h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">Can I change plans anytime?</h4>
              <p className="text-sm text-brand-midnight/70">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">What happens after the free trial?</h4>
              <p className="text-sm text-brand-midnight/70">
                Your trial automatically converts to the plan you selected. You can cancel anytime during the trial.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">Do you offer refunds?</h4>
              <p className="text-sm text-brand-midnight/70">
                Yes, we offer a 30-day money-back guarantee on all plans. No questions asked.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">Is there a setup fee?</h4>
              <p className="text-sm text-brand-midnight/70">
                No setup fees, ever. You only pay the monthly subscription for your selected plan.
              </p>
            </div>
          </div>
        </div>

        {/* Trust indicators */}
        <div className="text-center mt-16">
          <div className="flex items-center justify-center gap-1 mb-4">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
            ))}
            <span className="ml-2 text-lg font-semibold text-brand-midnight">4.9/5</span>
          </div>
          <p className="text-brand-midnight/70 mb-2">Trusted by 10,000+ businesses worldwide</p>
          <p className="text-sm text-brand-midnight/60">
            &quot;Best investment we&apos;ve made for our customer service. Setup was a breeze!&quot; - Sarah M., CEO
          </p>
        </div>
      </div>
    </section>
  )
}