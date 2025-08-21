// components/KnowledgeBaseManager.tsx - Updated with subscription limits
'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
  Crown,
  AlertTriangle,
  Database,
} from 'lucide-react'
import FileUpload from './FileUpload'
import { UsageWarning } from './UsageLimits'

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

interface Usage {
  current_chunk_usage: number
  max_total_chunks: number
  remaining_chunks: number
  current_kb_count: number
  max_knowledge_bases: number
  can_create_kb: boolean
  plan: string
  status: string
}

interface KnowledgeBaseManagerProps {
  knowledgeBases: KnowledgeBase[]
  selectedKB: string | null
  onSelectKB: (id: string) => void
  onRefresh: () => void
  token: string
  usage?: Usage
  onUpgrade?: () => void
}

export default function KnowledgeBaseManager({
  knowledgeBases,
  selectedKB,
  onSelectKB,
  onRefresh,
  token,
  usage,
  onUpgrade
}: KnowledgeBaseManagerProps) {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showWebsiteModal, setShowWebsiteModal] = useState(false)
  const [showFileUploadModal, setShowFileUploadModal] = useState(false)
  const [selectedKBForContent, setSelectedKBForContent] = useState<string>('')
  const [selectedKBForWebsite, setSelectedKBForWebsite] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [processingKB, setProcessingKB] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [validationLoading, setValidationLoading] = useState(false)

  const [newKBForm, setNewKBForm] = useState({
    name: '',
    description: ''
  })

  const [websiteForm, setWebsiteForm] = useState({
    url: '',
    max_pages: 10,
    single_page_mode: false
  })

  // Validate if user can create KB
  const validateKBCreation = async () => {
    if (!usage) return true
    
    if (!usage.can_create_kb) {
      setError(`Knowledge base limit reached (${usage.current_kb_count}/${usage.max_knowledge_bases}). Upgrade your plan to create more knowledge bases.`)
      return false
    }
    
    return true
  }

  // Validate chunk usage for website processing
  const validateChunkUsage = async (estimatedChunks: number) => {
    setValidationLoading(true)
    try {
      const response = await fetch(`${API_BASE}/subscription/validate/chunks/${estimatedChunks}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const validation = await response.json()
        if (!validation.can_add) {
          setError(validation.message + ' Consider upgrading your plan.')
          return false
        }
        return true
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to validate chunk usage')
        return false
      }
    } catch {
      setError('Network error during validation')
      return false
    } finally {
      setValidationLoading(false)
    }
  }

  const createKnowledgeBase = async () => {
    setLoading(true)
    setError('')

    // Validate KB creation limits
    if (!(await validateKBCreation())) {
      setLoading(false)
      return
    }

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
    } catch {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const processWebsite = async () => {
    if (!selectedKBForWebsite) {
      setError('Please select a knowledge base')
      return
    }

    setLoading(true)
    setError('')
    setProcessingKB(selectedKBForWebsite)

    // Estimate chunks (rough estimate: 1 page ≈ 8 chunks)
    const estimatedChunks = websiteForm.max_pages * 8
    
    // Validate chunk usage
    if (!(await validateChunkUsage(estimatedChunks))) {
      setLoading(false)
      setProcessingKB(null)
      return
    }

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${selectedKBForWebsite}/process-website`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(websiteForm)
      })

      if (response.ok) {
        setWebsiteForm({ url: '', max_pages: 10, single_page_mode: false })
        setSelectedKBForWebsite('')
        setShowWebsiteModal(false)
        onRefresh()
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to process website')
        setProcessingKB(null)
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setError('Network error. Please try again.')
      setProcessingKB(null)
    } finally {
      setLoading(false)
    }
  }

  const deleteKnowledgeBase = async (id: string) => {
    if (!confirm('Are you sure you want to delete this knowledge base? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        onRefresh()
        if (selectedKB === id) {
          onSelectKB('')
        }
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to delete knowledge base')
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setError('Network error. Please try again.')
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await onRefresh()
    setRefreshing(false)
  }

  // const getStatusColor = (status: string) => {
  //   switch (status) {
  //     case 'ready': return 'bg-green-500'
  //     case 'processing': return 'bg-yellow-500'
  //     case 'error': return 'bg-red-500'
  //     default: return 'bg-gray-400'
  //   }
  // }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing': return <Clock className="h-4 w-4 text-yellow-500" />
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Database className="h-4 w-4 text-gray-400" />
    }
  }

  const canCreateKB = usage ? usage.can_create_kb : true
  const showUsageWarning = usage && (
    usage.remaining_chunks < 50 || 
    !usage.can_create_kb ||
    (usage.current_chunk_usage / usage.max_total_chunks) > 0.8
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-brand-black">Knowledge Bases</h2>
          <p className="text-brand-midnight/70">Manage your AI training data and content</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
          </Button>
          
          {canCreateKB ? (
            <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
              <DialogTrigger asChild>
                <Button className="bg-brand-dark-cyan hover:bg-brand-midnight text-white">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Knowledge Base
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Knowledge Base</DialogTitle>
                  <DialogDescription>
                    Create a new knowledge base to organize your content.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={newKBForm.name}
                      onChange={(e) => setNewKBForm(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Product Documentation"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description (Optional)</Label>
                    <Textarea
                      id="description"
                      value={newKBForm.description}
                      onChange={(e) => setNewKBForm(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Brief description of this knowledge base"
                      rows={3}
                    />
                  </div>
                  {error && (
                    <Alert className="border-red-200 bg-red-50">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  <div className="flex justify-end gap-3">
                    <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                      Cancel
                    </Button>
                    <Button 
                      onClick={createKnowledgeBase}
                      disabled={!newKBForm.name || loading}
                      className="bg-brand-dark-cyan hover:bg-brand-midnight text-white"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Creating...
                        </>
                      ) : (
                        'Create Knowledge Base'
                      )}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          ) : (
            <Button 
              variant="outline"
              onClick={onUpgrade}
              className="border-orange-300 text-orange-600 hover:bg-orange-50"
            >
              <Crown className="h-4 w-4 mr-2" />
              Upgrade to Create More
            </Button>
          )}
        </div>
      </div>

      {/* Usage Warning */}
      {usage && showUsageWarning && (
        <UsageWarning usage={usage} onUpgrade={onUpgrade} />
      )}

      {/* Knowledge Bases Grid */}
      {knowledgeBases.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {knowledgeBases.map((kb) => (
            <Card
              key={kb.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedKB === kb.id ? 'ring-2 ring-brand-dark-cyan border-brand-dark-cyan' : ''
              } ${processingKB === kb.id ? 'opacity-75' : ''}`}
              onClick={() => onSelectKB(kb.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(kb.status)}
                    <Badge variant="outline" className="text-xs">
                      {kb.status}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-red-500 hover:bg-red-50 hover:text-red-700"
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteKnowledgeBase(kb.id)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <CardTitle className="text-lg truncate">{kb.name}</CardTitle>
                {kb.description && (
                  <p className="text-sm text-brand-midnight/70 line-clamp-2">
                    {kb.description}
                  </p>
                )}
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-brand-midnight/70">Data Chunks</span>
                    <span className="font-medium">{kb.total_chunks.toLocaleString()}</span>
                  </div>
                  
                  {kb.last_updated && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-brand-midnight/70">Last Updated</span>
                      <span className="font-medium">
                        {new Date(kb.last_updated).toLocaleDateString()}
                      </span>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    <Dialog open={showWebsiteModal && selectedKBForWebsite === kb.id} 
                            onOpenChange={(open) => {
                              setShowWebsiteModal(open)
                              if (open) setSelectedKBForWebsite(kb.id)
                              else setSelectedKBForWebsite('')
                            }}>
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 text-xs"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Globe className="h-3 w-3 mr-1" />
                          Website
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Add Website Content</DialogTitle>
                          <DialogDescription>
                            Extract content from a website to add to {kb.name}
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="url">Website URL</Label>
                            <Input
                              id="url"
                              type="url"
                              value={websiteForm.url}
                              onChange={(e) => setWebsiteForm(prev => ({ ...prev, url: e.target.value }))}
                              placeholder="https://example.com"
                            />
                          </div>
                          <div>
                            <Label htmlFor="max_pages">Maximum Pages to Process</Label>
                            <Input
                              id="max_pages"
                              type="number"
                              min="1"
                              max="50"
                              value={websiteForm.max_pages}
                              onChange={(e) => setWebsiteForm(prev => ({ ...prev, max_pages: parseInt(e.target.value) || 10 }))}
                            />
                            <p className="text-xs text-brand-midnight/60 mt-1">
                              Estimated chunks: ~{websiteForm.max_pages * 8} 
                              {usage && usage.max_total_chunks !== -1 && (
                                <span className="ml-1">
                                  (You have {usage.remaining_chunks} remaining)
                                </span>
                              )}
                            </p>
                          </div>
                          {error && (
                            <Alert className="border-red-200 bg-red-50">
                              <AlertTriangle className="h-4 w-4" />
                              <AlertDescription>{error}</AlertDescription>
                            </Alert>
                          )}
                          <div className="flex justify-end gap-3">
                            <Button 
                              variant="outline" 
                              onClick={() => {
                                setShowWebsiteModal(false)
                                setSelectedKBForWebsite('')
                              }}
                            >
                              Cancel
                            </Button>
                            <Button 
                              onClick={processWebsite}
                              disabled={!websiteForm.url || loading || validationLoading}
                              className="bg-brand-dark-cyan hover:bg-brand-midnight text-white"
                            >
                              {loading || validationLoading ? (
                                <>
                                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  {validationLoading ? 'Validating...' : 'Processing...'}
                                </>
                              ) : (
                                'Process Website'
                              )}
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Dialog open={showFileUploadModal && selectedKBForContent === kb.id} 
                            onOpenChange={(open) => {
                              setShowFileUploadModal(open)
                              if (open) setSelectedKBForContent(kb.id)
                              else setSelectedKBForContent('')
                            }}>
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 text-xs"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Upload className="h-3 w-3 mr-1" />
                          Files
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Upload Documents</DialogTitle>
                          <DialogDescription>
                            Upload documents to add to {kb.name}
                          </DialogDescription>
                        </DialogHeader>
                        <FileUpload
                          knowledgeBaseId={kb.id}
                          token={token}
                          onUploadComplete={() => {
                            setShowFileUploadModal(false)
                            setSelectedKBForContent('')
                            onRefresh()
                          }}
                          usage={usage}
                          onUpgrade={onUpgrade}
                        />
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-12 pb-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Database className="h-8 w-8 text-brand-dark-cyan" />
              </div>
              <h3 className="text-lg font-semibold text-brand-black mb-2">No Knowledge Bases Yet</h3>
              <p className="text-brand-midnight/60 mb-6 max-w-md mx-auto">
                Knowledge bases help organize your content. Create your first one to start building your AI assistant.
              </p>
              
              {canCreateKB ? (
                <Button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-brand-dark-cyan hover:bg-brand-midnight text-white"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Knowledge Base
                </Button>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-orange-600">
                    You&apos;ve reached your knowledge base limit ({usage?.current_kb_count}/{usage?.max_knowledge_bases})
                  </p>
                  <Button
                    onClick={onUpgrade}
                    className="bg-brand-cerulean hover:bg-brand-midnight text-white"
                  >
                    <Crown className="h-4 w-4 mr-2" />
                    Upgrade to Create More
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Processing Status */}
      {processingKB && (
        <Alert className="border-blue-200 bg-blue-50">
          <Loader2 className="h-4 w-4 animate-spin" />
          <AlertDescription>
            <strong>Processing Content:</strong> Your content is being processed. This may take a few minutes.
            You can continue using the dashboard while processing happens in the background.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}