/* eslint-disable @typescript-eslint/no-unused-vars */
'use client'

import { useState } from 'react'
import { Button } from "@/app/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card"
import { Input } from "@/app/components/ui/input"
import { Label } from "@/app/components/ui/label"
import { Textarea } from "@/app/components/ui/textarea"
import { Alert, AlertDescription } from "@/app/components/ui/alert"
import { Badge } from "@/app/components/ui/badge"
import { Separator } from "@/app/components/ui/separator"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/app/components/ui/dialog"
import { 
  Plus, 
  Globe, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Trash2,
  RefreshCw
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface KnowledgeBase {
  id: string
  name: string
  description?: string
  status: 'not_ready' | 'processing' | 'ready' | 'error'
  total_chunks: number
  last_updated?: string
  created_at: string
}

interface KnowledgeBaseManagerProps {
  knowledgeBases: KnowledgeBase[]
  selectedKB: string | null
  onSelectKB: (id: string) => void
  onRefresh: () => void
  token: string
}

export default function KnowledgeBaseManager({
  knowledgeBases,
  selectedKB,
  onSelectKB,
  onRefresh,
  token
}: KnowledgeBaseManagerProps) {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showWebsiteModal, setShowWebsiteModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [processingKB, setProcessingKB] = useState<string | null>(null)

  const [newKBForm, setNewKBForm] = useState({
    name: '',
    description: ''
  })

  const [websiteForm, setWebsiteForm] = useState({
    url: '',
    max_pages: 50,
    single_page_mode: false
  })

  const createKnowledgeBase = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newKBForm)
      })

      if (response.ok) {
        setNewKBForm({ name: '', description: '' })
        setShowCreateModal(false)
        onRefresh()
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to create knowledge base')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const processWebsite = async (kbId: string) => {
    setProcessingKB(kbId)
    setError('')

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${kbId}/process-website`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          url: websiteForm.url,
          max_pages: websiteForm.max_pages,
          single_page_mode: websiteForm.single_page_mode,
          include_patterns: [],
          exclude_patterns: ["/blog", "/news"]
        })
      })

      if (response.ok) {
        setWebsiteForm({ url: '', max_pages: 50, single_page_mode: false })
        setShowWebsiteModal(false)
        // Refresh to get updated status
        setTimeout(() => {
          onRefresh()
        }, 1000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to process website')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setProcessingKB(null)
    }
  }

  const deleteKnowledgeBase = async (kbId: string) => {
    if (!confirm('Are you sure you want to delete this knowledge base? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${kbId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        onRefresh()
        if (selectedKB === kbId) {
          onSelectKB('')
        }
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to delete knowledge base')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Ready</Badge>
      case 'processing':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800"><Clock className="w-3 h-3 mr-1" />Processing</Badge>
      case 'error':
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Error</Badge>
      default:
        return <Badge variant="outline">Not Ready</Badge>
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Knowledge Bases</CardTitle>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Knowledge Base</DialogTitle>
                    <DialogDescription>
                      Create a new knowledge base to organize your chatbot&apos;s information.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="kb-name">Name</Label>
                      <Input
                        id="kb-name"
                        placeholder="e.g., Company FAQ, Product Docs"
                        value={newKBForm.name}
                        onChange={(e) => setNewKBForm(prev => ({ ...prev, name: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="kb-desc">Description (Optional)</Label>
                      <Textarea
                        id="kb-desc"
                        placeholder="Brief description of this knowledge base"
                        value={newKBForm.description}
                        onChange={(e) => setNewKBForm(prev => ({ ...prev, description: e.target.value }))}
                      />
                    </div>
                    
                    {error && (
                      <Alert variant="destructive">
                        <AlertDescription>{error}</AlertDescription>
                      </Alert>
                    )}
                    
                    <div className="flex gap-3">
                      <Button onClick={createKnowledgeBase} disabled={loading || !newKBForm.name}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Create
                      </Button>
                      <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {knowledgeBases.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-2xl mb-2">📚</div>
              <p className="text-sm">No knowledge bases yet.</p>
              <p className="text-xs">Create one to get started!</p>
            </div>
          ) : (
            knowledgeBases.map((kb, index) => (
              <div key={kb.id}>
                <div 
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedKB === kb.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                  onClick={() => onSelectKB(kb.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm">{kb.name}</h3>
                    <div className="flex items-center gap-1">
                      {getStatusBadge(kb.status)}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteKnowledgeBase(kb.id)
                        }}
                        className="h-6 w-6 p-0 hover:bg-red-100 hover:text-red-600"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  
                  {kb.description && (
                    <p className="text-xs text-gray-600 mb-2">{kb.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{kb.total_chunks} chunks</span>
                    <span>Created {formatDate(kb.created_at)}</span>
                  </div>
                  
                  {kb.status === 'not_ready' && (
                    <div className="mt-2 pt-2 border-t">
                      <Dialog open={showWebsiteModal} onOpenChange={setShowWebsiteModal}>
                        <DialogTrigger asChild>
                          <Button size="sm" variant="outline" className="w-full">
                            <Globe className="h-3 w-3 mr-1" />
                            Add Website Content
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Process Website</DialogTitle>
                            <DialogDescription>
                              Enter a website URL to extract and process its content for this knowledge base.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label htmlFor="website-url">Website URL</Label>
                              <Input
                                id="website-url"
                                placeholder="https://example.com"
                                value={websiteForm.url}
                                onChange={(e) => setWebsiteForm(prev => ({ ...prev, url: e.target.value }))}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="max-pages">Max Pages to Process</Label>
                              <Input
                                id="max-pages"
                                type="number"
                                min="1"
                                max="200"
                                value={websiteForm.max_pages}
                                onChange={(e) => setWebsiteForm(prev => ({ ...prev, max_pages: parseInt(e.target.value) || 50 }))}
                              />
                            </div>
                            
                            {error && (
                              <Alert variant="destructive">
                                <AlertDescription>{error}</AlertDescription>
                              </Alert>
                            )}
                            
                            <div className="flex gap-3">
                              <Button 
                                onClick={() => processWebsite(kb.id)} 
                                disabled={processingKB === kb.id || !websiteForm.url}
                              >
                                {processingKB === kb.id && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Process Website
                              </Button>
                              <Button variant="outline" onClick={() => setShowWebsiteModal(false)}>
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  )}
                </div>
                {index < knowledgeBases.length - 1 && <Separator className="my-3" />}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}