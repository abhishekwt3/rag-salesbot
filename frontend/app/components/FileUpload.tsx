// Add this component to your frontend (create as components/FileUpload.tsx)

'use client'

import { useState, useRef } from 'react'
import { Button } from "@/components/ui/button"
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FileUploadProps {
  knowledgeBaseId: string
  token: string
  onUploadComplete: () => void
  isOpen: boolean
  onOpenChange: (open: boolean) => void
}

interface UploadFile {
  file: File
  id: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

export default function FileUpload({ 
  knowledgeBaseId, 
  token, 
  onUploadComplete, 
  isOpen, 
  onOpenChange 
}: FileUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedTypes = ['text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const maxFileSize = 10 * 1024 * 1024 // 10MB

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: UploadFile[] = []
    
    Array.from(selectedFiles).forEach((file) => {
      // Validate file type
      const isValidType = allowedTypes.includes(file.type) || 
                         file.name.toLowerCase().endsWith('.txt') || 
                         file.name.toLowerCase().endsWith('.docx')
      
      if (!isValidType) {
        alert(`File "${file.name}" is not supported. Please upload TXT or DOCX files.`)
        return
      }

      // Validate file size
      if (file.size > maxFileSize) {
        alert(`File "${file.name}" is too large. Maximum size is 10MB.`)
        return
      }

      newFiles.push({
        file,
        id: Math.random().toString(36).substr(2, 9),
        status: 'pending',
        progress: 0
      })
    })

    setFiles(prev => [...prev, ...newFiles])
  }

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const uploadFiles = async () => {
    if (files.length === 0) return

    setUploading(true)

    try {
      const formData = new FormData()
      files.forEach(fileObj => {
        formData.append('files', fileObj.file)
      })

      // Update all files to uploading status
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const, progress: 0 })))

      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/upload-documents`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const data = await response.json()
        
        // Mark all files as successful
        setFiles(prev => prev.map(f => ({ 
          ...f, 
          status: 'success' as const, 
          progress: 100 
        })))

        // Close dialog after short delay
        setTimeout(() => {
          onUploadComplete()
          onOpenChange(false)
          setFiles([])
        }, 1500)

      } else {
        const errorData = await response.json()
        
        // Mark all files as error
        setFiles(prev => prev.map(f => ({ 
          ...f, 
          status: 'error' as const, 
          error: errorData.detail || 'Upload failed' 
        })))
      }
    } catch (error) {
      console.error('Upload error:', error)
      
      // Mark all files as error
      setFiles(prev => prev.map(f => ({ 
        ...f, 
        status: 'error' as const, 
        error: 'Network error' 
      })))
    } finally {
      setUploading(false)
    }
  }

  const getFileIcon = (fileName: string) => {
    const ext = fileName.toLowerCase().split('.').pop()
    if (ext === 'txt') return '📄'
    if (ext === 'docx' || ext === 'doc') return '📘'
    return '📁'
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return <FileText className="h-4 w-4 text-gray-400" />
      case 'uploading':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Upload Documents</DialogTitle>
          <DialogDescription>
            Upload TXT or DOCX files to add content to your knowledge base. Maximum 10MB per file.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              Drop files here or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supported formats: TXT, DOCX (max 10MB each)
            </p>
            
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.docx"
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
            />
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">Selected Files</h4>
              
              {files.map((fileObj) => (
                <div key={fileObj.id} className="flex items-center gap-3 p-3 border rounded-lg">
                  <span className="text-xl">{getFileIcon(fileObj.file.name)}</span>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700 truncate">
                      {fileObj.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    
                    {fileObj.status === 'uploading' && (
                      <Progress value={fileObj.progress} className="mt-1" />
                    )}
                    
                    {fileObj.status === 'error' && fileObj.error && (
                      <p className="text-xs text-red-500 mt-1">{fileObj.error}</p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {getStatusIcon(fileObj.status)}
                    
                    {fileObj.status === 'pending' && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeFile(fileObj.id)}
                        className="h-6 w-6 p-0"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Upload Button */}
          {files.length > 0 && (
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setFiles([])}
                disabled={uploading}
              >
                Clear All
              </Button>
              
              <Button
                onClick={uploadFiles}
                disabled={uploading || files.length === 0}
              >
                {uploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload {files.length} File{files.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
            </div>
          )}

          {/* Help Text */}
          <Alert>
            <AlertDescription>
              <strong>Supported formats:</strong>
              <ul className="mt-1 space-y-1 text-sm">
                <li>• <strong>TXT files:</strong> Plain text documents</li>
                <li>• <strong>DOCX files:</strong> Microsoft Word documents</li>
              </ul>
            </AlertDescription>
          </Alert>
        </div>
      </DialogContent>
    </Dialog>
  )
}