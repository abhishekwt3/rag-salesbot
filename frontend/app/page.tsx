'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/app/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/app/components/ui/tabs"
import { Input } from "@/app/components/ui/input"
import { Label } from "@/app/components/ui/label"
import { Alert, AlertDescription } from "@/app/components/ui/alert"
import { Badge } from "@/app/components/ui/badge"
import { Separator } from "@/app/components/ui/separator"
import { Avatar, AvatarFallback, AvatarInitials } from "@/app/components/ui/avatar"
import AuthModal from '@/app/components/AuthModal'
import KnowledgeBaseManager from '@/app/components/KnowledgeBaseManager'
import ChatInterface from '@/app/components/ChatInterface'
import { Bot, Database, Users, Zap, ArrowRight, Shield, Globe, MessageCircle } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
  status: 'not_ready' | 'processing' | 'ready' | 'error'
  total_chunks: number
  last_updated?: string
  created_at: string
}

export default function SaaSChatbotApp() {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)

  // Check for existing token on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      setToken(savedToken)
      fetchUserInfo(savedToken)
    } else {
      setLoading(false)
    }
  }, [])

  // Fetch user info and knowledge bases
  useEffect(() => {
    if (token && user) {
      fetchKnowledgeBases()
    }
  }, [token, user])

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem('token')
        setToken(null)
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchKnowledgeBases = async () => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const kbs = await response.json()
        setKnowledgeBases(kbs)
      }
    } catch (error) {
      console.error('Error fetching knowledge bases:', error)
    }
  }

  const handleLogin = (authToken: string, userData: User) => {
    setToken(authToken)
    setUser(userData)
    localStorage.setItem('token', authToken)
    setShowAuthModal(false)
  }

  const handleLogout = () => {
    setToken(null)
    setUser(null)
    setKnowledgeBases([])
    setSelectedKB(null)
    localStorage.removeItem('token')
  }

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user || !token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Hero Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="p-3 bg-blue-600 rounded-full">
                <Bot className="h-8 w-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
              AI Chatbots for
              <span className="text-blue-600"> Your Website</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Create intelligent chatbots powered by your own content. 
              Each chatbot learns from your specific knowledge base to provide accurate, relevant answers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                onClick={() => setShowAuthModal(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Get Started Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button variant="outline" size="lg">
                View Demo
              </Button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <Card className="border-none shadow-lg">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 p-2 bg-green-100 rounded-full w-fit">
                  <Database className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle>Your Own Knowledge Base</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Upload your website content or documents. Each user gets their own isolated knowledge base.
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 p-2 bg-purple-100 rounded-full w-fit">
                  <Shield className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle>Secure & Private</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Your data stays private. Each chatbot only answers questions based on your specific content.
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 p-2 bg-blue-100 rounded-full w-fit">
                  <Zap className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Lightning Fast</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Powered by advanced AI and vector search for instant, accurate responses to user queries.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* How it Works */}
          <div className="mt-20">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              How It Works
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="mx-auto mb-4 p-3 bg-blue-600 rounded-full w-fit">
                  <Globe className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">1. Add Your Content</h3>
                <p className="text-gray-600">
                  Enter your website URL or upload documents to create your knowledge base.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto mb-4 p-3 bg-blue-600 rounded-full w-fit">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">2. AI Learns Your Content</h3>
                <p className="text-gray-600">
                  Our AI processes and understands your content to create intelligent responses.
                </p>
              </div>
              <div className="text-center">
                <div className="mx-auto mb-4 p-3 bg-blue-600 rounded-full w-fit">
                  <MessageCircle className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">3. Deploy Your Chatbot</h3>
                <p className="text-gray-600">
                  Start chatting! Your AI assistant is ready to answer questions about your content.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Auth Modal */}
        {showAuthModal && (
          <AuthModal
            onClose={() => setShowAuthModal(false)}
            onSuccess={handleLogin}
          />
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Bot className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold">AI Chatbot SaaS</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="hidden sm:flex">
                {knowledgeBases.length} Knowledge Base{knowledgeBases.length !== 1 ? 's' : ''}
              </Badge>
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarFallback>{getInitials(user.full_name)}</AvatarFallback>
                </Avatar>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium">{user.full_name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Sidebar - Knowledge Base Manager */}
          <div className="lg:col-span-1">
            <KnowledgeBaseManager
              knowledgeBases={knowledgeBases}
              selectedKB={selectedKB}
              onSelectKB={setSelectedKB}
              onRefresh={fetchKnowledgeBases}
              token={token}
            />
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            {selectedKB ? (
              <ChatInterface
                knowledgeBaseId={selectedKB}
                knowledgeBaseName={knowledgeBases.find(kb => kb.id === selectedKB)?.name || 'Unknown'}
                token={token}
              />
            ) : (
              <Card className="h-full">
                <CardContent className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Select a Knowledge Base
                    </h3>
                    <p className="text-gray-500">
                      Choose a knowledge base from the sidebar to start chatting with your AI assistant.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}