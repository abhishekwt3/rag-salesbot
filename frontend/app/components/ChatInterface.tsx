'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from "@/app/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card"
import { Input } from "@/app/components/ui/input"
//import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/app/components/ui/badge"
import { ScrollArea } from "@/app/components/ui/scroll-area"
import { Separator } from "@/app/components/ui/separator"
import { 
  Send, 
  Bot, 
  User, 
  ExternalLink, 
  Loader2,
  MessageCircle,
  Copy,
  Check
} from 'lucide-react'

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
  loading?: boolean
}

interface ChatInterfaceProps {
  knowledgeBaseId: string
  knowledgeBaseName: string
  token: string
}

export default function ChatInterface({ 
  knowledgeBaseId, 
  knowledgeBaseName, 
  token 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: `Hello! I'm your AI assistant for ${knowledgeBaseName}. I can answer questions based on the content in this knowledge base. What would you like to know?`,
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputText.trim() || loading) return

    const userMessage: Message = {
      id: Date.now(),
      text: inputText.trim(),
      isBot: false,
      timestamp: new Date()
    }

    const loadingMessage: Message = {
      id: Date.now() + 1,
      text: "Thinking...",
      isBot: true,
      timestamp: new Date(),
      loading: true
    }

    setMessages(prev => [...prev, userMessage, loadingMessage])
    setInputText('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question: userMessage.text,
          knowledge_base_id: knowledgeBaseId,
          max_results: 5
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const botResponse: Message = {
          id: Date.now() + 2,
          text: data.answer,
          isBot: true,
          timestamp: new Date(),
          confidence: data.confidence,
          sources: data.sources
        }

        setMessages(prev => prev.slice(0, -1).concat([botResponse]))
      } else {
        const errorData = await response.json()
        const errorMessage: Message = {
          id: Date.now() + 2,
          text: `Sorry, I encountered an error: ${errorData.detail || 'Unable to process your question'}`,
          isBot: true,
          timestamp: new Date()
        }
        setMessages(prev => prev.slice(0, -1).concat([errorMessage]))
      }
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 2,
        text: "Sorry, I'm having trouble connecting. Please try again.",
        isBot: true,
        timestamp: new Date()
      }
      setMessages(prev => prev.slice(0, -1).concat([errorMessage]))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyToClipboard = async (text: string, messageId: number) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(messageId)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (error) {
      console.error('Failed to copy text:', error)
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-full">
              <MessageCircle className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-lg">Chat with {knowledgeBaseName}</CardTitle>
              <p className="text-sm text-gray-500 mt-1">
                AI assistant powered by your knowledge base
              </p>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <ScrollArea className="flex-1 px-6">
          <div className="space-y-4 pb-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.isBot ? 'justify-start' : 'justify-end'}`}
              >
                {message.isBot && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                )}
                
                <div className={`max-w-[80%] ${message.isBot ? 'order-2' : 'order-1'}`}>
                  <div
                    className={`rounded-lg px-4 py-3 ${
                      message.isBot
                        ? 'bg-gray-100 text-gray-900'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    {message.loading ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Processing your question...</span>
                      </div>
                    ) : (
                      <div className="text-sm whitespace-pre-wrap">
                        {message.text}
                      </div>
                    )}
                    
                    {/* Bot message actions */}
                    {message.isBot && !message.loading && (
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-200">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">
                            {formatTime(message.timestamp)}
                          </span>
                          {message.confidence && (
                            <Badge 
                              variant="secondary" 
                              className={`text-xs ${getConfidenceColor(message.confidence)}`}
                            >
                              {Math.round(message.confidence * 100)}% confidence
                            </Badge>
                          )}
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(message.text, message.id)}
                          className="h-6 px-2"
                        >
                          {copiedId === message.id ? (
                            <Check className="w-3 h-3" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    )}
                  </div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-gray-500 font-medium">Sources:</p>
                      {message.sources.slice(0, 3).map((source, index) => (
                        <div 
                          key={index}
                          className="text-xs bg-white border rounded p-2 flex items-center justify-between"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{source.title}</p>
                            <p className="text-gray-500 truncate">{source.url}</p>
                          </div>
                          <div className="flex items-center gap-2 ml-2">
                            <Badge variant="outline" className="text-xs">
                              {Math.round(source.relevance_score * 100)}%
                            </Badge>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(source.url, '_blank')}
                              className="h-6 w-6 p-0"
                            >
                              <ExternalLink className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* User message timestamp */}
                  {!message.isBot && (
                    <p className="text-xs text-gray-400 mt-1 text-right">
                      {formatTime(message.timestamp)}
                    </p>
                  )}
                </div>
                
                {!message.isBot && (
                  <div className="flex-shrink-0 order-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        
        <Separator />
        
        {/* Input */}
        <div className="p-4">
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question about your knowledge base..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              className="flex-1"
            />
            <Button 
              onClick={sendMessage}
              disabled={loading || !inputText.trim()}
              size="sm"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </CardContent>
    </Card>
  )
}