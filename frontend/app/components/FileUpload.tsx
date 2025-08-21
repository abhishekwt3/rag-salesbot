// components/FileUpload.tsx - Updated with subscription limits
'use client'

import { useState, useCallback } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  Upload,
  File,
  X,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileText,
  Crown,
  Database,
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

interface FileUploadProps {
  knowledgeBaseId: string
  token: string
  onUploadComplete: () => void
  usage?: Usage
  onUpgrade?: () => void
}

interface UploadedFile {
  file: File
  id: string
  status: 'pending' | 'uploading' | 'completed' | 'error'
  progress: number
  error?: string
  estimatedChunks?: number
}

export default function FileUpload({ 
  knowledgeBaseId, 
  token, 
  onUploadComplete,
  usage,
  onUpgrade 
}: FileUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  interface UploadResult {
    files_processed?: number
    // add other properties if needed
  }
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null)

  const allowedTypes = ['.txt', '.docx', '.doc']
  const maxFileSize = 10 * 1024 * 1024 // 10MB
  const maxFiles = 5

  // Estimate chunks for a file (rough estimate: 1KB ≈ 0.5 chunks)
  const estimateChunks = (file: File): number => {
    const sizeKB = file.size / 1024
    return Math.ceil(sizeKB * 0.5)
  }

  // Validate file against subscription limits
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedTypes.includes(extension)) {
      return { valid: false, error: `File type ${extension} not supported. Allowed: ${allowedTypes.join(', ')}` }
    }

    // Check file size
    if (file.size > maxFileSize) {
      return { valid: false, error: `File size exceeds 10MB limit` }
    }

    // Check chunk limits if usage data is available
    if (usage && usage.max_total_chunks !== -1) {
      const estimatedChunks = estimateChunks(file)
      if (estimatedChunks > usage.remaining_chunks) {
        return { 
          valid: false, 
          error: `File would use ~${estimatedChunks} chunks but you only have ${usage.remaining_chunks} remaining. Upgrade your plan or remove some content.`
        }
      }
    }

    return { valid: true }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    addFiles(selectedFiles)
    e.target.value = '' // Reset input
  }

  const addFiles = (newFiles: File[]) => {
    setError('')

    if (files.length + newFiles.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`)
      return
    }

    const validFiles: UploadedFile[] = []
    let totalEstimatedChunks = 0

    for (const file of newFiles) {
      const validation = validateFile(file)
      
      if (!validation.valid) {
        setError(validation.error || 'Invalid file')
        continue
      }

      const estimatedChunks = estimateChunks(file)
      totalEstimatedChunks += estimatedChunks

      validFiles.push({
        file,
        id: Math.random().toString(36).substr(2, 9),
        status: 'pending',
        progress: 0,
        estimatedChunks
      })
    }

    // Final check for total chunks
    if (usage && usage.max_total_chunks !== -1) {
      const currentTotalEstimate = files.reduce((sum, f) => sum + (f.estimatedChunks || 0), 0)
      if (currentTotalEstimate + totalEstimatedChunks > usage.remaining_chunks) {
        setError(`Total estimated chunks (${currentTotalEstimate + totalEstimatedChunks}) would exceed your remaining limit (${usage.remaining_chunks})`)
        return
      }
    }

    setFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  const uploadFiles = async () => {
    if (files.length === 0) return

    setUploading(true)
    setError('')
    setUploadResult(null)

    try {
      const formData = new FormData()
      files.forEach(({ file }) => {
        formData.append('files', file)
      })

      // Update file statuses to uploading
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const, progress: 0 })))

      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/upload-documents`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setUploadResult(result)
        
        // Update files to completed
        setFiles(prev => prev.map(f => ({ ...f, status: 'completed' as const, progress: 100 })))
        
        // Poll for processing status
        pollProcessingStatus()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Upload failed')
        
        // Update files to error
        setFiles(prev => prev.map(f => ({ ...f, status: 'error' as const, error: errorData.detail })))
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setError('Network error during upload')
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' as const, error: 'Network error' })))
    } finally {
      setUploading(false)
    }
  }

  const pollProcessingStatus = async () => {
    const maxAttempts = 30
    let attempts = 0

    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/processing-status`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const status = await response.json()
          
          if (status.status === 'ready') {
            onUploadComplete()
            return
          } else if (status.status === 'error') {
            setError('Processing failed. Please try again.')
            return
          }
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 2000) // Check every 2 seconds
        } else {
          setError('Processing is taking longer than expected. Please check back later.')
        }
      } catch (error) {
        console.error('Error checking status:', error)
      }
    }

    checkStatus()
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    if (extension === 'txt') return <FileText className="h-5 w-5 text-blue-500" />
    if (['doc', 'docx'].includes(extension || '')) return <FileText className="h-5 w-5 text-blue-600" />
    return <File className="h-5 w-5 text-gray-500" />
  }

  const totalEstimatedChunks = files.reduce((sum, f) => sum + (f.estimatedChunks || 0), 0)

  return (
    <div className="space-y-6">
      {/* Usage Info */}
      {usage && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Chunk Usage</span>
              </div>
              <Badge variant="outline">
                {usage.plan} Plan
              </Badge>
            </div>
            <div className="mt-2 text-sm text-brand-midnight/70">
              Current: {usage.current_chunk_usage.toLocaleString()} / {' '}
              {usage.max_total_chunks === -1 ? 'Unlimited' : usage.max_total_chunks.toLocaleString()}
              {usage.max_total_chunks !== -1 && (
                <span className="ml-2">
                  ({usage.remaining_chunks.toLocaleString()} remaining)
                </span>
              )}
            </div>
            {totalEstimatedChunks > 0 && (
              <div className="mt-1 text-xs text-blue-600">
                Estimated chunks for selected files: ~{totalEstimatedChunks}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Chunk limit warning */}
      {usage && usage.remaining_chunks < 50 && usage.max_total_chunks !== -1 && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="flex items-center justify-between">
              <div>
                <strong>Low on chunks:</strong> Only {usage.remaining_chunks} chunks remaining.
                {onUpgrade && (
                  <div className="text-sm mt-1">Upgrade your plan to get more data chunks.</div>
                )}
              </div>
              {onUpgrade && (
                <Button size="sm" variant="outline" onClick={onUpgrade}>
                  <Crown className="h-4 w-4 mr-1" />
                  Upgrade
                </Button>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Documents
          </CardTitle>
          <p className="text-sm text-brand-midnight/70">
            Upload TXT or DOCX files (max {maxFileSize / (1024 * 1024)}MB each, {maxFiles} files total)
          </p>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging 
                ? 'border-brand-dark-cyan bg-brand-dark-cyan/5' 
                : 'border-gray-300 hover:border-brand-dark-cyan/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className={`h-12 w-12 mx-auto mb-4 ${isDragging ? 'text-brand-dark-cyan' : 'text-gray-400'}`} />
            <p className="text-lg font-medium text-brand-black mb-2">
              {isDragging ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-brand-midnight/60 mb-4">
              or click to select files
            </p>
            <input
              type="file"
              multiple
              accept={allowedTypes.join(',')}
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
              disabled={uploading}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outline"
                className="cursor-pointer"
                disabled={uploading}
              >
                <Upload className="h-4 w-4 mr-2" />
                Select Files
              </Button>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Files ({files.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {files.map((fileItem) => (
                <div key={fileItem.id} className="flex items-center gap-3 p-3 border rounded-lg">
                  {getFileIcon(fileItem.file.name)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{fileItem.file.name}</p>
                    <div className="flex items-center gap-4 text-sm text-brand-midnight/60">
                      <span>{(fileItem.file.size / 1024).toFixed(1)} KB</span>
                      {fileItem.estimatedChunks && (
                        <span>~{fileItem.estimatedChunks} chunks</span>
                      )}
                      <Badge
                        variant={
                          fileItem.status === 'completed' ? 'default' :
                          fileItem.status === 'error' ? 'destructive' :
                          fileItem.status === 'uploading' ? 'secondary' : 'outline'
                        }
                      >
                        {fileItem.status}
                      </Badge>
                    </div>
                    {fileItem.status === 'uploading' && (
                      <Progress value={fileItem.progress} className="mt-2 h-1" />
                    )}
                    {fileItem.status === 'error' && fileItem.error && (
                      <p className="text-sm text-red-600 mt-1">{fileItem.error}</p>
                    )}
                  </div>
                  {fileItem.status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : fileItem.status === 'error' ? (
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                  ) : fileItem.status === 'uploading' ? (
                    <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-red-500 hover:bg-red-50"
                      onClick={() => removeFile(fileItem.id)}
                      disabled={uploading}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            {/* Upload Summary */}
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span>Total files: {files.length}</span>
                <span>Estimated chunks: ~{totalEstimatedChunks}</span>
              </div>
              {usage && usage.max_total_chunks !== -1 && (
                <div className="mt-1 text-xs text-brand-midnight/60">
                  After upload: {usage.current_chunk_usage + totalEstimatedChunks} / {usage.max_total_chunks} chunks
                </div>
              )}
            </div>

            {/* Upload Button */}
            <div className="flex justify-end gap-3 mt-4">
              <Button
                variant="outline"
                onClick={() => setFiles([])}
                disabled={uploading}
              >
                Clear All
              </Button>
              <Button
                onClick={uploadFiles}
                disabled={files.length === 0 || uploading || files.some(f => f.status === 'error')}
                className="bg-brand-dark-cyan hover:bg-brand-midnight text-white"
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  'Upload Files'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Upload successful!</strong> Processing {uploadResult.files_processed || files.length} files.
            The content will be available for chat once processing is complete.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}