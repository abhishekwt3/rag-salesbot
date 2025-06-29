"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Bot,
  CheckCircle,
  Star,
  ArrowRight,
  Play,
  Headphones,
  MessageSquare,
  Sparkles,
} from "lucide-react"
import Link from "next/link"

// Import the new components
import Features from "./components/Features"
import Integration from "./components/Integration"
import Testimonials from "./components/Testimonials"
import Dashboard from "./components/Dashboard"
import Pricing from "./components/Pricing"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

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

export default function LandingPage() {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<"login" | "register">("login")
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState("")

  // Check for existing token on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("token")
    if (savedToken) {
      setToken(savedToken)
      fetchUserInfo(savedToken)
    } else {
      setLoading(false)
    }
  }, [])

  // Fetch user info
  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        fetchKnowledgeBases(authToken)
      } else {
        localStorage.removeItem("token")
        setToken(null)
      }
    } catch (error) {
      console.error("Error fetching user info:", error)
      localStorage.removeItem("token")
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchKnowledgeBases = async (authToken?: string) => {
    const tokenToUse = authToken || token
    if (!tokenToUse) return

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases`, {
        headers: {
          Authorization: `Bearer ${tokenToUse}`,
        },
      })

      if (response.ok) {
        const kbs = await response.json()
        setKnowledgeBases(kbs)
      }
    } catch (error) {
      console.error("Error fetching knowledge bases:", error)
    }
  }

  const handleAuth = async (email: string, password: string, fullName?: string) => {
    setAuthLoading(true)
    setAuthError("")

    try {
      const endpoint = authMode === "login" ? "/auth/login" : "/auth/register"
      const body = authMode === "login" ? { email, password } : { email, password, full_name: fullName }

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (response.ok) {
        const authToken = data.access_token
        setToken(authToken)
        setUser(data.user)
        localStorage.setItem("token", authToken)
        setShowAuthModal(false)
        fetchKnowledgeBases(authToken)
      } else {
        setAuthError(data.detail || "Authentication failed")
      }
    } catch (error) {
      setAuthError("Network error. Please try again.")
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    setToken(null)
    setUser(null)
    setKnowledgeBases([])
    localStorage.removeItem("token")
  }

  const handleGetStarted = (plan?: string) => {
    setAuthMode("register")
    setShowAuthModal(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="relative">
            <Bot className="h-16 w-16 text-brand-dark-cyan mx-auto mb-4 animate-pulse" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-brand-dark-cyan rounded-full animate-ping"></div>
          </div>
          <p className="text-brand-midnight font-medium">Loading salesbot...</p>
        </div>
      </div>
    )
  }

  // If user is logged in, show dashboard
  if (user && token) {
    return (
      <Dashboard 
        user={user}
        knowledgeBases={knowledgeBases}
        onLogout={handleLogout}
        token={token}
        onRefresh={fetchKnowledgeBases}
      />
    )
  }

  // Landing page for non-authenticated users
  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-brand-timberwolf/20 bg-white/80 backdrop-blur-md">
        <div className="container flex h-16 items-center px-4 lg:px-6">
          <Link href="/" className="flex items-center justify-center group">
            <div className="relative">
              <Bot className="h-8 w-8 text-brand-dark-cyan group-hover:text-brand-cerulean transition-colors" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-brand-dark-cyan rounded-full animate-pulse"></div>
            </div>
            <span className="ml-3 text-2xl font-display font-bold text-brand-black">salesbot</span>
          </Link>
          <nav className="ml-auto flex items-center gap-6">
            <div className="hidden md:flex items-center gap-6">
              <Link
                href="#features"
                className="text-sm font-medium text-brand-midnight hover:text-brand-dark-cyan transition-colors"
              >
                Features
              </Link>
              <Link
                href="#integration"
                className="text-sm font-medium text-brand-midnight hover:text-brand-dark-cyan transition-colors"
              >
                Integration
              </Link>
              <Link
                href="#pricing"
                className="text-sm font-medium text-brand-midnight hover:text-brand-dark-cyan transition-colors"
              >
                Pricing
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setAuthMode("login")
                  setShowAuthModal(true)
                }}
                className="border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white bg-transparent"
              >
                Sign In
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  setAuthMode("register")
                  setShowAuthModal(true)
                }}
                className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-medium"
              >
                Get Started
              </Button>
            </div>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative w-full py-16 md:py-24 lg:py-32 xl:py-40 overflow-hidden">
          <div className="absolute inset-0 bg-hero-gradient opacity-5"></div>
          <div className="absolute inset-0 bg-gradient-to-br from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5"></div>

          <div className="container relative px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[1fr_500px] lg:gap-16 xl:grid-cols-[1fr_600px] items-center">
              <div className="flex flex-col justify-center space-y-6 animate-slide-up">
                <div className="space-y-4">
                  <Badge
                    variant="secondary"
                    className="w-fit bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 font-medium"
                  >
                    <Sparkles className="w-3 h-3 mr-1" />
                    AI-Powered Sales Revolution
                  </Badge>
                  <h1 className="text-4xl font-display font-bold tracking-tight sm:text-6xl xl:text-7xl text-brand-black leading-tight">
                    Transform Your Website Into a{" "}
                    <span className="bg-gradient-to-r from-brand-dark-cyan via-brand-cerulean to-brand-midnight bg-clip-text text-transparent">
                      24/7 Sales Machine
                    </span>
                  </h1>
                  <p className="max-w-[600px] text-lg md:text-xl text-brand-midnight/80 leading-relaxed font-medium">
                    Deploy an intelligent RAG-powered salesbot that knows your products inside out. Upload documents,
                    add website URLs, and watch your conversion rates soar with AI that never sleeps.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-4">
                  <Button
                    size="lg"
                    onClick={handleGetStarted}
                    className="h-14 px-8 bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-semibold text-lg group"
                  >
                    Start Free Trial
                    <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    className="h-14 px-8 border-2 border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white font-semibold text-lg group bg-transparent"
                  >
                    <Play className="mr-2 h-5 w-5" />
                    Watch Demo
                  </Button>
                </div>

                <div className="flex flex-wrap items-center gap-6 text-sm text-brand-midnight/70">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="font-medium">No credit card required</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="font-medium">5-minute setup</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="font-medium">14-day free trial</span>
                  </div>
                </div>

                {/* Trust indicators */}
                <div className="pt-4">
                  <p className="text-sm text-brand-midnight/60 mb-3 font-medium">
                    Trusted by 10,000+ businesses worldwide
                  </p>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                    <span className="ml-2 text-sm font-semibold text-brand-midnight">4.9/5</span>
                    <span className="text-sm text-brand-midnight/60">(2,847 reviews)</span>
                  </div>
                </div>
              </div>

              {/* Chat Widget Preview */}
              <div className="flex items-center justify-center animate-fade-in">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-brand-dark-cyan/20 via-brand-cerulean/20 to-brand-midnight/20 rounded-2xl blur-3xl scale-110"></div>
                  <Card className="relative w-full max-w-md shadow-2xl border-0 bg-white/90 backdrop-blur-sm">
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <Bot className="h-8 w-8 text-brand-dark-cyan" />
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                          </div>
                          <div>
                            <CardTitle className="text-xl font-display text-brand-black">salesbot</CardTitle>
                            <p className="text-xs text-brand-midnight/60">Online • Ready to help</p>
                          </div>
                        </div>
                        <Badge className="bg-green-100 text-green-700 border-green-200">Live</Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="bg-brand-timberwolf/50 p-4 rounded-xl border-l-4 border-brand-dark-cyan">
                        <div className="flex items-start gap-2">
                          <Bot className="h-4 w-4 text-brand-dark-cyan mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-brand-black font-medium">
                            👋 Hi! I&apos;m your AI sales assistant. I can help you with product information, pricing, and
                            answer any questions about our services. What would you like to know?
                          </p>
                        </div>
                      </div>
                      <div className="bg-brand-dark-cyan/10 p-4 rounded-xl ml-8 border border-brand-dark-cyan/20">
                        <p className="text-sm text-brand-black font-medium">
                          What&apos;s the difference between your Pro and Enterprise plans?
                        </p>
                      </div>
                      <div className="bg-brand-timberwolf/50 p-4 rounded-xl border-l-4 border-brand-dark-cyan">
                        <div className="flex items-start gap-2">
                          <Bot className="h-4 w-4 text-brand-dark-cyan mt-0.5 flex-shrink-0" />
                          <div className="space-y-2">
                            <p className="text-sm text-brand-black font-medium">
                              Great question! Here&apos;s a quick comparison:
                            </p>
                            <div className="text-xs space-y-1 text-brand-midnight/80">
                              <div>
                                • <strong>Pro:</strong> 10K conversations/month, basic analytics
                              </div>
                              <div>
                                • <strong>Enterprise:</strong> Unlimited conversations, advanced analytics, priority
                                support
                              </div>
                            </div>
                            <Button
                              size="sm"
                              className="mt-2 bg-brand-dark-cyan hover:bg-brand-cerulean text-white text-xs"
                            >
                              View Full Comparison
                            </Button>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-center pt-2">
                        <div className="flex items-center gap-1 text-xs text-brand-midnight/60">
                          <div className="w-2 h-2 bg-brand-dark-cyan rounded-full animate-pulse"></div>
                          <span>AI is typing...</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="w-full py-12 bg-brand-timberwolf/30">
          <div className="container px-4 md:px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-display font-bold text-brand-dark-cyan mb-2">10K+</div>
                <p className="text-sm text-brand-midnight/70 font-medium">Active Businesses</p>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-display font-bold text-brand-dark-cyan mb-2">2M+</div>
                <p className="text-sm text-brand-midnight/70 font-medium">Conversations Handled</p>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-display font-bold text-brand-dark-cyan mb-2">300%</div>
                <p className="text-sm text-brand-midnight/70 font-medium">Avg. Lead Increase</p>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-display font-bold text-brand-dark-cyan mb-2">24/7</div>
                <p className="text-sm text-brand-midnight/70 font-medium">Always Available</p>
              </div>
            </div>
          </div>
        </section>

        {/* Use the new components */}
        <Features />
        <Integration />
        <Pricing onGetStarted={handleGetStarted} />
        <Testimonials />

        {/* CTA Section */}
        <section className="w-full py-16 md:py-24 lg:py-32 bg-gradient-to-br from-brand-dark-cyan via-brand-cerulean to-brand-midnight relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-white/0 to-white/5"></div>

          <div className="container relative px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-8 text-center">
              <div className="space-y-4">
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold tracking-tight text-white">
                  Ready to Transform Your Sales?
                </h2>
                <p className="mx-auto max-w-[600px] text-lg md:text-xl text-white/90 leading-relaxed">
                  Start your free trial today and see how salesbot can increase your conversion rates in just minutes.
                  No credit card required, no setup fees.
                </p>
              </div>

              <div className="w-full max-w-md space-y-4">
                <form className="flex gap-3">
                  <Input
                    type="email"
                    placeholder="Enter your business email"
                    className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/60 focus:bg-white/20"
                  />
                  <Button
                    type="submit"
                    size="lg"
                    className="bg-white text-brand-dark-cyan hover:bg-white/90 font-semibold px-8"
                    onClick={(e) => {
                      e.preventDefault()
                      handleGetStarted()
                    }}
                  >
                    Start Free Trial
                  </Button>
                </form>
                <div className="flex items-center justify-center gap-6 text-sm text-white/80">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>14-day free trial</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>No credit card</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>Cancel anytime</span>
                  </div>
                </div>
              </div>

              <div className="pt-8">
                <p className="text-white/60 text-sm mb-4">Or get in touch with our sales team</p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 bg-transparent">
                    <Headphones className="mr-2 h-4 w-4" />
                    Schedule Demo
                  </Button>
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 bg-transparent">
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Talk to Sales
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <Card className="w-full max-w-md mx-4 shadow-2xl border-0">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-brand-dark-cyan/10 rounded-full">
                  <Bot className="h-8 w-8 text-brand-dark-cyan" />
                </div>
              </div>
              <CardTitle className="text-2xl font-display font-bold text-brand-black">
                {authMode === "login" ? "Welcome Back" : "Get Started"}
              </CardTitle>
              <CardDescription>
                {authMode === "login"
                  ? "Sign in to your salesbot account"
                  : "Create your account and start building AI salesbots"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.currentTarget)
                  const email = formData.get("email") as string
                  const password = formData.get("password") as string
                  const fullName = formData.get("fullName") as string
                  handleAuth(email, password, fullName)
                }}
                className="space-y-4"
              >
                {authMode === "register" && (
                  <div className="space-y-2">
                    <label htmlFor="fullName" className="text-sm font-medium text-brand-black">
                      Full Name
                    </label>
                    <Input
                      id="fullName"
                      name="fullName"
                      type="text"
                      required
                      className="border-brand-timberwolf focus:border-brand-dark-cyan"
                      placeholder="Enter your full name"
                    />
                  </div>
                )}
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-brand-black">
                    Email
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    required
                    className="border-brand-timberwolf focus:border-brand-dark-cyan"
                    placeholder="Enter your email"
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium text-brand-black">
                    Password
                  </label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    required
                    className="border-brand-timberwolf focus:border-brand-dark-cyan"
                    placeholder="Enter your password"
                  />
                </div>

                {authError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{authError}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  className="w-full bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-semibold"
                  disabled={authLoading}
                >
                  {authLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      {authMode === "login" ? "Signing In..." : "Creating Account..."}
                    </div>
                  ) : authMode === "login" ? (
                    "Sign In"
                  ) : (
                    "Create Account"
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-brand-midnight/60">
                  {authMode === "login" ? "Don't have an account?" : "Already have an account?"}
                  <button
                    onClick={() => {
                      setAuthMode(authMode === "login" ? "register" : "login")
                      setAuthError("")
                    }}
                    className="ml-1 text-brand-dark-cyan hover:text-brand-cerulean font-medium"
                  >
                    {authMode === "login" ? "Sign up" : "Sign in"}
                  </button>
                </p>
              </div>
            </CardContent>
            <div className="absolute top-4 right-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAuthModal(false)}
                className="text-brand-midnight/60 hover:text-brand-black"
              >
                ✕
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Footer */}
      <footer className="w-full border-t border-brand-timberwolf/30 bg-brand-timberwolf/10">
        <div className="container px-4 md:px-6 py-12">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Bot className="h-8 w-8 text-brand-dark-cyan" />
                <span className="text-2xl font-display font-bold text-brand-black">salesbot</span>
              </div>
              <p className="text-sm text-brand-midnight/70 leading-relaxed max-w-xs">
                Transform your website into a 24/7 sales machine with AI-powered conversations that convert.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <span className="text-sm text-brand-midnight/60">4.9/5 (2,847 reviews)</span>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-display font-semibold text-brand-black">Product</h3>
              <nav className="flex flex-col space-y-2">
                <Link
                  href="/features"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Features
                </Link>
                <Link
                  href="/pricing"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Pricing
                </Link>
                <Link
                  href="/integrations"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Integrations
                </Link>
                <Link
                  href="/api"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  API
                </Link>
              </nav>
            </div>

            <div className="space-y-4">
              <h3 className="font-display font-semibold text-brand-black">Company</h3>
              <nav className="flex flex-col space-y-2">
                <Link
                  href="/about"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  About
                </Link>
                <Link
                  href="/blog"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Blog
                </Link>
                <Link
                  href="/careers"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Careers
                </Link>
                <Link
                  href="/contact"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Contact
                </Link>
              </nav>
            </div>

            <div className="space-y-4">
              <h3 className="font-display font-semibold text-brand-black">Support</h3>
              <nav className="flex flex-col space-y-2">
                <Link
                  href="/help"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Help Center
                </Link>
                <Link
                  href="/docs"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Documentation
                </Link>
                <Link
                  href="/status"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Status
                </Link>
                <Link
                  href="/security"
                  className="text-sm text-brand-midnight/70 hover:text-brand-dark-cyan transition-colors"
                >
                  Security
                </Link>
              </nav>
            </div>
          </div>

          <Separator className="my-8 bg-brand-timberwolf/50" />

          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-xs text-brand-midnight/60">© 2024 salesbot. All rights reserved.</p>
            <nav className="flex gap-6">
              <Link
                href="/privacy"
                className="text-xs text-brand-midnight/60 hover:text-brand-dark-cyan transition-colors"
              >
                Privacy Policy
              </Link>
              <Link
                href="/terms"
                className="text-xs text-brand-midnight/60 hover:text-brand-dark-cyan transition-colors"
              >
                Terms of Service
              </Link>
              <Link
                href="/cookies"
                className="text-xs text-brand-midnight/60 hover:text-brand-dark-cyan transition-colors"
              >
                Cookie Policy
              </Link>
            </nav>
          </div>
        </div>
      </footer>
    </div>
  )
}