/* eslint-disable @typescript-eslint/no-unused-vars */
'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Plus, 
  Settings, 
  Code, 
  ExternalLink, 
  Copy,
  Trash2,
  Eye,
  MessageCircle,
  BarChart3,
  Check,
  Globe
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
  status: string
}

interface WidgetManagerProps {
  knowledgeBases: KnowledgeBase[]
  token: string
  onRefresh: () => void
}

export default function WidgetManager({ knowledgeBases, token, onRefresh }: WidgetManagerProps) {
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedWidget, setSelectedWidget] = useState<Widget | null>(null)
  const [copiedText, setCopiedText] = useState('')

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
    fetchWidgets()
  }, [token])

  const fetchWidgets = async () => {
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
        setError('Failed to fetch widgets')
      }
    } catch (error) {
      setError('Network error while fetching widgets')
    } finally {
      setLoading(false)
    }
  }

  const createWidget = async () => {
    setError('')
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
        setShowCreateModal(false)
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
        setError(data.detail || 'Failed to create widget')
      }
    } catch (error) {
      setError('Network error while creating widget')
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
        setError('Failed to delete widget')
      }
    } catch (error) {
      setError('Network error while deleting widget')
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

  const getTestURL = (widget: Widget) => {
    return `${API_BASE}/widget/${widget.widget_key}/script.js`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getKnowledgeBaseName = (kbId: string) => {
    const kb = knowledgeBases.find(kb => kb.id === kbId)
    return kb ? kb.name : 'Unknown'
  }

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Chat Widgets</h2>
          <p className="text-gray-600">Embed AI chatbots on your websites</p>
        </div>
        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Widget
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create Chat Widget</DialogTitle>
              <DialogDescription>
                Create a new embeddable chat widget for your website.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="widget-name">Widget Name</Label>
                <Input
                  id="widget-name"
                  placeholder="e.g., Support Chat, Help Widget"
                  value={newWidget.name}
                  onChange={(e) => setNewWidget(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="knowledge-base">Knowledge Base</Label>
                <Select 
                  value={newWidget.knowledge_base_id} 
                  onValueChange={(value) => setNewWidget(prev => ({ ...prev, knowledge_base_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select knowledge base" />
                  </SelectTrigger>
                  <SelectContent>
                    {knowledgeBases
                      .filter(kb => kb.status === 'ready')
                      .map(kb => (
                        <SelectItem key={kb.id} value={kb.id}>
                          {kb.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="website-url">Website URL (Optional)</Label>
                <Input
                  id="website-url"
                  placeholder="https://yourwebsite.com"
                  value={newWidget.website_url}
                  onChange={(e) => setNewWidget(prev => ({ ...prev, website_url: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="primary-color">Primary Color</Label>
                  <Input
                    id="primary-color"
                    type="color"
                    value={newWidget.primary_color}
                    onChange={(e) => setNewWidget(prev => ({ ...prev, primary_color: e.target.value }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="position">Position</Label>
                  <Select 
                    value={newWidget.widget_position} 
                    onValueChange={(value) => setNewWidget(prev => ({ ...prev, widget_position: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bottom-right">Bottom Right</SelectItem>
                      <SelectItem value="bottom-left">Bottom Left</SelectItem>
                      <SelectItem value="top-right">Top Right</SelectItem>
                      <SelectItem value="top-left">Top Left</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="welcome-message">Welcome Message</Label>
                <Textarea
                  id="welcome-message"
                  placeholder="Hi! How can I help you today?"
                  value={newWidget.welcome_message}
                  onChange={(e) => setNewWidget(prev => ({ ...prev, welcome_message: e.target.value }))}
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-3">
                <Button onClick={createWidget} disabled={!newWidget.name || !newWidget.knowledge_base_id}>
                  Create Widget
                </Button>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {widgets.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No widgets yet</h3>
            <p className="text-gray-500 mb-4">Create your first chat widget to embed on your website.</p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Widget
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {widgets.map((widget) => (
            <Card key={widget.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{widget.name}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      Knowledge Base: {getKnowledgeBaseName(widget.knowledge_base_id)}
                    </p>
                    {widget.website_url && (
                      <p className="text-sm text-gray-500">
                        Website: {widget.website_url}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className={getStatusColor(widget.is_active)}>
                      {widget.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteWidget(widget.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="embed" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="embed">Embed Code</TabsTrigger>
                    <TabsTrigger value="preview">Preview</TabsTrigger>
                    <TabsTrigger value="analytics">Analytics</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="embed" className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <Label className="text-sm font-medium">Embed Code</Label>
                        <div className="mt-1 relative">
                          <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                            {getEmbedCode(widget)}
                          </pre>
                          <Button
                            size="sm"
                            variant="outline"
                            className="absolute top-2 right-2"
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
                        <Label className="text-sm font-medium">Widget Key</Label>
                        <div className="mt-1 flex items-center gap-2">
                          <Input
                            value={widget.widget_key}
                            readOnly
                            className="font-mono text-xs"
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

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(getTestURL(widget), '_blank')}
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Test Widget
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSelectedWidget(widget)}
                        >
                          <Settings className="h-3 w-3 mr-1" />
                          Configure
                        </Button>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="preview" className="space-y-4">
                    <div className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-center gap-3 mb-3">
                        <div 
                          className="w-6 h-6 rounded-full"
                          style={{ backgroundColor: widget.primary_color }}
                        ></div>
                        <div>
                          <p className="font-medium text-sm">{widget.widget_title}</p>
                          <p className="text-xs text-gray-500">Position: {widget.widget_position}</p>
                        </div>
                      </div>
                      <div className="bg-white border rounded p-3 text-sm">
                        {widget.welcome_message}
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Placeholder: {widget.placeholder_text}
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="analytics" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="flex items-center gap-2">
                          <MessageCircle className="h-5 w-5 text-blue-600" />
                          <span className="text-sm font-medium">Total Messages</span>
                        </div>
                        <p className="text-2xl font-bold text-blue-600 mt-1">
                          {widget.total_messages}
                        </p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="flex items-center gap-2">
                          <BarChart3 className="h-5 w-5 text-green-600" />
                          <span className="text-sm font-medium">Conversations</span>
                        </div>
                        <p className="text-2xl font-bold text-green-600 mt-1">
                          {widget.total_conversations}
                        </p>
                      </div>
                    </div>
                    {widget.last_used && (
                      <p className="text-sm text-gray-500">
                        Last used: {formatDate(widget.last_used)}
                      </p>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}