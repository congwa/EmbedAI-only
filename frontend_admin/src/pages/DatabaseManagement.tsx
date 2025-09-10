import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import {
  Plus,
  Database,
  Trash2,
  RefreshCw,
  Search,
  Settings,
  Users,
  HardDrive,
  Calendar
} from 'lucide-react'
import { formatDateTime, formatFileSize } from '@/lib/utils'

interface DatabaseInfo {
  tenant_id: string
  name: string
  description: string
  created_at: string
  files_count: number
  size_mb: number
  last_updated: string
  status: 'active' | 'inactive' | 'building'
}

interface CreateDatabaseRequest {
  tenant_id: string
  name: string
  description?: string
}

export function DatabaseManagement() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newDatabase, setNewDatabase] = useState<CreateDatabaseRequest>({
    tenant_id: '',
    name: '',
    description: ''
  })
  
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // 获取数据库列表
  const { data: databases, isLoading, refetch } = useQuery<DatabaseInfo[]>({
    queryKey: ['databases'],
    queryFn: async () => {
      // 模拟数据，实际应该调用API
      return [
        {
          tenant_id: 'tenant_1',
          name: '电子产品推荐',
          description: '包含手机、电脑、平板等电子产品的知识库',
          created_at: '2024-01-15T10:30:00Z',
          files_count: 125,
          size_mb: 45.6,
          last_updated: '2024-01-20T14:22:00Z',
          status: 'active'
        },
        {
          tenant_id: 'tenant_2',
          name: '时尚服装',
          description: '男女装、童装、鞋包等时尚产品推荐',
          created_at: '2024-01-18T09:15:00Z',
          files_count: 87,
          size_mb: 32.1,
          last_updated: '2024-01-21T11:45:00Z',
          status: 'active'
        },
        {
          tenant_id: 'tenant_3',
          name: '家居建材',
          description: '家具、装修材料、家电等家居产品',
          created_at: '2024-01-20T16:20:00Z',
          files_count: 45,
          size_mb: 18.9,
          last_updated: '2024-01-21T13:10:00Z',
          status: 'building'
        }
      ]
    }
  })

  // 创建数据库
  const createMutation = useMutation({
    mutationFn: async (data: CreateDatabaseRequest) => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (!data.tenant_id || !data.name) {
        throw new Error('租户ID和数据库名称不能为空')
      }
      
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '创建成功',
        description: '数据库已成功创建'
      })
      setShowCreateForm(false)
      setNewDatabase({ tenant_id: '', name: '', description: '' })
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    },
    onError: (error: any) => {
      toast({
        title: '创建失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 删除数据库
  const deleteMutation = useMutation({
    mutationFn: async (tenantId: string) => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '删除成功',
        description: '数据库已成功删除'
      })
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    },
    onError: (error: any) => {
      toast({
        title: '删除失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 重建索引
  const rebuildMutation = useMutation({
    mutationFn: async (tenantId: string) => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '重建成功',
        description: '索引已成功重建'
      })
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    },
    onError: (error: any) => {
      toast({
        title: '重建失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 过滤数据库
  const filteredDatabases = databases?.filter(db =>
    db.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    db.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    db.tenant_id.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  const handleCreateDatabase = () => {
    createMutation.mutate(newDatabase)
  }

  const handleDeleteDatabase = (tenantId: string) => {
    if (window.confirm('确定要删除这个数据库吗？此操作不可撤销。')) {
      deleteMutation.mutate(tenantId)
    }
  }

  const handleRebuildIndex = (tenantId: string) => {
    if (window.confirm('确定要重建索引吗？这可能需要一些时间。')) {
      rebuildMutation.mutate(tenantId)
    }
  }

  const getStatusBadge = (status: DatabaseInfo['status']) => {
    const variants = {
      active: 'bg-green-100 text-green-800 border-green-200',
      inactive: 'bg-gray-100 text-gray-800 border-gray-200',
      building: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    }
    
    const labels = {
      active: '活跃',
      inactive: '非活跃',
      building: '构建中'
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[status]}`}>
        {labels[status]}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">数据库管理</h1>
          <p className="text-muted-foreground mt-1">
            管理知识库数据库，创建、删除和维护数据库
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="h-4 w-4" />
            创建数据库
          </Button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="搜索数据库名称、描述或租户ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 创建数据库表单 */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>创建新数据库</CardTitle>
            <CardDescription>
              填写数据库信息以创建新的知识库
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tenant_id">租户ID *</Label>
                <Input
                  id="tenant_id"
                  placeholder="例如: tenant_shop_001"
                  value={newDatabase.tenant_id}
                  onChange={(e) => setNewDatabase({
                    ...newDatabase,
                    tenant_id: e.target.value
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">数据库名称 *</Label>
                <Input
                  id="name"
                  placeholder="例如: 电子产品推荐"
                  value={newDatabase.name}
                  onChange={(e) => setNewDatabase({
                    ...newDatabase,
                    name: e.target.value
                  })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">描述</Label>
              <Input
                id="description"
                placeholder="描述这个数据库的用途和内容"
                value={newDatabase.description}
                onChange={(e) => setNewDatabase({
                  ...newDatabase,
                  description: e.target.value
                })}
              />
            </div>
            <div className="flex items-center gap-3 pt-4">
              <Button
                onClick={handleCreateDatabase}
                disabled={createMutation.isPending || !newDatabase.tenant_id || !newDatabase.name}
              >
                {createMutation.isPending ? '创建中...' : '创建数据库'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                取消
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 数据库列表 */}
      <div className="grid gap-4">
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-muted rounded w-3/4" />
                  <div className="h-4 bg-muted rounded w-full" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="h-4 bg-muted rounded w-1/2" />
                    <div className="h-4 bg-muted rounded w-3/4" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredDatabases.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">没有找到数据库</p>
              <p className="text-muted-foreground mb-4">
                {searchQuery ? '尝试修改搜索条件' : '开始创建您的第一个数据库'}
              </p>
              {!searchQuery && (
                <Button onClick={() => setShowCreateForm(true)}>
                  <Plus className="h-4 w-4" />
                  创建数据库
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredDatabases.map((db) => (
              <Card key={db.tenant_id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg truncate">{db.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {db.description || '无描述'}
                      </CardDescription>
                    </div>
                    {getStatusBadge(db.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 基本信息 */}
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-muted-foreground">
                        <Users className="h-4 w-4" />
                        租户ID
                      </span>
                      <span className="font-mono text-xs">{db.tenant_id}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-muted-foreground">
                        <HardDrive className="h-4 w-4" />
                        文件/大小
                      </span>
                      <span>{db.files_count} 个 / {formatFileSize(db.size_mb * 1024 * 1024)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        创建时间
                      </span>
                      <span>{formatDateTime(db.created_at)}</span>
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRebuildIndex(db.tenant_id)}
                      disabled={rebuildMutation.isPending || db.status === 'building'}
                    >
                      <Settings className="h-4 w-4" />
                      重建索引
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteDatabase(db.tenant_id)}
                      disabled={deleteMutation.isPending || db.status === 'building'}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                      删除
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
