'use client'

import { useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ArrowRight,
  Play,
  CheckCircle,
  Sparkles,
  MessageSquare,
  Bot,
} from "lucide-react"

interface HeroSectionProps {
  onGetStarted?: () => void
  onWatchDemo?: () => void
}

export default function HeroSection({ onGetStarted, onWatchDemo }: HeroSectionProps) {
  useEffect(() => {
    // Load the Salesdok widget
    const script = document.createElement('script')
    script.src = 'https://api.salesdok.com/widget/widget_ad697e71e16e4a67/script.js'
    script.async = true
    document.head.appendChild(script)

    // Widget positioning logic
    const moveWidgetToMockup = () => {
      const widgetSelectors = [
        '#salesdok-widget',
        '[id*="salesdok"]',
        '[class*="salesdok"]',
        '[class*="widget"]',
        '[id*="widget"]',
        'div[style*="position: fixed"][style*="bottom"][style*="right"]'
      ]
      
      let widget = null
      
      for (const selector of widgetSelectors) {
        const elements = document.querySelectorAll(selector)
        if (elements.length > 0) {
          widget = elements[elements.length - 1] as HTMLElement
          break
        }
      }
      
      if (widget && widget.offsetParent !== null) {
        const target = document.getElementById('widget-target')
        if (target && !target.hasChildNodes()) {
          const widgetClone = widget.cloneNode(true) as HTMLElement
          
          // Reset positioning
          widgetClone.style.position = 'relative'
          widgetClone.style.bottom = 'auto'
          widgetClone.style.right = 'auto'
          widgetClone.style.top = 'auto'
          widgetClone.style.left = 'auto'
          widgetClone.style.zIndex = '50'
          widgetClone.style.maxWidth = '300px'
          
          // Hide original widget
          widget.style.display = 'none'
          
          target.appendChild(widgetClone)
          return true
        }
      }
      
      return false
    }
    
    let attempts = 0
    const maxAttempts = 20
    
    const tryMoveWidget = () => {
      attempts++
      
      if (moveWidgetToMockup()) {
        console.log('Widget successfully positioned in mockup')
        return
      }
      
      if (attempts < maxAttempts) {
        setTimeout(tryMoveWidget, 500)
      } else {
        // Fallback: create a placeholder
        const target = document.getElementById('widget-target')
        if (target && !target.hasChildNodes()) {
          target.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl border max-w-xs">
              <div class="bg-brand-dark-cyan text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
                <h4 class="font-semibold text-sm">Chat Support</h4>
                <button class="text-white/80 hover:text-white">×</button>
              </div>
              <div class="p-4 space-y-3">
                <div class="bg-gray-100 rounded-lg p-3 text-sm">
                  Widget is loading... Please wait.
                </div>
              </div>
              <div class="text-center py-2 text-xs text-gray-500">
                Powered by <span class="text-brand-dark-cyan font-medium">Salesdok</span>
              </div>
            </div>
          `
        }
      }
    }
    
    // Start trying to move widget after delay
    const timer = setTimeout(tryMoveWidget, 1000)
    
    return () => {
      clearTimeout(timer)
      document.head.removeChild(script)
    }
  }, [])

  return (
    <>
      {/* Add custom styles */}
      <style jsx>{`
        .bg-grid-pattern {
          background-image: 
            linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px);
          background-size: 20px 20px;
        }
        
        /* Override widget positioning */
        :global(#salesdok-widget),
        :global([id*="salesdok"]),
        :global([class*="salesdok"]) {
          position: absolute !important;
          bottom: 20px !important;
          right: 20px !important;
          z-index: 50 !important;
          max-width: 350px !important;
        }
        
        /* Hide default floating widget */
        :global(body > div[style*="position: fixed"]),
        :global(body > div[style*="bottom"]),
        :global(body > div[style*="right"]) {
          display: none !important;
        }
      `}</style>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-white via-brand-powder/10 to-brand-cerulean/5 py-20 lg:py-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="container relative px-4 lg:px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center max-w-7xl mx-auto">
            {/* Left Column - Content */}
            <div className="text-center lg:text-left">
              <Badge className="mb-6 bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 px-4 py-2 text-sm font-medium">
                <Sparkles className="w-4 h-4 mr-2" />
                AI-Powered Sales Assistant
              </Badge>
              <h1 className="mb-6 text-4xl font-bold tracking-tight text-brand-black lg:text-6xl font-display">
                Convert Visitors into{" "}
                <span className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean bg-clip-text text-transparent">
                  Customers
                </span>{" "}
                with AI
              </h1>
              <p className="mb-8 text-lg text-brand-midnight/70 lg:text-xl">
                Deploy intelligent chatbots that understand your business, answer questions instantly, and guide prospects
                through your sales funnel 24/7.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button
                  size="lg"
                  onClick={onGetStarted}
                  className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-8 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={onWatchDemo}
                  className="border-brand-dark-cyan text-brand-dark-cyan hover:bg-brand-dark-cyan hover:text-white px-8 py-3 text-lg font-semibold bg-transparent"
                >
                  <Play className="mr-2 h-5 w-5" />
                  Watch Demo
                </Button>
              </div>
              <div className="mt-12 flex justify-center lg:justify-start gap-8 text-sm text-brand-midnight/60">
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
            </div>

            {/* Right Column - Live Widget Preview */}
            <div className="relative z-10">
              <div className="relative bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl p-8 shadow-2xl">
                {/* Browser mockup */}
                <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                  <div className="bg-gray-100 px-4 py-3 flex items-center gap-2">
                    <div className="flex gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-400"></div>
                      <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                      <div className="w-3 h-3 rounded-full bg-green-400"></div>
                    </div>
                    <div className="flex-1 text-center">
                      <div className="bg-white rounded px-3 py-1 text-xs text-gray-500">
                        yourwebsite.com
                      </div>
                    </div>
                  </div>
                  <div className="h-80 bg-gradient-to-br from-blue-50 to-indigo-100 relative overflow-visible">
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                      <div className="text-center">
                        <div className="text-4xl mb-2">🏢</div>
                        <div className="text-sm">Your Website</div>
                        <div className="text-xs mt-2 text-brand-dark-cyan font-medium">Try the live chat widget!</div>
                      </div>
                    </div>
                    
                    {/* Widget will appear here */}
                    <div id="widget-target" className="absolute bottom-4 right-4 z-50"></div>
                  </div>
                </div>
                
                {/* Floating elements */}
                <div className="absolute -top-4 -left-4 bg-brand-dark-cyan text-white rounded-full p-3 shadow-lg">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <div className="absolute -bottom-4 -right-4 bg-brand-cerulean text-white rounded-full p-3 shadow-lg">
                  <Bot className="w-6 h-6" />
                </div>
              </div>
              
              {/* Pulse animation */}
              <div className="absolute -top-2 -right-2 w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
              
              {/* Live Widget Notice */}
              <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-brand-dark-cyan text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                Live Widget Active
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}