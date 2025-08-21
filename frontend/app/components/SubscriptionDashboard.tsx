// components/SubscriptionDashboard.tsx - Complete subscription management
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
//import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  CreditCard,
  Calendar,
  Database,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Crown,
  Building,
  Zap,
  RefreshCw,
  Settings,
  Loader2,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface SubscriptionData {
  id: string
  plan: string
  status: string
  amount: number
  currency: string
  billing_cycle: string
  max_knowledge_bases: number
  max_total_chunks: number
  current_chunk_usage: number
  current_kb_count: number
  remaining_chunks: number
  trial_end?: string
  current_period_start?: string
  current_period_end?: string
  created_at: string
  is_trial_active: boolean
}

interface UsageData {
  current_chunk_usage: number
  max_total_chunks: number
  remaining_chunks: number
  current_kb_count: number
  max_knowledge_bases: number
  can_create_kb: boolean
  plan: string
  status: string
}

interface Payment {
  id: string
  amount: number
  currency: string
  status: string
  payment_method?: string
  billing_period_start?: string
  billing_period_end?: string
  paid_at?: string
  created_at: string
}

interface SubscriptionDashboardProps {
  token: string
  onSubscriptionUpdate?: () => void
}

export default function SubscriptionDashboard({ token, onSubscriptionUpdate }: SubscriptionDashboardProps) {
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null)
  const [usage, setUsage] = useState<UsageData | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchSubscriptionData()
  }, [token])

  const fetchSubscriptionData = async () => {
    setLoading(true)
    setError("")

    try {
      // Fetch subscription details
      const subResponse = await fetch(`${API_BASE}/subscription/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (subResponse.ok) {
        const subData = await subResponse.json()
        setSubscription(subData)
      }

      // Fetch usage details
      const usageResponse = await fetch(`${API_BASE}/subscription/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (usageResponse.ok) {
        const usageData = await usageResponse.json()
        setUsage(usageData)
      }

      // Fetch payment history (if endpoint exists)
      try {
        const paymentsResponse = await fetch(`${API_BASE}/subscription/payments`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (paymentsResponse.ok) {
          const paymentsData = await paymentsResponse.json()
          setPayments(paymentsData.payments || [])
        }
      } catch {
        // Payment history endpoint might not exist yet
        console.log('Payment history not available')
      }

    } catch (error) {
      setError('Failed to load subscription data')
      console.error('Error fetching subscription data:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshData = async () => {
    setRefreshing(true)
    await fetchSubscriptionData()
    setRefreshing(false)
    if (onSubscriptionUpdate) {
      onSubscriptionUpdate()
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-500'
      case 'trialing':
        return 'bg-blue-500'
      case 'past_due':
        return 'bg-yellow-500'
      case 'canceled':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusBadge = (status: string) => {
    const color = getStatusColor(status)
    return (
      <Badge className={`${color} text-white`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const formatCurrency = (amount: number, currency: string) => {
    if (currency === 'INR') {
      return `₹${(amount / 100).toFixed(0)}`
    }
    return `$${(amount / 100).toFixed(2)}`
  }

  const getUsagePercentage = (current: number, max: number) => {
    if (max === -1) return 0 // Unlimited
    return Math.min((current / max) * 100, 100)
  }

//   const getUsageColor = (percentage: number) => {
//     if (percentage < 70) return 'bg-green-500'
//     if (percentage < 90) return 'bg-yellow-500'
//     return 'bg-red-500'
//   }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-brand-dark-cyan" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!subscription || !usage) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>No subscription data found</AlertDescription>
      </Alert>
    )
  }

  const chunkUsagePercentage = getUsagePercentage(usage.current_chunk_usage, usage.max_total_chunks)
  const kbUsagePercentage = getUsagePercentage(usage.current_kb_count, usage.max_knowledge_bases)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-brand-black">Subscription & Usage</h2>
          <p className="text-brand-midnight/70">Manage your plan and monitor usage</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={refreshData}
          disabled={refreshing}
        >
          {refreshing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="usage">Usage Details</TabsTrigger>
          <TabsTrigger value="billing">Billing History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Current Plan Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean flex items-center justify-center text-white">
                    {getPlanIcon(subscription.plan)}
                  </div>
                  <div>
                    <CardTitle className="capitalize">{subscription.plan} Plan</CardTitle>
                    <CardDescription>
                      {formatCurrency(subscription.amount, subscription.currency)} per {subscription.billing_cycle}
                    </CardDescription>
                  </div>
                </div>
                <div className="text-right">
                  {getStatusBadge(subscription.status)}
                  {subscription.is_trial_active && (
                    <div className="text-sm text-brand-midnight/70 mt-1">
                      Trial ends {subscription.trial_end ? new Date(subscription.trial_end).toLocaleDateString() : 'soon'}
                    </div>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-brand-dark-cyan">
                    {usage.max_knowledge_bases === -1 ? '∞' : usage.max_knowledge_bases}
                  </div>
                  <div className="text-sm text-brand-midnight/70">Knowledge Bases</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-brand-dark-cyan">
                    {usage.max_total_chunks === -1 ? '∞' : usage.max_total_chunks.toLocaleString()}
                  </div>
                  <div className="text-sm text-brand-midnight/70">Data Chunks</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-brand-dark-cyan">
                    {subscription.currency}
                  </div>
                  <div className="text-sm text-brand-midnight/70">Currency</div>
                </div>
              </div>

              {subscription.current_period_end && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 text-blue-700">
                    <Calendar className="h-4 w-4" />
                    <span className="font-medium">Next billing date:</span>
                    <span>{new Date(subscription.current_period_end).toLocaleDateString()}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Usage Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Data Chunks Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Data Chunks Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Used: {usage.current_chunk_usage.toLocaleString()}</span>
                    <span>
                      {usage.max_total_chunks === -1 
                        ? 'Unlimited' 
                        : `of ${usage.max_total_chunks.toLocaleString()}`
                      }
                    </span>
                  </div>
                  {usage.max_total_chunks !== -1 && (
                    <Progress 
                      value={chunkUsagePercentage} 
                      className="h-2"
                    />
                  )}
                  <div className="text-xs text-brand-midnight/70">
                    {usage.max_total_chunks === -1 
                      ? 'You have unlimited data chunks'
                      : `${usage.remaining_chunks} chunks remaining`
                    }
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Knowledge Bases Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Knowledge Bases
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Created: {usage.current_kb_count}</span>
                    <span>
                      {usage.max_knowledge_bases === -1 
                        ? 'Unlimited' 
                        : `of ${usage.max_knowledge_bases}`
                      }
                    </span>
                  </div>
                  {usage.max_knowledge_bases !== -1 && (
                    <Progress 
                      value={kbUsagePercentage} 
                      className="h-2"
                    />
                  )}
                  <div className="text-xs text-brand-midnight/70">
                    {usage.can_create_kb 
                      ? 'You can create more knowledge bases'
                      : 'Knowledge base limit reached'
                    }
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Alerts */}
          {chunkUsagePercentage > 80 && usage.max_total_chunks !== -1 && (
            <Alert className="border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>Usage Warning:</strong> You&apos;ve used {chunkUsagePercentage.toFixed(0)}% of your data chunks. 
                Consider upgrading your plan to avoid service interruption.
              </AlertDescription>
            </Alert>
          )}

          {subscription.is_trial_active && (
            <Alert className="border-blue-200 bg-blue-50">
              <Clock className="h-4 w-4" />
              <AlertDescription>
                <strong>Trial Active:</strong> Your trial ends on {' '}
                {subscription.trial_end ? new Date(subscription.trial_end).toLocaleDateString() : 'soon'}.
                Choose a paid plan to continue using the service.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="usage" className="space-y-6">
          {/* Detailed Usage Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-brand-dark-cyan">
                  {usage.current_chunk_usage.toLocaleString()}
                </div>
                <p className="text-xs text-brand-midnight/70">Data Chunks Used</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-brand-dark-cyan">
                  {usage.remaining_chunks === -1 ? '∞' : usage.remaining_chunks.toLocaleString()}
                </div>
                <p className="text-xs text-brand-midnight/70">Chunks Remaining</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-brand-dark-cyan">
                  {usage.current_kb_count}
                </div>
                <p className="text-xs text-brand-midnight/70">Knowledge Bases</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-brand-dark-cyan">
                  {usage.max_knowledge_bases === -1 ? '∞' : usage.max_knowledge_bases - usage.current_kb_count}
                </div>
                <p className="text-xs text-brand-midnight/70">KB Slots Available</p>
              </CardContent>
            </Card>
          </div>

          {/* Usage Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Usage Recommendations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {chunkUsagePercentage > 90 && usage.max_total_chunks !== -1 && (
                <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                  <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
                  <div>
                    <div className="font-medium text-red-800">Critical: Chunk Limit Almost Reached</div>
                    <div className="text-sm text-red-700">Upgrade to a higher plan immediately to avoid service disruption.</div>
                  </div>
                </div>
              )}
              
              {!usage.can_create_kb && usage.max_knowledge_bases !== -1 && (
                <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
                  <div>
                    <div className="font-medium text-yellow-800">Knowledge Base Limit Reached</div>
                    <div className="text-sm text-yellow-700">You can&apos;t create more knowledge bases. Consider upgrading your plan.</div>
                  </div>
                </div>
              )}

              {chunkUsagePercentage < 50 && usage.current_kb_count < 2 && (
                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                  <div>
                    <div className="font-medium text-green-800">Great Usage Pattern</div>
                    <div className="text-sm text-green-700">You&apos;re efficiently using your allocated resources.</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing" className="space-y-6">
          {/* Billing Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Billing Summary</CardTitle>
              <CardDescription>
                Current plan: {subscription.plan} • Next billing: {' '}
                {subscription.current_period_end 
                  ? new Date(subscription.current_period_end).toLocaleDateString()
                  : 'N/A'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Next Payment</div>
                  <div className="text-sm text-brand-midnight/70">
                    {formatCurrency(subscription.amount, subscription.currency)} on{' '}
                    {subscription.current_period_end 
                      ? new Date(subscription.current_period_end).toLocaleDateString()
                      : 'N/A'
                    }
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Manage Billing
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Payment History */}
          <Card>
            <CardHeader>
              <CardTitle>Payment History</CardTitle>
            </CardHeader>
            <CardContent>
              {payments.length > 0 ? (
                <div className="space-y-3">
                  {payments.map((payment) => (
                    <div key={payment.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          payment.status === 'completed' ? 'bg-green-500' :
                          payment.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                        }`} />
                        <div>
                          <div className="font-medium">
                            {formatCurrency(payment.amount, payment.currency)}
                          </div>
                          <div className="text-sm text-brand-midnight/70">
                            {payment.paid_at ? new Date(payment.paid_at).toLocaleDateString() : new Date(payment.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant={payment.status === 'completed' ? 'default' : 'destructive'}>
                          {payment.status}
                        </Badge>
                        {payment.payment_method && (
                          <div className="text-xs text-brand-midnight/70 mt-1">
                            {payment.payment_method}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-brand-midnight/60">
                  <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No payment history available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}