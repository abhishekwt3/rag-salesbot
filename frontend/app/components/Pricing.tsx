// components/Pricing.tsx - Updated with new subscription plans
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  CheckCircle,
  Star,
  Zap,
  Crown,
  Building,
  Database,
  CreditCard,
  Loader2,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface PricingProps {
  onGetStarted?: (plan: string) => void
  token?: string | null
  currentPlan?: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  currentSubscription?: any
}

interface Plan {
  plan: string
  name: string
  amount_usd: number
  amount_inr: number
  max_knowledge_bases: number
  max_total_chunks: number
  description: string
  features: string[]
}

export default function Pricing({ onGetStarted, token, currentPlan, currentSubscription }: PricingProps) {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(false)
  const [currency, setCurrency] = useState<'USD' | 'INR'>('USD')
  const [error, setError] = useState("")

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_BASE}/subscription/plans`)
      if (response.ok) {
        const data = await response.json()
        setPlans(data.plans)
      }
    } catch (error) {
      console.error('Error fetching plans:', error)
    }
  }

  const handlePlanSelect = async (plan: string) => {
    if (!token) {
      if (onGetStarted) {
        onGetStarted(plan)
      }
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_BASE}/subscription/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: plan.toLowerCase(),
          currency: currency,
          billing_cycle: 'monthly'
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.payment_link) {
          // Redirect to payment link
          window.open(data.payment_link, '_blank')
        }
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to create subscription')
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getPrice = (plan: Plan) => {
    if (currency === 'USD') {
      return `$${(plan.amount_usd / 100).toFixed(0)}`
    } else {
      return `₹${(plan.amount_inr / 100).toFixed(0)}`
    }
  }

  const getPlanIcon = (plan: string) => {
    switch (plan) {
      case 'basic':
        return <Zap className="w-5 h-5" />
      case 'pro':
        return <Crown className="w-5 h-5" />
      case 'enterprise':
        return <Building className="w-5 h-5" />
      default:
        return <Database className="w-5 h-5" />
    }
  }

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'basic':
        return 'from-blue-500 to-cyan-500'
      case 'pro':
        return 'from-purple-500 to-pink-500'
      case 'enterprise':
        return 'from-orange-500 to-red-500'
      default:
        return 'from-gray-500 to-gray-600'
    }
  }

  const isCurrentPlan = (plan: string) => {
    return currentPlan === plan
  }

  const canUpgrade = (plan: string) => {
    if (!currentPlan) return true
    
    const planOrder = { basic: 1, pro: 2, enterprise: 3 }
    return planOrder[plan as keyof typeof planOrder] > planOrder[currentPlan as keyof typeof planOrder]
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
            Start with our 7-day trial and scale as you grow. All plans include our core AI features with no setup fees.
          </p>

          {/* Currency Toggle */}
          <div className="flex items-center gap-2 bg-white rounded-lg p-1 shadow-sm border">
            <Button
              variant={currency === 'USD' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrency('USD')}
              className="text-xs"
            >
              USD ($)
            </Button>
            <Button
              variant={currency === 'INR' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setCurrency('INR')}
              className="text-xs"
            >
              INR (₹)
            </Button>
          </div>
        </div>

        {error && (
          <Alert className="mb-8 max-w-2xl mx-auto">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <Card 
              key={plan.plan}
              className={`relative overflow-hidden transition-all duration-300 hover:shadow-xl ${
                plan.plan === 'pro' ? 'border-2 border-brand-cerulean shadow-lg scale-105' : ''
              } ${isCurrentPlan(plan.plan) ? 'ring-2 ring-green-500' : ''}`}
            >
              {plan.plan === 'pro' && (
                <Badge 
                  className="absolute -top-1 left-1/2 transform -translate-x-1/2 bg-brand-cerulean text-white"
                >
                  Most Popular
                </Badge>
              )}
              
              {isCurrentPlan(plan.plan) && (
                <Badge 
                  className="absolute -top-1 right-4 bg-green-500 text-white"
                >
                  Current Plan
                </Badge>
              )}

              <CardHeader className="text-center pb-2">
                <div className={`w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-r ${getPlanColor(plan.plan)} flex items-center justify-center text-white`}>
                  {getPlanIcon(plan.plan)}
                </div>
                <CardTitle className="text-xl font-bold text-brand-black">{plan.name}</CardTitle>
                <CardDescription className="text-brand-midnight/70">
                  {plan.description}
                </CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-brand-black">
                    {getPrice(plan)}
                  </span>
                  <span className="text-brand-midnight/60 ml-1">/month</span>
                </div>
              </CardHeader>

              <CardContent className="pt-2">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-brand-dark-cyan">
                      {plan.max_knowledge_bases === -1 ? '∞' : plan.max_knowledge_bases}
                    </div>
                    <div className="text-xs text-brand-midnight/70">Knowledge Bases</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-brand-dark-cyan">
                      {plan.max_total_chunks === -1 ? '∞' : plan.max_total_chunks.toLocaleString()}
                    </div>
                    <div className="text-xs text-brand-midnight/70">Data Chunks</div>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-3 mb-6">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start gap-3">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-brand-midnight/80">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Action Button */}
                <Button 
                  className={`w-full font-semibold ${
                    plan.plan === 'pro' 
                      ? 'bg-brand-cerulean hover:bg-brand-midnight text-white' 
                      : plan.plan === 'enterprise'
                      ? 'border-brand-midnight text-brand-midnight hover:bg-brand-midnight hover:text-white bg-transparent'
                      : 'bg-brand-dark-cyan hover:bg-brand-midnight text-white'
                  }`}
                  variant={plan.plan === 'enterprise' ? 'outline' : 'default'}
                  onClick={() => handlePlanSelect(plan.plan)}
                  disabled={loading || isCurrentPlan(plan.plan) || !canUpgrade(plan.plan)}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : isCurrentPlan(plan.plan) ? (
                    'Current Plan'
                  ) : !canUpgrade(plan.plan) ? (
                    'Contact Support'
                  ) : plan.plan === 'enterprise' ? (
                    'Contact Sales'
                  ) : token ? (
                    'Upgrade Now'
                  ) : (
                    'Start Free Trial'
                  )}
                </Button>

                {plan.plan !== 'enterprise' && !isCurrentPlan(plan.plan) && (
                  <p className="text-xs text-brand-midnight/60 text-center mt-2">
                    7-day free trial included
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trial Info for logged-in users */}
        {token && currentSubscription?.is_trial_active && (
          <Alert className="mt-8 max-w-2xl mx-auto border-blue-200 bg-blue-50">
            <CreditCard className="h-4 w-4" />
            <AlertDescription>
              <strong>Trial Active:</strong> Your 7-day trial is currently active. 
              {currentSubscription.trial_end && (
                <> Trial ends on {new Date(currentSubscription.trial_end).toLocaleDateString()}.</>
              )}
            </AlertDescription>
          </Alert>
        )}

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto mt-16">
          <h3 className="text-2xl font-display font-bold text-center text-brand-black mb-8">
            Frequently Asked Questions
          </h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">How do data chunks work?</h4>
              <p className="text-sm text-brand-midnight/70">
                Data chunks are pieces of your content processed by our AI. One page typically creates 5-10 chunks. 
                The limit applies to your total chunks across all knowledge bases.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">Can I change plans anytime?</h4>
              <p className="text-sm text-brand-midnight/70">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately 
                with prorated billing.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">What happens after the trial?</h4>
              <p className="text-sm text-brand-midnight/70">
                You can choose to continue with a paid plan or your account will be paused. 
                Your data is kept safe for 30 days.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-brand-black">Do you offer refunds?</h4>
              <p className="text-sm text-brand-midnight/70">
                Yes, we offer a 30-day money-back guarantee on all plans. No questions asked.
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