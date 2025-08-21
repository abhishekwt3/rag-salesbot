// components/Dashboard.tsx - Updated with subscription integration
"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import WidgetIntegration from "./WidgetIntegration"
import SubscriptionDashboard from "./SubscriptionDashboard"
import UsageLimits, { UsageWarning, InlineUsage } from "./UsageLimits"
import Pricing from "./Pricing"
import {
  Bot,
  Database,
  LogOut,
  MessageCircle,
  Code,
  Plus,
  Activity,
  TrendingUp,
  MoreVertical,
  Play,
  Crown,
  CreditCard,
  AlertTriangle,
  Loader2,
} from "lucide-react"
import KnowledgeBaseManager from "./KnowledgeBaseManager"
import ChatInterface from "./ChatInterface"
import { useSubscription, SubscriptionUtils } from "../utils/subscription"

interface User {
  id: string
  email: string
  full_name: string
  created_at: string
}

interface KnowledgeBase {
  id: string
  name: string
  description?: string
  status: "not_ready" | "processing" | "ready" | "error"
  total_chunks: number
  last_updated?: string
  created_at: string
}

interface DashboardProps {
  user: User
  knowledgeBases: KnowledgeBase[]
  onLogout: () => void
  token: string
  onRefresh: () => void
}

export default function Dashboard({ user, knowledgeBases, onLogout, token, onRefresh }: DashboardProps) {
  const [selectedKB, setSelectedKB] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<"overview" | "knowledge" | "chat" | "widgets" | "subscription">("overview")
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)

  // Subscription data
  const { subscription, usage, loading: subscriptionLoading, error: subscriptionError, refresh: refreshSubscription } = useSubscription(token)

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  // Handle knowledge base selection with optional tab switching
  const handleKBSelection = (id: string, shouldChangeTab: boolean = false) => {
    setSelectedKB(id)
    if (id && shouldChangeTab) {
      setActiveTab("chat")
    }
  }

  const selectedKnowledgeBase = knowledgeBases.find((kb) => kb.id === selectedKB)
  const readyKnowledgeBases = knowledgeBases.filter((kb) => kb.status === "ready")
  const totalChunks = knowledgeBases.reduce((sum, kb) => sum + kb.total_chunks, 0)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
        return "bg-green-500"
      case "processing":
        return "bg-yellow-500"
      case "error":
        return "bg-red-500"
      default:
        return "bg-gray-400"
    }
  }

  const getStatusBadge = (status: string) => {
    const color = getStatusColor(status)
    return <div className={`w-2 h-2 rounded-full ${color}`}></div>
  }

  // Refresh both dashboard and subscription data
  const handleRefresh = () => {
    onRefresh()
    refreshSubscription()
  }

  // Show subscription warnings
  const showSubscriptionWarnings = () => {
    if (!subscription || !usage) return false
    
    const warnings = SubscriptionUtils.getUsageWarnings(subscription)
    return warnings.length > 0
  }

  const handleUpgradeClick = () => {
    setShowUpgradeModal(true)
  }

  const handleSubscriptionUpdate = () => {
    refreshSubscription()
    onRefresh()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean rounded-lg flex items-center justify-center">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-brand-black">Salesdok Dashboard</h1>
                  <p className="text-sm text-brand-midnight/60">Welcome back, {user.full_name}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Subscription Status */}
              {subscription && usage && (
                <div className="flex items-center gap-3">
                  <Badge className={`${SubscriptionUtils.getStatusColor(subscription.status) === 'green' ? 'bg-green-500' : 
                    SubscriptionUtils.getStatusColor(subscription.status) === 'blue' ? 'bg-blue-500' :
                    SubscriptionUtils.getStatusColor(subscription.status) === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'} text-white`}>
                    {subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1)}
                  </Badge>
                  {subscription.is_trial_active && (
                    <Badge variant="outline" className="text-blue-600 border-blue-300">
                      Trial: {SubscriptionUtils.getDaysUntilTrialEnd(subscription)}d left
                    </Badge>
                  )}
                  {showSubscriptionWarnings() && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-orange-600 border-orange-300 hover:bg-orange-50"
                      onClick={handleUpgradeClick}
                    >
                      <Crown className="h-4 w-4 mr-1" />
                      Upgrade
                    </Button>
                  )}
                </div>
              )}

              {/* User Menu */}
              <div className="flex items-center gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-brand-dark-cyan text-white text-sm">
                    {getInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
                <Button variant="outline" size="sm" onClick={onLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>

          {/* Quick Usage Display */}
          {usage && (
            <div className="mt-3 flex items-center justify-between">
              <InlineUsage usage={usage} />
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRefresh}
                  className="text-brand-midnight/60"
                >
                  <Activity className="h-4 w-4 mr-1" />
                  Refresh
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Subscription Warnings */}
      {usage && showSubscriptionWarnings() && (
        <div className="px-6 py-4 bg-yellow-50 border-b border-yellow-200">
          <UsageWarning usage={usage} onUpgrade={handleUpgradeClick} />
        </div>
      )}

      {/* Main Content */}
      <div className="px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab as never} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">Overview</span>
            </TabsTrigger>
            <TabsTrigger value="knowledge" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              <span className="hidden sm:inline">Knowledge</span>
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Chat</span>
            </TabsTrigger>
            <TabsTrigger value="widgets" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              <span className="hidden sm:inline">Widgets</span>
            </TabsTrigger>
            <TabsTrigger value="subscription" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              <span className="hidden sm:inline">Billing</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                      <Database className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-brand-black">{knowledgeBases.length}</div>
                      <p className="text-xs text-brand-midnight/60">Knowledge Bases</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                      <TrendingUp className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-brand-black">{totalChunks.toLocaleString()}</div>
                      <p className="text-xs text-brand-midnight/60">Data Chunks</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
                      <MessageCircle className="h-6 w-6 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-brand-black">{readyKnowledgeBases.length}</div>
                      <p className="text-xs text-brand-midnight/60">Ready for Chat</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
                      <Code className="h-6 w-6 text-orange-600" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-brand-black">0</div>
                      <p className="text-xs text-brand-midnight/60">Active Widgets</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Usage Overview */}
            {usage && !subscriptionLoading && (
              <UsageLimits 
                usage={usage} 
                subscription={subscription}
                onUpgrade={handleUpgradeClick}
              />
            )}

            {/* Recent Knowledge Bases */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Recent Knowledge Bases</CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActiveTab("knowledge")}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add New
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {knowledgeBases.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {knowledgeBases.slice(0, 6).map((kb) => (
                      <Card
                        key={kb.id}
                        className={`cursor-pointer transition-all duration-200 hover:shadow-md border ${
                          selectedKB === kb.id ? "ring-2 ring-brand-dark-cyan border-brand-dark-cyan" : ""
                        }`}
                        onClick={() => handleKBSelection(kb.id)}
                      >
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between mb-3">
                            {getStatusBadge(kb.status)}
                            <div className="flex items-center gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                              >
                                <MoreVertical className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                          <h3 className="text-base font-semibold text-brand-black mb-2 truncate">{kb.name}</h3>
                          <p className="text-sm text-brand-midnight/60 mb-3">
                            {kb.total_chunks.toLocaleString()} chunks
                          </p>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1 text-xs py-1.5 bg-transparent"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleKBSelection(kb.id, true)
                              }}
                              disabled={kb.status !== "ready"}
                            >
                              <Play className="h-3 w-3 mr-1" />
                              Test
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1 text-xs py-1.5 bg-transparent"
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedKB(kb.id)
                                setActiveTab("widgets")
                              }}
                              disabled={kb.status !== "ready"}
                            >
                              <Code className="h-3 w-3 mr-1" />
                              Embed
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Database className="h-8 w-8 text-brand-dark-cyan" />
                    </div>
                    <h3 className="text-lg font-semibold text-brand-black mb-2">No Knowledge Bases Yet</h3>
                    <p className="text-sm text-brand-midnight/60 mb-4 max-w-sm mx-auto">
                      Create your first knowledge base to start building your AI salesbot.
                    </p>
                    <Button
                      onClick={() => setActiveTab("knowledge")}
                      className="bg-brand-dark-cyan hover:bg-brand-midnight text-white"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Create Knowledge Base
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="knowledge">
            <KnowledgeBaseManager
              knowledgeBases={knowledgeBases}
              selectedKB={selectedKB}
              onSelectKB={setSelectedKB}
              onRefresh={handleRefresh}
              token={token}
              usage={usage ?? undefined}
              onUpgrade={handleUpgradeClick}
            />
          </TabsContent>

          <TabsContent value="chat">
            {selectedKB && selectedKnowledgeBase && selectedKnowledgeBase.status === "ready" ? (
              <ChatInterface
                knowledgeBaseId={selectedKB}
                knowledgeBaseName={selectedKnowledgeBase.name}
                token={token}
              />
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <MessageCircle className="h-16 w-16 text-brand-midnight/30 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-brand-black mb-2">No Knowledge Base Selected</h3>
                    <p className="text-brand-midnight/60 mb-4">
                      Select a ready knowledge base to start chatting
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => setActiveTab("knowledge")}
                    >
                      Select Knowledge Base
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="widgets">
            <WidgetIntegration token={token} knowledgeBases={knowledgeBases} />
          </TabsContent>

          <TabsContent value="subscription">
            {subscriptionLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-brand-dark-cyan" />
              </div>
            ) : subscriptionError ? (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{subscriptionError}</AlertDescription>
              </Alert>
            ) : (
              <SubscriptionDashboard 
                token={token} 
                onSubscriptionUpdate={handleSubscriptionUpdate}
              />
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Upgrade Modal */}
      <Dialog open={showUpgradeModal} onOpenChange={setShowUpgradeModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Upgrade Your Plan</DialogTitle>
            <DialogDescription>
              Choose a plan that fits your needs and unlock more features.
            </DialogDescription>
          </DialogHeader>
          <Pricing 
            token={token}
            currentPlan={subscription?.plan}
            currentSubscription={subscription}
            onGetStarted={() => {
              setShowUpgradeModal(false)
              // Handle plan selection
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}