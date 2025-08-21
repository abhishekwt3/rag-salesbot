// utils/subscription.ts - Subscription utilities and API functions
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface SubscriptionPlan {
  plan: string
  name: string
  amount_usd: number
  amount_inr: number
  max_knowledge_bases: number
  max_total_chunks: number
  description: string
  features: string[]
}

export interface Subscription {
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

export interface Usage {
  current_chunk_usage: number
  max_total_chunks: number
  remaining_chunks: number
  current_kb_count: number
  max_knowledge_bases: number
  can_create_kb: boolean
  plan: string
  status: string
}

export interface ChunkValidation {
  can_add: boolean
  current_usage: number
  max_allowed: number
  remaining: number
  message: string
}

export interface KnowledgeBaseValidation {
  can_create: boolean
  current_count: number
  max_allowed: number
  message: string
}

export class SubscriptionAPI {
  private token: string

  constructor(token: string) {
    this.token = token
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Plan Management
  async getPlans(): Promise<{ plans: SubscriptionPlan[] }> {
    const response = await fetch(`${API_BASE}/subscription/plans`)
    if (!response.ok) {
      throw new Error('Failed to fetch plans')
    }
    return response.json()
  }

  async getCurrentSubscription(): Promise<Subscription> {
    return this.fetchWithAuth('/subscription/current')
  }

  async getUsage(): Promise<Usage> {
    return this.fetchWithAuth('/subscription/usage')
  }

  // Subscription Creation and Management
  async createSubscription(plan: string, currency: string = 'USD', billingCycle: string = 'monthly') {
    return this.fetchWithAuth('/subscription/create', {
      method: 'POST',
      body: JSON.stringify({
        plan: plan.toLowerCase(),
        currency,
        billing_cycle: billingCycle
      })
    })
  }

  async verifyPayment(paymentData: {
    subscription_id: string
    razorpay_payment_id: string
    razorpay_order_id: string
    razorpay_signature: string
  }) {
    return this.fetchWithAuth('/subscription/payment/verify', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    })
  }

  // Usage Validation
  async validateChunkUsage(chunkCount: number): Promise<ChunkValidation> {
    return this.fetchWithAuth(`/subscription/validate/chunks/${chunkCount}`)
  }

  async validateKnowledgeBaseCreation(): Promise<KnowledgeBaseValidation> {
    return this.fetchWithAuth('/subscription/validate/knowledge-base')
  }

  // Billing and Payment History
  async getPaymentHistory() {
    try {
      return this.fetchWithAuth('/subscription/payments')
    } catch {
      // Payment history endpoint might not exist yet
      return { payments: [] }
    }
  }

  async getBillingInfo() {
    try {
      return this.fetchWithAuth('/subscription/billing')
    } catch  {
      return null
    }
  }
}

// Utility Functions
export class SubscriptionUtils {
  static formatCurrency(amount: number, currency: string): string {
    if (currency === 'INR') {
      return `₹${(amount / 100).toFixed(0)}`
    }
    return `$${(amount / 100).toFixed(2)}`
  }

  static getUsagePercentage(current: number, max: number): number {
    if (max === -1) return 0 // Unlimited
    return Math.min((current / max) * 100, 100)
  }

  static getUsageColor(percentage: number): string {
    if (percentage < 70) return 'green'
    if (percentage < 90) return 'yellow'
    return 'red'
  }

  static getPlanIcon(plan: string): string {
    switch (plan.toLowerCase()) {
      case 'basic': return 'zap'
      case 'pro': return 'crown'
      case 'enterprise': return 'building'
      default: return 'database'
    }
  }

  static getPlanColor(plan: string): string {
    switch (plan.toLowerCase()) {
      case 'basic': return 'from-blue-500 to-cyan-500'
      case 'pro': return 'from-purple-500 to-pink-500'
      case 'enterprise': return 'from-orange-500 to-red-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  static getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'active': return 'green'
      case 'trialing': return 'blue'
      case 'past_due': return 'yellow'
      case 'canceled': return 'red'
      default: return 'gray'
    }
  }

  static isUpgrade(currentPlan: string, targetPlan: string): boolean {
    const planOrder = { basic: 1, pro: 2, enterprise: 3 }
    return planOrder[targetPlan as keyof typeof planOrder] > planOrder[currentPlan as keyof typeof planOrder]
  }

  static canCreateKnowledgeBase(subscription: Subscription): boolean {
    if (subscription.max_knowledge_bases === -1) return true
    return subscription.current_kb_count < subscription.max_knowledge_bases
  }

  static canAddChunks(subscription: Subscription, chunkCount: number): boolean {
    if (subscription.max_total_chunks === -1) return true
    return (subscription.current_chunk_usage + chunkCount) <= subscription.max_total_chunks
  }

  static getRemainingChunks(subscription: Subscription): number {
    if (subscription.max_total_chunks === -1) return -1
    return Math.max(0, subscription.max_total_chunks - subscription.current_chunk_usage)
  }

  static getDaysUntilTrialEnd(subscription: Subscription): number {
    if (!subscription.trial_end) return 0
    const trialEnd = new Date(subscription.trial_end)
    const now = new Date()
    const diffTime = trialEnd.getTime() - now.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  static isTrialEnding(subscription: Subscription, warningDays: number = 3): boolean {
    if (!subscription.is_trial_active) return false
    return this.getDaysUntilTrialEnd(subscription) <= warningDays
  }

  static getUsageWarnings(subscription: Subscription): string[] {
    const warnings: string[] = []

    // Chunk usage warnings
    const chunkPercentage = this.getUsagePercentage(
      subscription.current_chunk_usage, 
      subscription.max_total_chunks
    )

    if (chunkPercentage > 90) {
      warnings.push('Critical: Data chunk limit almost reached. Upgrade immediately to avoid service disruption.')
    } else if (chunkPercentage > 80) {
      warnings.push('Warning: You have used over 80% of your data chunks. Consider upgrading your plan.')
    }

    // Knowledge base warnings
    if (!this.canCreateKnowledgeBase(subscription) && subscription.max_knowledge_bases !== -1) {
      warnings.push('Knowledge base limit reached. Upgrade to create more knowledge bases.')
    }

    // Trial warnings
    if (this.isTrialEnding(subscription)) {
      const daysLeft = this.getDaysUntilTrialEnd(subscription)
      warnings.push(`Trial ends in ${daysLeft} days. Choose a paid plan to continue using the service.`)
    }

    return warnings
  }

  static getRecommendedPlan(usage: Usage): string | null {
    if (usage.plan === 'basic') {
      if (usage.current_chunk_usage > 150 || usage.current_kb_count > 3) {
        return 'pro'
      }
    } else if (usage.plan === 'pro') {
      if (usage.current_chunk_usage > 1200 || usage.current_kb_count > 25) {
        return 'enterprise'
      }
    }
    return null
  }
}

// Custom Hooks
export function useSubscription(token: string | null) {
  const [subscription, setSubscription] = React.useState<Subscription | null>(null)
  const [usage, setUsage] = React.useState<Usage | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  const fetchData = React.useCallback(async () => {
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const api = new SubscriptionAPI(token)
      const [subData, usageData] = await Promise.all([
        api.getCurrentSubscription(),
        api.getUsage()
      ])
      
      setSubscription(subData)
      setUsage(usageData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch subscription data')
    } finally {
      setLoading(false)
    }
  }, [token])

  React.useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    subscription,
    usage,
    loading,
    error,
    refresh: fetchData,
    api: token ? new SubscriptionAPI(token) : null
  }
}

// Error Handling Utilities
export class SubscriptionErrors {
  static isLimitError(error: string): boolean {
    return error.includes('limit') || 
           error.includes('exceeded') || 
           error.includes('maximum') ||
           error.includes('upgrade')
  }

  static isPaymentError(error: string): boolean {
    return error.includes('payment') || 
           error.includes('billing') || 
           error.includes('subscription')
  }

  static getErrorMessage(error: string): string {
    if (this.isLimitError(error)) {
      return "You've reached your plan's usage limit. Please upgrade to continue."
    }
    
    if (this.isPaymentError(error)) {
      return "There's an issue with your subscription. Please check your billing information."
    }
    
    return error
  }

  static getErrorAction(error: string): { label: string; action: string } | null {
    if (this.isLimitError(error)) {
      return { label: 'Upgrade Plan', action: 'upgrade' }
    }
    
    if (this.isPaymentError(error)) {
      return { label: 'Manage Billing', action: 'billing' }
    }
    
    return null
  }
}

// Progress Calculation Utilities
export class ProgressUtils {
  static calculateProgress(current: number, max: number, segments: number = 10): number[] {
    if (max === -1) return new Array(segments).fill(0)
    
    const segmentSize = max / segments
    const progress = []
    
    for (let i = 0; i < segments; i++) {
      const segmentStart = i * segmentSize
      const segmentEnd = (i + 1) * segmentSize
      
      if (current <= segmentStart) {
        progress.push(0)
      } else if (current >= segmentEnd) {
        progress.push(100)
      } else {
        const segmentProgress = ((current - segmentStart) / segmentSize) * 100
        progress.push(segmentProgress)
      }
    }
    
    return progress
  }

  static getProgressColor(percentage: number): string {
    if (percentage < 50) return '#10B981' // green
    if (percentage < 75) return '#F59E0B' // yellow
    if (percentage < 90) return '#EF4444' // red
    return '#DC2626' // dark red
  }
}

// Export React for the custom hook
import React from 'react'