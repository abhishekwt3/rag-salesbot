/* eslint-disable @typescript-eslint/no-unused-vars */
'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { 
  Plus, 
  Globe, 
  Upload,
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Trash2,
  RefreshCw,
} from 'lucide-react'
import FileUpload from './FileUpload' // Import the FileUpload component

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.salesdok.com'

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
  const [showFileUploadModal, setShowFileUploadModal] = useState(false)
  const [selectedKBForContent, setSelectedKBForContent] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [processingKB, setProcessingKB] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false) // <- ADD this line


  const [newKBForm, setNewKBForm] = useState({
    name: '',
    description: ''
  })

  const [websiteForm, setWebsiteForm] = useState({
    url: '',
    max_pages: 10,
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
        setWebsiteForm({ url: '', max_pages: 10, single_page_mode: false })
        setShowWebsiteModal(false)
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

  const handleFileUploadComplete = () => {
    setShowFileUploadModal(false)
    setSelectedKBForContent('')
    onRefresh()
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">Ready</Badge>
      case 'processing':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800 border-yellow-200">Processing</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="secondary">Not Ready</Badge>
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
        return <Loader2 className="h-4 w-4 text-yellow-500 animate-spin" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  }

    // Handle manual refresh
  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await onRefresh()
    } finally {
      // Add a small delay to show the refresh animation
      setTimeout(() => {
        setRefreshing(false)
      }, 500)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Knowledge Bases</h2>
        <div className="flex items-center gap-2">
          <Button 
            size="sm" 
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-1"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>

        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-1" />
              New KB
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Knowledge Base</DialogTitle>
              <DialogDescription>
                Create a new knowledge base to organize your content and train your chatbot.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label className="pb-2" htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={newKBForm.name}
                  onChange={(e) => setNewKBForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Customer Support, Product Documentation"
                />
              </div>
              <div>
                <Label className="pb-2"htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={newKBForm.description}
                  onChange={(e) => setNewKBForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of what this knowledge base contains..."
                  rows={3}
                />
              </div>
              {error && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button onClick={createKnowledgeBase} disabled={loading || !newKBForm.name.trim()}>
                  {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Create
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Knowledge Bases List */}
      <div className={knowledgeBases.length === 0 ? "" : "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"}>
        {knowledgeBases.length === 0 ? (
          <div className="text-center py-8 text-gray-500 col-span-full">
            <div className="text-2xl mb-2">📚</div>
            <p className="text-sm">No knowledge bases yet.</p>
            <p className="text-xs">Create one to get started!</p>
          </div>
        ) : (
          knowledgeBases.map((kb) => (
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
                
                {/* Content Addition Options */}
                {(kb.status === 'not_ready' || kb.status === 'ready') && (
                  <div className="mt-3 pt-2 border-t">
                    <div className="flex gap-2">
                      {/* Website Processing */}
                      <Dialog open={showWebsiteModal} onOpenChange={setShowWebsiteModal}>
                        <DialogTrigger asChild>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="flex-1"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Globe className="h-3 w-3 mr-1" />
                            Add Webpage
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Process Webpage</DialogTitle>
                            <DialogDescription>
                              Enter a website URL to extract and process its content for this knowledge base.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label className="pb-2" htmlFor="url">Website URL</Label>
                              <Input
                                id="url"
                                type="url"
                                value={websiteForm.url}
                                onChange={(e) => setWebsiteForm(prev => ({ ...prev, url: e.target.value }))}
                                placeholder="https://example.com"
                              />
                            </div>
                            <div>
                              <Label className="pb-2" htmlFor="max_pages">Maximum Pages to Process</Label>
                              <Input
                                id="max_pages"
                                type="number"
                                value={websiteForm.max_pages}
                                onChange={(e) => setWebsiteForm(prev => ({ ...prev, max_pages: parseInt(e.target.value) || 10 }))}
                                min="1"
                                max="10"
                              />
                            </div>
                            <div className="flex justify-end gap-2">
                              <Button variant="outline" onClick={() => setShowWebsiteModal(false)}>
                                Cancel
                              </Button>
                              <Button 
                                onClick={() => processWebsite(kb.id)} 
                                disabled={!websiteForm.url.trim() || processingKB === kb.id}
                              >
                                {processingKB === kb.id ? (
                                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                ) : null}
                                Process Website
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>

                      {/* File Upload */}
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedKBForContent(kb.id)
                          setShowFileUploadModal(true)
                        }}
                      >
                        <Upload className="h-3 w-3 mr-1" />
                        Upload Files
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* File Upload Modal */}
      <FileUpload
        knowledgeBaseId={selectedKBForContent}
        token={token}
        onUploadComplete={handleFileUploadComplete}
        isOpen={showFileUploadModal}
        onOpenChange={setShowFileUploadModal}
      />

      {error && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}