import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import {
  Upload,
  File,
  FileText,
  Image,
  Trash2,
  Download,
  Search,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Clock,
  X
} from 'lucide-react'
import { formatDateTime, formatFileSize } from '@/lib/utils'

interface FileInfo {
  id: string
  filename: string
  size: number
  content_type: string
  upload_time: string
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
}

interface UploadProgress {
  file: File
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  error?: string
}

export function FileUpload() {
  const [searchQuery, setSearchQuery] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([])
  
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // 获取文件列表
  const { data: files, isLoading, refetch } = useQuery<FileInfo[]>({
    queryKey: ['files'],
    queryFn: async () => {
      // 模拟数据，实际应该调用API
      return [
        {
          id: 'file_1',
          filename: 'products.csv',
          size: 2048576,
          content_type: 'text/csv',
          upload_time: '2024-01-21T10:30:00Z',
          processing_status: 'completed' as const
        },
        {
          id: 'file_2',
          filename: 'product_images.zip',
          size: 15728640,
          content_type: 'application/zip',
          upload_time: '2024-01-21T11:15:00Z',
          processing_status: 'processing' as const
        },
        {
          id: 'file_3',
          filename: 'descriptions.txt',
          size: 512000,
          content_type: 'text/plain',
          upload_time: '2024-01-21T09:45:00Z',
          processing_status: 'failed' as const,
          error_message: '文件格式不支持'
        }
      ]
    }
  })

  // 文件上传
  const uploadMutation = useMutation({
    mutationFn: async ({ files }: { files: File[] }) => {
      // 模拟文件上传
      for (const file of files) {
        const uploadItem: UploadProgress = {
          file,
          progress: 0,
          status: 'uploading'
        }
        
        setUploadProgress(prev => [...prev, uploadItem])
        
        // 模拟上传进度
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100))
          setUploadProgress(prev => 
            prev.map(item => 
              item.file === file 
                ? { ...item, progress }
                : item
            )
          )
        }
        
        // 模拟处理状态
        setUploadProgress(prev => 
          prev.map(item => 
            item.file === file 
              ? { ...item, status: 'processing' }
              : item
          )
        )
        
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 随机成功或失败
        const success = Math.random() > 0.2
        setUploadProgress(prev => 
          prev.map(item => 
            item.file === file 
              ? { 
                  ...item, 
                  status: success ? 'completed' : 'failed',
                  error: success ? undefined : '处理失败'
                }
              : item
          )
        )
      }
      
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '上传完成',
        description: '文件已成功上传并处理'
      })
      queryClient.invalidateQueries({ queryKey: ['files'] })
      // 3秒后清除上传进度
      setTimeout(() => {
        setUploadProgress([])
      }, 3000)
    },
    onError: (error: any) => {
      toast({
        title: '上传失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 删除文件
  const deleteMutation = useMutation({
    mutationFn: async (fileId: string) => {
      await new Promise(resolve => setTimeout(resolve, 500))
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '删除成功',
        description: '文件已成功删除'
      })
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
    onError: (error: any) => {
      toast({
        title: '删除失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 处理文件拖拽
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    if (droppedFiles.length > 0) {
      uploadMutation.mutate({ files: droppedFiles })
    }
  }, [uploadMutation, toast])

  // 处理文件选择
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length > 0) {
      uploadMutation.mutate({ files: selectedFiles })
    }
    // 清除input值以允许重复选择同一文件
    e.target.value = ''
  }

  const handleDeleteFile = (fileId: string) => {
    if (window.confirm('确定要删除这个文件吗？')) {
      deleteMutation.mutate(fileId)
    }
  }

  // 过滤文件
  const filteredFiles = files?.filter(file =>
    file.filename.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) return Image
    if (contentType.includes('text') || contentType.includes('csv')) return FileText
    return File
  }

  const getStatusIcon = (status: FileInfo['processing_status']) => {
    switch (status) {
      case 'completed': return CheckCircle2
      case 'processing': return Clock
      case 'failed': return AlertCircle
      default: return Clock
    }
  }

  const getStatusColor = (status: FileInfo['processing_status']) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'processing': return 'text-yellow-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">文件上传</h1>
          <p className="text-muted-foreground mt-1">
            上传和管理知识库文件，支持多种文件格式
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          刷新
        </Button>
      </div>

      {/* 租户选择和搜索 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="搜索文件名..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 文件上传区域 */}
      <Card>
        <CardHeader>
          <CardTitle>上传文件</CardTitle>
          <CardDescription>
            拖拽文件到下方区域或点击选择文件。支持 CSV、TXT、JSON、PDF 等格式。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragOver 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg font-medium mb-2">
              拖拽文件到此处或点击选择
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              支持多文件上传，单个文件最大 100MB
            </p>
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
              accept=".csv,.txt,.json,.pdf,.doc,.docx,.xls,.xlsx"
            />
            <Button asChild>
              <label htmlFor="file-upload" className="cursor-pointer">
                选择文件
              </label>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 上传进度 */}
      {uploadProgress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>上传进度</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {uploadProgress.map((item, index) => (
              <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.file.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {item.status === 'uploading' && (
                      <>
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${item.progress}%` }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">{item.progress}%</span>
                      </>
                    )}
                    {item.status === 'processing' && (
                      <span className="text-xs text-yellow-600">处理中...</span>
                    )}
                    {item.status === 'completed' && (
                      <span className="text-xs text-green-600 flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        完成
                      </span>
                    )}
                    {item.status === 'failed' && (
                      <span className="text-xs text-red-600 flex items-center gap-1">
                        <X className="h-3 w-3" />
                        {item.error || '失败'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* 文件列表 */}
      <Card>
        <CardHeader>
          <CardTitle>文件列表</CardTitle>
          <CardDescription>
            已上传的文件和处理状态
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse flex items-center gap-3 p-3 border rounded-lg">
                  <div className="h-5 w-5 bg-muted rounded" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-muted rounded w-1/3" />
                    <div className="h-3 bg-muted rounded w-1/4" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredFiles.length === 0 ? (
            <div className="text-center py-8">
              <File className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">没有找到文件</p>
              <p className="text-muted-foreground">
                {searchQuery ? '尝试修改搜索条件' : '上传您的第一个文件'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredFiles.map((file) => {
                const FileIcon = getFileIcon(file.content_type)
                const StatusIcon = getStatusIcon(file.processing_status)
                
                return (
                  <div key={file.id} className="flex items-center gap-3 p-3 border rounded-lg">
                    <FileIcon className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium truncate">{file.filename}</p>
                        <StatusIcon className={`h-4 w-4 ${getStatusColor(file.processing_status)}`} />
                      </div>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{formatFileSize(file.size)}</span>
                        <span>{formatDateTime(file.upload_time)}</span>
                      </div>
                      {file.error_message && (
                        <p className="text-xs text-destructive mt-1">
                          {file.error_message}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteFile(file.id)}
                        disabled={deleteMutation.isPending}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
