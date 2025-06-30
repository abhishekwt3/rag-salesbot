/* eslint-disable @typescript-eslint/no-unused-vars */
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Plus,
  Trash2,
  Copy,
  Check,
  ExternalLink,
  Send,
  MessageCircle,
  Activity,
  Bot,
  Code,
  Settings
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Widget {
  id: string
  name: string
  knowledge_base_id: string
  widget_key: string
  website_url?: string
  primary_color: string
  widget_position: string
  welcome_message: string
  placeholder_text: string
  widget_title: string
  is_active: boolean
  show_branding: boolean
  total_conversations: number
  total_messages: number
  last_used?: string
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

interface WidgetIntegrationProps {
  token: string
  knowledgeBases: KnowledgeBase[]
}

export default function WidgetIntegration({ token, knowledgeBases }: WidgetIntegrationProps) {
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateWidget, setShowCreateWidget] = useState(false)
  const [copiedText, setCopiedText] = useState("")
  const [widgetError, setWidgetError] = useState("")
  const [newWidget, setNewWidget] = useState({
    name: '',
    knowledge_base_id: '',
    website_url: '',
    primary_color: '#2563eb',
    widget_position: 'bottom-right',
    welcome_message: 'Hi! How can I help you today?',
    placeholder_text: 'Type your message...',
    widget_title: 'Chat Support',
    show_branding: true
  })

  useEffect(() => {
    if (token) {
      fetchWidgets()
    }
  }, [token])

  const fetchWidgets = async () => {
    if (!token) return
    
    try {
      const response = await fetch(`${API_BASE}/widgets`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setWidgets(data)
      } else {
        setWidgetError('Failed to fetch widgets')
      }
    } catch (error) {
      setWidgetError('Network error while fetching widgets')
    } finally {
      setLoading(false)
    }
  }

  const createWidget = async () => {
    setWidgetError('')
    try {
      const response = await fetch(`${API_BASE}/widgets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newWidget)
      })

      if (response.ok) {
        setShowCreateWidget(false)
        setNewWidget({
          name: '',
          knowledge_base_id: '',
          website_url: '',
          primary_color: '#2563eb',
          widget_position: 'bottom-right',
          welcome_message: 'Hi! How can I help you today?',
          placeholder_text: 'Type your message...',
          widget_title: 'Chat Support',
          show_branding: true
        })
        fetchWidgets()
      } else {
        const data = await response.json()
        setWidgetError(data.detail || 'Failed to create widget')
      }
    } catch (error) {
      setWidgetError('Network error while creating widget')
    }
  }

  const deleteWidget = async (widgetId: string) => {
    if (!confirm('Are you sure you want to delete this widget? This will break any existing embeds.')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/widgets/${widgetId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        fetchWidgets()
      } else {
        setWidgetError('Failed to delete widget')
      }
    } catch (error) {
      setWidgetError('Network error while deleting widget')
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(type)
      setTimeout(() => setCopiedText(''), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const getEmbedCode = (widget: Widget) => {
    return `<!-- AI Chatbot Widget -->
<script>
  (function() {
    var script = document.createElement('script');
    script.src = '${API_BASE}/widget/${widget.widget_key}/script.js';
    script.async = true;
    document.head.appendChild(script);
  })();
</script>`
  }

  const getKnowledgeBaseName = (kbId: string) => {
    const kb = knowledgeBases.find(kb => kb.id === kbId)
    return kb ? kb.name : 'Unknown'
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-dark-cyan mx-auto"></div>
              <p className="text-brand-midnight/60 mt-4">Loading widgets...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <Card className="bg-white border-0 shadow-md">
        <CardHeader className="pb-6">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold text-brand-black flex items-center gap-2">
                <Code className="h-6 w-6 text-brand-dark-cyan" />
                Widget Integration
              </CardTitle>
              <CardDescription className="text-base text-brand-midnight/60 mt-2">
                Manage your chat widgets and get embed codes for your website
              </CardDescription>
            </div>
            <Button
              onClick={() => setShowCreateWidget(true)}
              className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-4 py-2 text-sm font-medium flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Create Widget
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {widgets.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Bot className="h-10 w-10 text-brand-dark-cyan" />
              </div>
              <h3 className="text-xl font-semibold text-brand-black mb-3">No Widgets Yet</h3>
              <p className="text-base text-brand-midnight/60 mb-6 max-w-md mx-auto">
                Create your first chat widget to embed AI assistance on your website.
              </p>
              <Button
                onClick={() => setShowCreateWidget(true)}
                className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-6 py-2 text-sm font-medium"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Widget
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Active Widgets Grid */}
              <div className="grid gap-6">
                {widgets.map((widget) => (
                  <Card key={widget.id} className="border border-gray-200 hover:border-brand-dark-cyan/30 transition-colors">
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div 
                            className="w-12 h-12 rounded-lg flex items-center justify-center"
                            style={{ backgroundColor: `${widget.primary_color}15` }}
                          >
                            <Bot 
                              className="h-6 w-6" 
                              style={{ color: widget.primary_color }}
                            />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-brand-black">{widget.name}</h3>
                            <p className="text-sm text-brand-midnight/60 mt-1">
                              Knowledge Base: {getKnowledgeBaseName(widget.knowledge_base_id)}
                            </p>
                            {widget.website_url && (
                              <p className="text-sm text-brand-midnight/60">
                                Website: {widget.website_url}
                              </p>
                            )}
                            <div className="flex items-center gap-4 mt-2">
                              <div className="flex items-center gap-1 text-xs text-brand-midnight/60">
                                <MessageCircle className="h-3 w-3" />
                                {widget.total_conversations} conversations
                              </div>
                              <div className="flex items-center gap-1 text-xs text-brand-midnight/60">
                                <Activity className="h-3 w-3" />
                                {widget.total_messages} messages
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant={widget.is_active ? "default" : "secondary"}
                            className={widget.is_active ? 
                              "bg-green-100 text-green-700 hover:bg-green-200" : 
                              "bg-gray-100 text-gray-700"
                            }
                          >
                            {widget.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteWidget(widget.id)}
                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Tabs defaultValue="embed" className="w-full">
                        <TabsList className="grid w-full grid-cols-3 bg-gray-50">
                          <TabsTrigger 
                            value="embed"
                            className="data-[state=active]:bg-white data-[state=active]:text-brand-dark-cyan"
                          >
                            Embed Code
                          </TabsTrigger>
                          <TabsTrigger 
                            value="preview"
                            className="data-[state=active]:bg-white data-[state=active]:text-brand-dark-cyan"
                          >
                            Preview
                          </TabsTrigger>
                          <TabsTrigger 
                            value="settings"
                            className="data-[state=active]:bg-white data-[state=active]:text-brand-dark-cyan"
                          >
                            Settings
                          </TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="embed" className="space-y-4 mt-4">
                          <div className="space-y-3">
                            <div>
                              <label className="text-sm font-medium text-brand-black">Embed Code</label>
                              <div className="mt-2 relative">
                                <div className="bg-brand-black/95 p-4 rounded-xl font-mono text-sm overflow-x-auto">
                                  <div className="text-gray-400 mb-1">{"<!-- Add this to your website -->"}</div>
                                  <div className="text-blue-400">{"<script>"}</div>
                                  <div className="ml-3 text-green-400">{"(function() {"}</div>
                                  <div className="ml-6 text-green-400">var script = document.createElement('script');</div>
                                  <div className="ml-6 text-yellow-400">script.src = '{API_BASE}/widget/{widget.widget_key}/script.js';</div>
                                  <div className="ml-6 text-green-400">script.async = true;</div>
                                  <div className="ml-6 text-green-400">document.head.appendChild(script);</div>
                                  <div className="ml-3 text-green-400">{"})();"}</div>
                                  <div className="text-blue-400">{"</script>"}</div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="absolute top-2 right-2 bg-white/90 hover:bg-white"
                                  onClick={() => copyToClipboard(getEmbedCode(widget), `embed-${widget.id}`)}
                                >
                                  {copiedText === `embed-${widget.id}` ? (
                                    <Check className="h-3 w-3" />
                                  ) : (
                                    <Copy className="h-3 w-3" />
                                  )}
                                </Button>
                              </div>
                            </div>

                            <div>
                              <label className="text-sm font-medium text-brand-black">Widget Key</label>
                              <div className="mt-2 flex items-center gap-2">
                                <Input
                                  value={widget.widget_key}
                                  readOnly
                                  className="font-mono text-xs bg-gray-50 border-gray-200"
                                />
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => copyToClipboard(widget.widget_key, `key-${widget.id}`)}
                                >
                                  {copiedText === `key-${widget.id}` ? (
                                    <Check className="h-3 w-3" />
                                  ) : (
                                    <Copy className="h-3 w-3" />
                                  )}
                                </Button>
                              </div>
                            </div>

                            <div className="flex gap-2 pt-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(`${API_BASE}/widget/${widget.widget_key}/script.js`, '_blank')}
                                className="text-brand-dark-cyan border-brand-dark-cyan hover:bg-brand-dark-cyan hover:text-white"
                              >
                                <ExternalLink className="h-3 w-3 mr-1" />
                                Test Widget
                              </Button>
                            </div>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="preview" className="space-y-4 mt-4">
                          <div className="bg-gradient-to-br from-brand-dark-cyan/5 to-brand-cerulean/5 rounded-xl p-6">
                            <h4 className="text-sm font-medium text-brand-black mb-4">Widget Preview</h4>
                            <div className="flex justify-center">
                              <div className="bg-white rounded-xl border shadow-lg p-4 max-w-sm w-full">
                                <div className="flex items-center gap-2 mb-3">
                                  <Bot 
                                    className="h-5 w-5" 
                                    style={{ color: widget.primary_color }}
                                  />
                                  <span className="text-sm font-medium text-brand-black">{widget.widget_title}</span>
                                  <Badge className="ml-auto bg-green-100 text-green-700 text-xs px-2 py-0.5">
                                    {widget.widget_position}
                                  </Badge>
                                </div>
                                <div className="text-sm text-brand-midnight/80 bg-gray-50 rounded-lg p-3 mb-3">
                                  {widget.welcome_message}
                                </div>
                                <div className="flex items-center gap-2 p-2 border rounded-lg bg-gray-50">
                                  <Input
                                    placeholder={widget.placeholder_text}
                                    className="border-0 bg-transparent text-xs"
                                    disabled
                                  />
                                  <Button 
                                    size="sm" 
                                    className="px-2"
                                    style={{ backgroundColor: widget.primary_color }}
                                  >
                                    <Send className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="settings" className="space-y-4 mt-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-3">
                              <label className="text-sm font-medium text-brand-black">Widget Position</label>
                              <div className="p-3 border border-gray-200 rounded-lg bg-gray-50">
                                <span className="text-sm text-brand-midnight/80 capitalize">
                                  {widget.widget_position.replace('-', ' ')}
                                </span>
                              </div>
                            </div>
                            <div className="space-y-3">
                              <label className="text-sm font-medium text-brand-black">Theme Color</label>
                              <div className="flex items-center gap-3">
                                <div 
                                  className="w-8 h-8 rounded-lg border-2 shadow-sm"
                                  style={{ 
                                    backgroundColor: widget.primary_color,
                                    borderColor: widget.primary_color 
                                  }}
                                ></div>
                                <span className="text-sm text-brand-midnight/80 font-mono">
                                  {widget.primary_color}
                                </span>
                              </div>
                            </div>
                            <div className="space-y-3">
                              <label className="text-sm font-medium text-brand-black">Welcome Message</label>
                              <div className="p-3 border border-gray-200 rounded-lg bg-gray-50">
                                <span className="text-sm text-brand-midnight/80">
                                  "{widget.welcome_message}"
                                </span>
                              </div>
                            </div>
                            <div className="space-y-3">
                              <label className="text-sm font-medium text-brand-black">Placeholder Text</label>
                              <div className="p-3 border border-gray-200 rounded-lg bg-gray-50">
                                <span className="text-sm text-brand-midnight/80">
                                  "{widget.placeholder_text}"
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between p-4 bg-brand-dark-cyan/5 rounded-lg">
                            <div>
                              <h5 className="text-sm font-medium text-brand-black">Show Branding</h5>
                              <p className="text-xs text-brand-midnight/60">Display "Powered by" branding</p>
                            </div>
                            <Badge variant={widget.show_branding ? "default" : "secondary"}>
                              {widget.show_branding ? "Enabled" : "Disabled"}
                            </Badge>
                          </div>
                        </TabsContent>
                      </Tabs>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Widget Modal */}
      {showCreateWidget && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4 bg-white">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                <Plus className="h-5 w-5 text-brand-dark-cyan" />
                Create New Widget
              </CardTitle>
              <CardDescription>
                Configure your chat widget for website integration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-brand-black">Widget Name</label>
                  <Input
                    placeholder="e.g., Support Chat"
                    value={newWidget.name}
                    onChange={(e) => setNewWidget(prev => ({ ...prev, name: e.target.value }))}
                    className="border-gray-200 focus:border-brand-dark-cyan focus:ring-brand-dark-cyan/20"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-brand-black">Website URL</label>
                  <Input
                    placeholder="https://yourwebsite.com"
                    value={newWidget.website_url}
                    onChange={(e) => setNewWidget(prev => ({ ...prev, website_url: e.target.value }))}
                    className="border-gray-200 focus:border-brand-dark-cyan focus:ring-brand-dark-cyan/20"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-brand-black">Knowledge Base</label>
                <select 
                  className="w-full p-3 border border-gray-200 rounded-lg bg-white focus:border-brand-dark-cyan focus:ring-2 focus:ring-brand-dark-cyan/20 outline-none"
                  value={newWidget.knowledge_base_id}
                  onChange={(e) => setNewWidget(prev => ({ ...prev, knowledge_base_id: e.target.value }))}
                >
                  <option value="">Select a knowledge base</option>
                  {knowledgeBases.filter(kb => kb.status === 'ready').map(kb => (
                    <option key={kb.id} value={kb.id}>{kb.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-brand-black">Widget Position</label>
                  <select 
                    className="w-full p-3 border border-gray-200 rounded-lg bg-white focus:border-brand-dark-cyan focus:ring-2 focus:ring-brand-dark-cyan/20 outline-none"
                    value={newWidget.widget_position}
                    onChange={(e) => setNewWidget(prev => ({ ...prev, widget_position: e.target.value }))}
                  >
                    <option value="bottom-right">Bottom Right</option>
                    <option value="bottom-left">Bottom Left</option>
                    <option value="top-right">Top Right</option>
                    <option value="top-left">Top Left</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-brand-black">Theme Color</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={newWidget.primary_color}
                      onChange={(e) => setNewWidget(prev => ({ ...prev, primary_color: e.target.value }))}
                      className="w-12 h-12 rounded-lg border border-gray-200 cursor-pointer"
                    />
                    <Input
                      value={newWidget.primary_color}
                      onChange={(e) => setNewWidget(prev => ({ ...prev, primary_color: e.target.value }))}
                      className="flex-1 font-mono border-gray-200 focus:border-brand-dark-cyan focus:ring-brand-dark-cyan/20"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-brand-black">Welcome Message</label>
                <Input
                  placeholder="Hi! How can I help you today?"
                  value={newWidget.welcome_message}
                  onChange={(e) => setNewWidget(prev => ({ ...prev, welcome_message: e.target.value }))}
                  className="border-gray-200 focus:border-brand-dark-cyan focus:ring-brand-dark-cyan/20"
                />
              </div>

              {widgetError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700">{widgetError}</p>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button 
                  onClick={createWidget} 
                  disabled={!newWidget.name || !newWidget.knowledge_base_id}
                  className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-6 py-2"
                >
                  Create Widget
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowCreateWidget(false)}
                  className="border-gray-200 text-brand-midnight hover:bg-gray-50"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}