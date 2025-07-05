"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import WidgetIntegration from "./WidgetIntegration"
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
} from "lucide-react"
import Link from "next/link"
import KnowledgeBaseManager from "./KnowledgeBaseManager"
import ChatInterface from "./ChatInterface"

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
  const [activeTab, setActiveTab] = useState<"overview" | "knowledge" | "chat" | "widgets">("overview")

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
 // const readyKnowledgeBases = knowledgeBases.filter((kb) => kb.status === "ready")
  //const totalChunks = knowledgeBases.reduce((sum, kb) => sum + kb.total_chunks, 0)

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
    switch (status) {
      case "ready":
        return "bg-green-100 text-green-800 border-green-200"
      case "processing":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "error":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center gap-3 group">
             <div className="relative">
              <Bot className="h-8 w-8 text-brand-dark-cyan group-hover:text-brand-cerulean transition-colors" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-brand-dark-cyan rounded-full animate-pulse"></div>
            </div>
            <span className=" text-4xl font-logo font-bold text-brand-midnight">Salesdok</span>     
            </Link>

            <div className="flex items-center gap-4">
              <Badge className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 px-3 py-1 text-sm font-medium">
                <Database className="w-4 h-4 mr-1" />
                {knowledgeBases.length} KBs
              </Badge>

              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10 border-2 border-brand-dark-cyan/20">
                  <AvatarFallback className="bg-brand-dark-cyan/10 text-brand-dark-cyan font-semibold text-sm">
                    {getInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden md:block">
                  <p className="text-sm font-semibold text-brand-black">{user.full_name}</p>
                  <p className="text-xs text-brand-midnight/60">{user.email}</p>
                </div>
                <Button
                  variant="outline"
                  onClick={onLogout}
                  className="border-gray-200 hover:border-red-300 hover:bg-red-50 hover:text-red-600 px-4 py-2 text-sm bg-transparent"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-8">
          <h1 className="text-2xl md:text-3xl font-display font-bold text-brand-black mb-3">
            Welcome back, {user.full_name.split(" ")[0]}! 👋
          </h1>
          <p className="text-base text-brand-midnight/70 max-w-2xl mx-auto">
            Manage your AI salesbots, train knowledge bases, and monitor performance from your dashboard.
          </p>
        </div>

        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "overview" | "knowledge" | "chat" | "widgets")} className="space-y-6">
          <div className="flex justify-center">
            <TabsList className="grid grid-cols-4 w-full max-w-2xl bg-white shadow-md border-0 p-1 h-12">
              <TabsTrigger
                value="overview"
                className="flex items-center gap-2 text-sm font-medium px-4 py-2 data-[state=active]:bg-brand-dark-cyan data-[state=active]:text-white"
              >
                <Activity className="h-4 w-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger
                value="knowledge"
                className="flex items-center gap-2 text-sm font-medium px-4 py-2 data-[state=active]:bg-brand-dark-cyan data-[state=active]:text-white"
              >
                <Database className="h-4 w-4" />
                Knowledge
              </TabsTrigger>
              <TabsTrigger
                value="chat"
                className="flex items-center gap-2 text-sm font-medium px-4 py-2 data-[state=active]:bg-brand-dark-cyan data-[state=active]:text-white"
                disabled={!selectedKB}
              >
                <MessageCircle className="h-4 w-4" />
                Test Chat
              </TabsTrigger>
              <TabsTrigger
                value="widgets"
                className="flex items-center gap-2 text-sm font-medium px-4 py-2 data-[state=active]:bg-brand-dark-cyan data-[state=active]:text-white"
              >
                <Code className="h-4 w-4" />
                Widgets
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {/* Knowledge Bases Grid */}
              <div className="lg:col-span-2">
                <Card className="bg-white border-0 shadow-md">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                          <Database className="h-5 w-5 text-brand-dark-cyan" />
                          Knowledge Bases
                        </CardTitle>
                        <CardDescription className="text-sm text-brand-midnight/60 mt-1">
                          Your AI training data and content sources
                        </CardDescription>
                      </div>
                      <Button
                        onClick={() => setActiveTab("knowledge")}
                        className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-4 py-2 text-sm font-medium"
                      >
                        <Plus className="h-4 w-4 mr-1" />
                        Create New
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {knowledgeBases.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {knowledgeBases.slice(0, 4).map((kb) => (
                          <Card
                            key={kb.id}
                            className="border border-gray-200 hover:border-brand-dark-cyan/30 hover:shadow-md transition-all duration-300 cursor-pointer p-4"
                            onClick={() => {
                              handleKBSelection(kb.id, false)
                              setActiveTab("knowledge")
                            }}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${getStatusColor(kb.status)}`}></div>
                                <Badge className={`${getStatusBadge(kb.status)} text-xs font-medium px-2 py-0.5`}>
                                  {kb.status}
                                </Badge>
                              </div>
                              <Button variant="ghost" size="sm" className="p-1 h-6 w-6">
                                <MoreVertical className="h-3 w-3" />
                              </Button>
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
                                  handleKBSelection(kb.id, true) // Auto-switch to chat when testing
                                }}
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
                              >
                                <Code className="h-3 w-3 mr-1" />
                                Embed
                              </Button>
                            </div>
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
                          className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-6 py-2 text-sm font-medium"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Create Knowledge Base
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <div className="space-y-4">
                <Card className="bg-white border-0 shadow-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-brand-black flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-brand-dark-cyan" />
                      Quick Actions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      variant="outline"
                      className="w-full justify-start h-auto p-4 border hover:border-brand-dark-cyan hover:bg-brand-dark-cyan/5 bg-transparent"
                      onClick={() => setActiveTab("knowledge")}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand-dark-cyan/10 rounded-lg">
                          <Plus className="h-4 w-4 text-brand-dark-cyan" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-medium text-brand-black">Create Knowledge Base</p>
                          <p className="text-xs text-brand-midnight/60">Upload documents and train AI</p>
                        </div>
                      </div>
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full justify-start h-auto p-4 border hover:border-brand-cerulean hover:bg-brand-cerulean/5 bg-transparent"
                      onClick={() => (selectedKB ? setActiveTab("chat") : setActiveTab("knowledge"))}
                      disabled={!selectedKB}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand-cerulean/10 rounded-lg">
                          <MessageCircle className="h-4 w-4 text-brand-cerulean" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-medium text-brand-black">Test AI Assistant</p>
                          <p className="text-xs text-brand-midnight/60">Chat with your trained bot</p>
                        </div>
                      </div>
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full justify-start h-auto p-4 border hover:border-brand-midnight hover:bg-brand-midnight/5 bg-transparent"
                      onClick={() => setActiveTab("widgets")}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand-midnight/10 rounded-lg">
                          <Code className="h-4 w-4 text-brand-midnight" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-medium text-brand-black">Get Widget Code</p>
                          <p className="text-xs text-brand-midnight/60">Embed on your website</p>
                        </div>
                      </div>
                    </Button>
                  </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card className="bg-white border-0 shadow-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-brand-black flex items-center gap-2">
                      <Activity className="h-4 w-4 text-brand-dark-cyan" />
                      Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-brand-black">Knowledge base created</p>
                          <p className="text-xs text-brand-midnight/60">2 hours ago</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-brand-black">Widget embedded</p>
                          <p className="text-xs text-brand-midnight/60">1 day ago</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-brand-black">Training completed</p>
                          <p className="text-xs text-brand-midnight/60">2 days ago</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Knowledge Bases Tab */}
          <TabsContent value="knowledge" className="space-y-6">
            <div className="max-w-5xl mx-auto">
              <Card className="bg-white border-0 shadow-md">
                <CardHeader className="pb-6">
                  <CardTitle className="text-2xl font-bold text-brand-black flex items-center gap-2">
                    <Database className="h-6 w-6 text-brand-dark-cyan" />
                    Knowledge Base Management
                  </CardTitle>
                  <CardDescription className="text-base text-brand-midnight/60 mt-2">
                    Create and manage your AI training data. Upload documents, add website URLs, and organize your
                    content.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <KnowledgeBaseManager
                    knowledgeBases={knowledgeBases}
                    selectedKB={selectedKB}
                    onSelectKB={(id) => handleKBSelection(id, false)} // Don't auto-switch tabs
                    onRefresh={onRefresh}
                    token={token}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <div className="max-w-4xl mx-auto">
              {selectedKB && selectedKnowledgeBase ? (
                <Card className="bg-white border-0 shadow-md">
                  <CardHeader className="pb-6">
                    <CardTitle className="text-2xl font-bold text-brand-black flex items-center gap-2">
                      <MessageCircle className="h-6 w-6 text-brand-dark-cyan" />
                      Test Your AI Assistant
                    </CardTitle>
                    <CardDescription className="text-base text-brand-midnight/60 mt-2">
                      Chat with your AI assistant for &quot;{selectedKnowledgeBase.name}&quot; to test responses and fine-tune
                      performance.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ChatInterface
                      knowledgeBaseId={selectedKB}
                      knowledgeBaseName={selectedKnowledgeBase.name}
                      token={token}
                    />
                  </CardContent>
                </Card>
              ) : (
                <Card className="bg-white border-0 shadow-md">
                  <CardContent className="pt-6">
                    <div className="text-center py-16">
                      <div className="w-20 h-20 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <MessageCircle className="h-10 w-10 text-brand-dark-cyan" />
                      </div>
                      <h3 className="text-xl font-semibold text-brand-black mb-3">Select a Knowledge Base</h3>
                      <p className="text-base text-brand-midnight/60 mb-6 max-w-md mx-auto">
                        Choose a knowledge base from the Knowledge tab to start testing your AI assistant.
                      </p>
                      <Button
                        onClick={() => setActiveTab("knowledge")}
                        className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-6 py-2 text-sm font-medium"
                      >
                        <Database className="h-4 w-4 mr-2" />
                        Go to Knowledge Bases
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Widgets Tab */}
        <TabsContent value="widgets" className="space-y-6">
            <WidgetIntegration 
            token={token} 
            knowledgeBases={knowledgeBases} 
          />
        </TabsContent>

      </Tabs>
        </main>
    </div>
  )
}