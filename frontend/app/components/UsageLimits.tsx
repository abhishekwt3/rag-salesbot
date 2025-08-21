// components/UsageLimits.tsx - Display usage limits and warnings
"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Database,
  AlertTriangle,
  TrendingUp,
  Crown,
  CheckCircle,
  Zap,
} from "lucide-react"
import { SubscriptionUtils } from "../utils/subscription"

interface Usage {
  current_chunk_usage: number
  max_total_chunks: number
  remaining_chunks: number
  current_kb_count: number
  max_knowledge_bases: number
  can_create_kb: boolean
  plan: string
  status: string
}

interface UsageLimitsProps {
  usage: Usage
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  subscription?: any
  compact?: boolean
  showUpgrade?: boolean
  onUpgrade?: () => void
}

export default function UsageLimits({ 
  usage, 
  subscription, 
  compact = false, 
  showUpgrade = true,
  onUpgrade 
}: UsageLimitsProps) {
  const chunkPercentage = SubscriptionUtils.getUsagePercentage(
    usage.current_chunk_usage, 
    usage.max_total_chunks
  )
  
  const kbPercentage = SubscriptionUtils.getUsagePercentage(
    usage.current_kb_count, 
    usage.max_knowledge_bases
  )

  const warnings = subscription ? SubscriptionUtils.getUsageWarnings(subscription) : []
  const recommendedPlan = SubscriptionUtils.getRecommendedPlan(usage)

//   const getProgressColor = (percentage: number) => {
//     if (percentage < 70) return "bg-green-500"
//     if (percentage < 90) return "bg-yellow-500"
//     return "bg-red-500"
//   }

  const getPlanBadgeColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'basic':
        return 'bg-blue-500'
      case 'pro':
        return 'bg-purple-500'
      case 'enterprise':
        return 'bg-orange-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (compact) {
    return (
      <Card className="border-l-4 border-l-brand-dark-cyan">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Badge className={`${getPlanBadgeColor(usage.plan)} text-white`}>
                {usage.plan.charAt(0).toUpperCase() + usage.plan.slice(1)} Plan
              </Badge>
              <Badge variant="outline" className="text-xs">
                {usage.status}
              </Badge>
            </div>
            {showUpgrade && recommendedPlan && (
              <Button size="sm" variant="outline" onClick={onUpgrade}>
                <Crown className="h-3 w-3 mr-1" />
                Upgrade
              </Button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span>Data Chunks</span>
                <span className="font-medium">
                  {usage.current_chunk_usage}/{usage.max_total_chunks === -1 ? '∞' : usage.max_total_chunks}
                </span>
              </div>
              {usage.max_total_chunks !== -1 && (
                <Progress 
                  value={chunkPercentage} 
                  className="h-2"
                />
              )}
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span>Knowledge Bases</span>
                <span className="font-medium">
                  {usage.current_kb_count}/{usage.max_knowledge_bases === -1 ? '∞' : usage.max_knowledge_bases}
                </span>
              </div>
              {usage.max_knowledge_bases !== -1 && (
                <Progress 
                  value={kbPercentage} 
                  className="h-2"
                />
              )}
            </div>
          </div>

          {warnings.length > 0 && (
            <Alert className="mt-3 border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                {warnings[0]}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Plan Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Usage & Limits
            </CardTitle>
            <Badge className={`${getPlanBadgeColor(usage.plan)} text-white`}>
              {usage.plan.charAt(0).toUpperCase() + usage.plan.slice(1)} Plan
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Data Chunks */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-brand-dark-cyan" />
                  <span className="font-medium">Data Chunks</span>
                </div>
                <span className="text-sm text-brand-midnight/70">
                  {usage.current_chunk_usage.toLocaleString()} / {' '}
                  {usage.max_total_chunks === -1 ? 'Unlimited' : usage.max_total_chunks.toLocaleString()}
                </span>
              </div>
              
              {usage.max_total_chunks !== -1 && (
                <div className="space-y-2">
                  <Progress 
                    value={chunkPercentage} 
                    className="h-3"
                  />
                  <div className="flex justify-between text-xs text-brand-midnight/60">
                    <span>Used: {chunkPercentage.toFixed(1)}%</span>
                    <span>Remaining: {usage.remaining_chunks.toLocaleString()}</span>
                  </div>
                </div>
              )}

              {usage.max_total_chunks === -1 && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <span>Unlimited data chunks</span>
                </div>
              )}
            </div>

            {/* Knowledge Bases */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-brand-dark-cyan" />
                  <span className="font-medium">Knowledge Bases</span>
                </div>
                <span className="text-sm text-brand-midnight/70">
                  {usage.current_kb_count} / {' '}
                  {usage.max_knowledge_bases === -1 ? 'Unlimited' : usage.max_knowledge_bases}
                </span>
              </div>
              
              {usage.max_knowledge_bases !== -1 && (
                <div className="space-y-2">
                  <Progress 
                    value={kbPercentage} 
                    className="h-3"
                  />
                  <div className="flex justify-between text-xs text-brand-midnight/60">
                    <span>Used: {kbPercentage.toFixed(1)}%</span>
                    <span>Available: {usage.max_knowledge_bases - usage.current_kb_count}</span>
                  </div>
                </div>
              )}

              {usage.max_knowledge_bases === -1 && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <span>Unlimited knowledge bases</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Warnings and Alerts */}
      {warnings.length > 0 && (
        <div className="space-y-3">
          {warnings.map((warning, index) => (
            <Alert 
              key={index} 
              className={`${
                warning.includes('Critical') 
                  ? 'border-red-200 bg-red-50' 
                  : warning.includes('Warning')
                  ? 'border-yellow-200 bg-yellow-50'
                  : 'border-blue-200 bg-blue-50'
              }`}
            >
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>
                  {warning.includes('Critical') ? 'Critical:' : 
                   warning.includes('Warning') ? 'Warning:' : 'Notice:'}
                </strong>{' '}
                {warning.replace(/^(Critical:|Warning:|Notice:)\s*/, '')}
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Upgrade Recommendation */}
      {showUpgrade && recommendedPlan && (
        <Card className="border-brand-cerulean/50 bg-gradient-to-r from-brand-cerulean/5 to-brand-dark-cyan/5">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-brand-cerulean to-brand-dark-cyan flex items-center justify-center text-white">
                  <Crown className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-brand-black mb-1">
                    Upgrade to {recommendedPlan.charAt(0).toUpperCase() + recommendedPlan.slice(1)} Plan
                  </h3>
                  <p className="text-sm text-brand-midnight/70 mb-3">
                    Based on your usage patterns, we recommend upgrading to get more resources 
                    and avoid hitting limits.
                  </p>
                  <div className="flex items-center gap-4 text-sm text-brand-midnight/60">
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span>More data chunks</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span>More knowledge bases</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span>Priority support</span>
                    </div>
                  </div>
                </div>
              </div>
              <Button 
                className="bg-brand-cerulean hover:bg-brand-midnight text-white"
                onClick={onUpgrade}
              >
                <Crown className="h-4 w-4 mr-2" />
                Upgrade Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Usage Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Usage Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-brand-midnight/70">
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-dark-cyan mt-2" />
              <span>
                <strong>Data chunks</strong> are created when you add content. 
                One webpage typically creates 5-10 chunks.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-dark-cyan mt-2" />
              <span>
                <strong>Knowledge bases</strong> organize your content by topic or use case. 
                Create separate ones for different purposes.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-dark-cyan mt-2" />
              <span>
                <strong>Chunk limits</strong> apply across all your knowledge bases. 
                Monitor your usage to avoid hitting limits.
              </span>
            </div>
            {usage.plan === 'basic' && (
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-brand-cerulean mt-2" />
                <span>
                  <strong>Upgrade to Pro</strong> for 7.5x more chunks and advanced features.
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Standalone Usage Warning Component
export function UsageWarning({ 
  usage, 
  type = 'both',
  onUpgrade 
}: { 
  usage: Usage
  type?: 'chunks' | 'kb' | 'both'
  onUpgrade?: () => void 
}) {
  const chunkPercentage = SubscriptionUtils.getUsagePercentage(
    usage.current_chunk_usage, 
    usage.max_total_chunks
  )
  
  const showChunkWarning = (type === 'chunks' || type === 'both') && 
    chunkPercentage > 80 && usage.max_total_chunks !== -1
  
  const showKBWarning = (type === 'kb' || type === 'both') && 
    !usage.can_create_kb && usage.max_knowledge_bases !== -1

  if (!showChunkWarning && !showKBWarning) {
    return null
  }

  return (
    <Alert className="border-yellow-200 bg-yellow-50">
      <AlertTriangle className="h-4 w-4" />
      <AlertDescription>
        <div className="flex items-center justify-between">
          <div>
            {showChunkWarning && (
              <div className="font-medium">
                Data chunks: {chunkPercentage.toFixed(0)}% used ({usage.remaining_chunks} remaining)
              </div>
            )}
            {showKBWarning && (
              <div className="font-medium">
                Knowledge base limit reached ({usage.current_kb_count}/{usage.max_knowledge_bases})
              </div>
            )}
            <div className="text-sm mt-1">
              {chunkPercentage > 90 ? 'Upgrade immediately to avoid service disruption.' : 'Consider upgrading your plan.'}
            </div>
          </div>
          {onUpgrade && (
            <Button size="sm" variant="outline" onClick={onUpgrade}>
              Upgrade
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  )
}

// Inline Usage Display Component
export function InlineUsage({ usage }: { usage: Usage }) {
  return (
    <div className="flex items-center gap-4 text-xs text-brand-midnight/60">
      <div className="flex items-center gap-1">
        <Database className="h-3 w-3" />
        <span>
          {usage.current_chunk_usage}/{usage.max_total_chunks === -1 ? '∞' : usage.max_total_chunks} chunks
        </span>
      </div>
      <div className="flex items-center gap-1">
        <TrendingUp className="h-3 w-3" />
        <span>
          {usage.current_kb_count}/{usage.max_knowledge_bases === -1 ? '∞' : usage.max_knowledge_bases} KBs
        </span>
      </div>
      <Badge variant="outline" className="text-xs">
        {usage.plan}
      </Badge>
    </div>
  )
}