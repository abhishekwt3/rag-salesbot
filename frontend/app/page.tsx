"use client"
import { useState, useEffect, useCallback } from "react"
import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import Script from "next/script"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Bot,
  CheckCircle,
  ArrowRight,
  Play,
  Sparkles,
  Loader2,
  AlertCircle,
  Zap,
  Users,
  TrendingUp,
} from "lucide-react"
import { FaGoogle } from "react-icons/fa"
import Link from "next/link"

// Import the new components
import Features from "./components/Features"
import Integration from "./components/Integration"
import Testimonials from "./components/Testimonials"
import Dashboard from "./components/Dashboard"
import Pricing from "./components/Pricing"
import YouTubeModal from "./components/YouTubeModal"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://api.salesdok.com"

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
  const [loginForm, setLoginForm] = useState({ email: "", password: "" })
  const [registerForm, setRegisterForm] = useState({
    email: "",
    password: "",
    full_name: "",
    confirmPassword: "",
  })

  // YouTube Modal State
  const [showVideoModal, setShowVideoModal] = useState(false)
  const videoId = "RzSYv7bkrpc" // Extracted from https://youtu.be/RzSYv7bkrpc?si=rCiq0vkZHtCrpw7s

  const handleWatchDemo = () => {
    setShowVideoModal(true)
  }

  // Enhanced session expiration handler
  const handleSessionExpired = useCallback(() => {
    console.log("Session expired, redirecting to homepage")
    setToken(null)
    setUser(null)
    setKnowledgeBases([])
    localStorage.removeItem("token")
    setShowAuthModal(false)
    // Force a clean state reset
    window.location.reload()
  }, [])

  // Enhanced API call with session handling
  // (makeAuthenticatedRequest removed because it was unused)

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

  // Handle OAuth callback
  useEffect(() => {
    const handleOAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const oauthToken = urlParams.get("token")
      const error = urlParams.get("error")

      if (error) {
        setAuthError(decodeURIComponent(error))
        setShowAuthModal(true)
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname)
        return
      }

      if (oauthToken) {
        try {
          // Fetch user info
          const userResponse = await fetch(`${API_BASE}/auth/me`, {
            headers: {
              Authorization: `Bearer ${oauthToken}`,
            },
          })

          if (userResponse.ok) {
            const userData = await userResponse.json()
            setToken(oauthToken)
            setUser(userData)
            localStorage.setItem("token", oauthToken)
            await fetchKnowledgeBases(oauthToken)

            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname)
          } else {
            setAuthError("Failed to fetch user information")
            setShowAuthModal(true)
          }
        } catch {
          setAuthError("Authentication failed")
          setShowAuthModal(true)
        }

        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname)
      }
    }

    handleOAuthCallback()
  }, [])

  // Fetch user info with enhanced error handling
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
        await fetchKnowledgeBases(authToken)
      } else if (response.status === 401) {
        // Session expired
        handleSessionExpired()
      } else {
        // Other error
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
      } else if (response.status === 401) {
        handleSessionExpired()
      }
    } catch (error) {
      console.error("Error fetching knowledge bases:", error)
    }
  }

  // OAuth handlers
  const handleGoogleAuth = async () => {
    setAuthLoading(true)
    setAuthError("")

    try {
      // Redirect to Google OAuth
      window.location.href = `${API_BASE}/auth/google`
    } catch {
      setAuthError("Failed to initialize Google authentication")
      setAuthLoading(false)
    }
  }

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setAuthLoading(true)
    setAuthError("")
    try {
      const endpoint = authMode === "login" ? "/auth/login" : "/auth/register"
      const formData = authMode === "login" ? loginForm : registerForm

      // Validation for register mode
      if (authMode === "register") {
        if (!registerForm.full_name.trim()) {
          setAuthError("Full name is required")
          setAuthLoading(false)
          return
        }
        if (registerForm.password !== registerForm.confirmPassword) {
          setAuthError("Passwords do not match")
          setAuthLoading(false)
          return
        }
        if (registerForm.password.length < 6) {
          setAuthError("Password must be at least 6 characters long")
          setAuthLoading(false)
          return
        }
      }

      const body =
        authMode === "login"
          ? { email: formData.email, password: formData.password }
          : {
              email: registerForm.email,
              password: registerForm.password,
              full_name: registerForm.full_name,
            }

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

        // Fetch user info to ensure we have complete user data
        let userData = data.user
        if (!userData) {
          const userResponse = await fetch(`${API_BASE}/auth/me`, {
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          })
          if (userResponse.ok) {
            userData = await userResponse.json()
          }
        }

        // Set all state atomically
        setToken(authToken)
        setUser(userData)
        localStorage.setItem("token", authToken)

        // Close modal and clear forms
        setShowAuthModal(false)
        setLoginForm({ email: "", password: "" })
        setRegisterForm({ email: "", password: "", full_name: "", confirmPassword: "" })
        setAuthError("")

        // Fetch knowledge bases
        await fetchKnowledgeBases(authToken)

        // Force re-render to dashboard (this ensures immediate redirect)
        setTimeout(() => {
          if (!user) {
            window.location.reload()
          }
        }, 100)
      } else {
        setAuthError(data.detail || "Authentication failed")
      }
    } catch {
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
    setShowAuthModal(false)
  }

  const handleGetStarted = () => {
    setAuthMode("register")
    setShowAuthModal(true)
  }

  // Function to open video modal

  // Enhanced loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="relative">
            <Bot className="h-16 w-16 text-brand-dark-cyan mx-auto mb-4 animate-pulse" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-brand-dark-cyan rounded-full animate-ping"></div>
          </div>
          <p className="text-brand-midnight font-medium">Loading Salesdok...</p>
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
        onRefresh={() => fetchKnowledgeBases()}
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
            <span className="ml-3 text-4xl font-logo font-bold text-brand-midnight">Salesdok</span>
          </Link>

          <nav className="ml-auto flex items-center gap-6">
            <div className="hidden md:flex items-center gap-6">
              <Link
                href="/blog"
                className="text-sm font-medium text-brand-midnight hover:text-brand-dark-cyan transition-colors"
              >
                Blog
              </Link>
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

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-white via-brand-powder/10 to-brand-cerulean/5 py-20 lg:py-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="container relative px-4 lg:px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center max-w-7xl mx-auto">
            {/* Left Column - Content */}
            <div className="text-center lg:text-left space-y-8">
              <div className="space-y-6">
                <Badge className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 px-4 py-2 text-sm font-medium">
                  <Sparkles className="w-4 h-4 mr-2" />
                  AI-Powered Sales Assistant
                </Badge>

                <h1 className="text-4xl font-bold tracking-tight text-brand-black lg:text-6xl font-display leading-tight">
                  Convert Visitors into{" "}
                  <span className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean bg-clip-text text-transparent">
                    Customers
                  </span>{" "}
                  with AI
                </h1>

                <p className="text-lg text-brand-midnight/70 lg:text-xl max-w-2xl">
                  Intelligent AI chat agents that understand your business, answer questions instantly, and guide
                  prospects through your sales funnel 24/7.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button
                  size="lg"
                  onClick={() => handleGetStarted()}
                  className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                >
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={handleWatchDemo}
                  className="border-brand-dark-cyan text-brand-dark-cyan hover:bg-brand-dark-cyan hover:text-white px-8 py-4 text-lg font-semibold bg-transparent"
                >
                  <Play className="mr-2 h-5 w-5" />
                  Watch Demo
                </Button>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-wrap justify-center lg:justify-start gap-6 text-sm text-brand-midnight/60">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  No credit card required
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Setup in 5 minutes
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  24/7 support
                </div>
              </div>

              {/* Social Proof Stats */}
              <div className="grid grid-cols-3 gap-6 pt-8 border-t border-brand-timberwolf/20">
                <div className="text-center">
                  <div className="text-2xl font-bold text-brand-dark-cyan">10K+</div>
                  <div className="text-sm text-brand-midnight/60">Active Users</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-brand-dark-cyan">40%</div>
                  <div className="text-sm text-brand-midnight/60">Avg. Conversion Boost</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-brand-dark-cyan">24/7</div>
                  <div className="text-sm text-brand-midnight/60">Always Available</div>
                </div>
              </div>
            </div>

            {/* Right Column - GIF/Demo Area */}
            <div className="relative">
     <video>
      
     </video>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <Features />

      {/* Integration Section */}
      <Integration />

      {/* Testimonials */}
      <Testimonials />

      {/* Pricing */}
      <Pricing onGetStarted={handleGetStarted} />

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean py-20">
        <div className="container px-4 lg:px-6">
          <div className="mx-auto max-w-3xl text-center text-white">
            <h2 className="mb-4 text-3xl font-bold lg:text-4xl font-display">Ready to Transform Your Sales Process?</h2>
            <p className="mb-8 text-lg opacity-90">
              Join thousands of businesses already using AI to boost their conversion rates and sales.
            </p>
            <Button
              size="lg"
              onClick={() => handleGetStarted()}
              className="bg-white text-brand-dark-cyan hover:bg-gray-100 px-8 py-3 text-lg font-semibold shadow-lg transform hover:scale-105 transition-all"
            >
              Get Started Today
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      <YouTubeModal
        isOpen={showVideoModal}
        onClose={() => setShowVideoModal(false)}
        videoId={videoId}
        title="Salesdok Demo Video"
      />

      {/* AI Chatbot Widget Script */}
      <Script
        id="salesdok-chatbot-script" // Unique ID for the script
        src="https://api.salesdok.com/widget/widget_1bc5682831ae4010/script.js"
        strategy="lazyOnload" // Or "afterInteractive", "beforeInteractive"
      />

      {/* Footer */}
      <footer className="border-t border-brand-timberwolf/20 bg-white py-12">
        <div className="container px-4 lg:px-6">
          <div className="grid gap-8 lg:grid-cols-4">
            <div className="lg:col-span-2">
              <Link href="/" className="flex items-center gap-3 mb-4">
                <Bot className="h-8 w-8 text-brand-dark-cyan" />
                <span className="text-3xl font-logo font-bold text-brand-midnight">Salesdok</span>
              </Link>
              <p className="text-brand-midnight/60 max-w-md">
                The most powerful AI sales assistant for modern businesses. Automate your customer interactions and
                boost conversions.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-brand-black mb-4">Product</h3>
              <ul className="space-y-2 text-brand-midnight/60">
                <li>
                  <Link href="#features" className="hover:text-brand-dark-cyan transition-colors">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="#integration" className="hover:text-brand-dark-cyan transition-colors">
                    Integration
                  </Link>
                </li>
                <li>
                  <Link href="#pricing" className="hover:text-brand-dark-cyan transition-colors">
                    Pricing
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-brand-black mb-4">Support</h3>
              <ul className="space-y-2 text-brand-midnight/60">
                <li>
                  <Link href="#" className="hover:text-brand-dark-cyan transition-colors">
                    Documentation
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-brand-dark-cyan transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-brand-dark-cyan transition-colors">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Compliance Section */}
          <div className="mt-4 pt-6 border-t border-brand-timberwolf/20">
            <div className="flex flex-col items-center space-y-4">
              <p className="text-sm text-brand-midnight/60 font-medium">
                Salesdok is compliant by SOC2, PCI DSS, uses AES-256 Encryption, and GDPR Ready
              </p>
              <div className="flex flex-wrap items-center justify-center gap-6">
                {/* SOC2 Compliance Logo */}
                <div className="group cursor-pointer">
                  <img
                    src="https://ik.imagekit.io/90xvn3fidvl/salesdok-soc2_F2uA39lEs.png"
                    alt="SOC 2 Type II Compliant"
                    className="h-12 w-auto opacity-80 group-hover:opacity-100 transition-opacity"
                  />
                </div>

                {/* PCI DSS Compliance Logo */}
                <div className="group cursor-pointer">
                  <img
                    src="https://ik.imagekit.io/90xvn3fidvl/salesdok-pci-dss_sZba9QwWd.png"
                    alt="PCI DSS Compliant"
                    className="h-12 w-auto opacity-80 group-hover:opacity-100 transition-opacity"
                  />
                </div>

                {/* AES Encryption Logo */}
                <div className="group cursor-pointer">
                  <img
                    src="https://ik.imagekit.io/90xvn3fidvl/AES256_mha8Hcxga.webp"
                    alt="AES-256 Encryption"
                    className="h-12 w-auto opacity-80 group-hover:opacity-100 transition-opacity"
                  />
                </div>

                {/* GDPR Compliance Logo */}
                <div className="group cursor-pointer">
                  <img
                    src="https://ik.imagekit.io/90xvn3fidvl/GDPR-ready_omM9jc7iw7.png"
                    alt="GDPR Ready"
                    className="h-12 w-auto opacity-80 group-hover:opacity-100 transition-opacity"
                  />
                </div>
              </div>
            </div>
          </div>

          <Separator className="my-4" />
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-brand-midnight/60 text-sm">© 2025 Salesdok. All rights reserved.</p>
            <div className="flex gap-4 text-brand-midnight/60 text-sm">
              <Link href="/privacy" className="hover:text-brand-dark-cyan transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms" className="hover:text-brand-dark-cyan transition-colors">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>
      </footer>

      {/* Enhanced Auth Modal with OAuth */}
      <Dialog open={showAuthModal} onOpenChange={setShowAuthModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-center">
              {authMode === "login" ? "Welcome Back" : "Get Started"}
            </DialogTitle>
            <DialogDescription className="text-center">
              {authMode === "login"
                ? "Sign in to your account to continue"
                : "Create your account and start building AI chatbots"}
            </DialogDescription>
          </DialogHeader>

          <Tabs
            value={authMode}
            onValueChange={(value) => setAuthMode(value as "login" | "register")}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Sign In</TabsTrigger>
              <TabsTrigger value="register">Sign Up</TabsTrigger>
            </TabsList>

            <div className="space-y-4">
              {/* Social Login Buttons */}
              <div className="space-y-3">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full flex items-center justify-center gap-2 h-11 hover:bg-red-50 hover:border-red-200 transition-all bg-transparent"
                  onClick={handleGoogleAuth}
                  disabled={authLoading}
                >
                  <FaGoogle className="h-5 w-5 text-blue-500" />
                  Continue with Google
                </Button>
              </div>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">Or continue with email</span>
                </div>
              </div>

              {/* Email/Password Form */}
              <form onSubmit={handleAuth} className="space-y-4">
                <TabsContent value="login" className="space-y-4 mt-0">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={loginForm.email}
                      onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      value={loginForm.password}
                      onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                      placeholder="Enter your password"
                      required
                    />
                  </div>
                </TabsContent>

                <TabsContent value="register" className="space-y-4 mt-0">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      type="text"
                      value={registerForm.full_name}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, full_name: e.target.value }))}
                      placeholder="Enter your full name"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg_email">Email</Label>
                    <Input
                      id="reg_email"
                      type="email"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg_password">Password</Label>
                    <Input
                      id="reg_password"
                      type="password"
                      value={registerForm.password}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, password: e.target.value }))}
                      placeholder="Create a password"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm_password">Confirm Password</Label>
                    <Input
                      id="confirm_password"
                      type="password"
                      value={registerForm.confirmPassword}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                      placeholder="Confirm your password"
                      required
                    />
                  </div>
                </TabsContent>

                {authError && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{authError}</AlertDescription>
                  </Alert>
                )}

                <Button
                  type="submit"
                  className="w-full bg-brand-dark-cyan hover:bg-brand-cerulean text-white"
                  disabled={authLoading}
                >
                  {authLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {authMode === "login" ? "Signing In..." : "Creating Account..."}
                    </>
                  ) : authMode === "login" ? (
                    "Sign In"
                  ) : (
                    "Create Account"
                  )}
                </Button>
              </form>
            </div>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  )
}
