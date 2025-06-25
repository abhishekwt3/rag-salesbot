'use client'

import { useState, useEffect, useRef } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  id: number
  text: string
  isBot: boolean
  timestamp: Date
  confidence?: number
  sources?: Array<{
    url: string
    title: string
    relevance_score: number
  }>
}

interface SystemStatus {
  status: string
  total_chunks: number
  last_updated?: string
}

// Simple icon components (no external dependencies)
const SendIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
)

const SettingsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
)

const GlobeIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
  </svg>
)

const LoaderIcon = () => (
  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
)

const CheckIcon = () => (
  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
)

const AlertIcon = () => (
  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
)

const ExternalIcon = () => (
  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
  </svg>
)

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm your AI assistant. I can answer questions about your website content. First, let me know your website URL to get started.",
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [showSetup, setShowSetup] = useState(false)
  const [websiteUrl, setWebsiteUrl] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Check system status on load
  useEffect(() => {
    checkSystemStatus()
  }, [])

  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`)
      const status = await response.json()
      setSystemStatus(status)
    } catch (error) {
      console.error('Error checking status:', error)
      setSystemStatus({ status: 'error', total_chunks: 0 })
    }
  }

  const handleSetupWebsite = async () => {
    if (!websiteUrl.trim()) return

    setIsLoading(true)
    const setupMessage: Message = {
      id: Date.now(),
      text: `Setting up website: ${websiteUrl}`,
      isBot: false,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, setupMessage])

    try {
      const response = await fetch(`${API_BASE}/setup-website`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: websiteUrl,
          max_pages: 50,
          exclude_patterns: ['/blog', '/news']
        })
      })

      if (response.ok) {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          text: "Great! I'm now processing your website content. This may take a few minutes. You can start asking questions once I'm ready!",
          isBot: true,
          timestamp: new Date()
        }])
        setShowSetup(false)
        setWebsiteUrl('')
        
        // Poll for status updates
        const pollInterval = setInterval(async () => {
          await checkSystemStatus()
          try {
            const currentStatus = await fetch(`${API_BASE}/status`).then(r => r.json())
            if (currentStatus.status === 'ready') {
              clearInterval(pollInterval)
              setMessages(prev => [...prev, {
                id: Date.now() + 2,
                text: `Perfect! I've processed ${currentStatus.total_chunks} pieces of content from your website. I'm ready to answer your questions!`,
                isBot: true,
                timestamp: new Date()
              }])
            }
          } catch (err) {
            console.error('Status check error:', err)
          }
        }, 5000)
      } else {
        throw new Error('Setup failed')
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "Sorry, there was an error setting up your website. Please check the URL and try again.",
        isBot: true,
        timestamp: new Date()
      }])
    }
    setIsLoading(false)
  }

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    // Check if it's a URL (simple setup)
    if (inputText.includes('http') && systemStatus?.status !== 'ready') {
      setWebsiteUrl(inputText.trim())
      setInputText('')
      await handleSetupWebsite()
      return
    }

    const userMessage: Message = {
      id: Date.now(),
      text: inputText.trim(),
      isBot: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = inputText.trim()
    setInputText('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: currentInput, max_results: 5 })
      })

      if (response.ok) {
        const data = await response.json()
        const botMessage: Message = {
          id: Date.now() + 1,
          text: data.answer,
          isBot: true,
          timestamp: new Date(),
          confidence: data.confidence,
          sources: data.sources || []
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        throw new Error('Query failed')
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: systemStatus?.status !== 'ready' 
          ? "I'm not ready yet. Please provide your website URL first, or wait for setup to complete."
          : "Sorry, I encountered an error. Please try again.",
        isBot: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
    setIsLoading(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getStatusBadge = () => {
    if (!systemStatus) return null

    const statusConfig = {
      ready: { 
        color: 'bg-green-100 text-green-800 border-green-200', 
        icon: <CheckIcon />,
        text: `Ready (${systemStatus.total_chunks} chunks)`
      },
      not_ready: { 
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200', 
        icon: <AlertIcon />,
        text: 'Not Ready'
      },
      error: { 
        color: 'bg-red-100 text-red-800 border-red-200', 
        icon: <AlertIcon />,
        text: 'Error'
      }
    }

    const config = statusConfig[systemStatus.status as keyof typeof statusConfig] || statusConfig.error

    return (
      <div className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
        {config.icon}
        {config.text}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto p-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">RAG Chatbot</h1>
          <div className="flex items-center gap-4">
            {getStatusBadge()}
            <button
              onClick={() => setShowSetup(!showSetup)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <SettingsIcon />
            </button>
          </div>
        </div>
      </div>

      {/* Setup Panel */}
      {showSetup && (
        <div className="bg-blue-50 border-b border-blue-200">
          <div className="max-w-4xl mx-auto p-4">
            <h3 className="text-lg font-medium text-blue-900 mb-3">Setup Website</h3>
            <div className="flex gap-3">
              <input
                type="url"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://your-website.com"
                className="flex-1 px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
              <button
                onClick={handleSetupWebsite}
                disabled={!websiteUrl.trim() || isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <GlobeIcon />
                Setup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
            >
              <div className={`max-w-2xl rounded-lg shadow-sm ${
                message.isBot
                  ? 'bg-white border border-gray-200 text-gray-900'
                  : 'bg-blue-600 text-white'
              }`}>
                <div className="p-4">
                  <div className="text-sm whitespace-pre-wrap">{message.text}</div>
                  
                  {/* Show sources if available */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      <div className="text-xs font-medium mb-1 opacity-70">Sources:</div>
                      <div className="space-y-1">
                        {message.sources.slice(0, 2).map((source, index) => (
                          <div key={index} className="text-xs opacity-70 flex items-center gap-1">
                            <ExternalIcon />
                            <a 
                              href={source.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="hover:underline"
                            >
                              {source.title} ({Math.round(source.relevance_score * 100)}%)
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Show confidence if available */}
                  {message.confidence !== undefined && (
                    <div className="text-xs mt-2 opacity-70">
                      Confidence: {Math.round(message.confidence * 100)}%
                    </div>
                  )}
                  
                  <div className="text-xs mt-2 opacity-60">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                <div className="p-4 flex items-center gap-3">
                  <LoaderIcon />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex gap-3">
            <input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                systemStatus?.status === 'ready' 
                  ? "Ask me anything about the website..."
                  : "Enter your website URL to get started, or ask a question..."
              }
              disabled={isLoading}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <SendIcon />
              Send
            </button>
          </div>
          
          <div className="mt-2 text-xs text-gray-500 text-center">
            {systemStatus?.status === 'ready' 
              ? `Ready to answer questions about your website content`
              : 'Tip: Paste your website URL to set up the knowledge base'
            }
          </div>
        </div>
      </div>
    </div>
  )
}