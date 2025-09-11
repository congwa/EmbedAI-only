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
  Calendar,
} from 'lucide-react'
import { formatDateTime, formatFileSize } from '@/lib/utils'
import { adminDatabaseApi } from '@/apis'

interface DatabaseInfo {
  id: number;
  db_id: string;
  name: string;
  description?: string;
  embed_model: string;
  dimension: number;
  created_at: string;
  file_count: number;
  status?: string;
}

interface CreateDatabaseRequest {
  name: string;
  description?: string;
  embed_model: string;
  dimension: number;
}

export function DatabaseManagement() {
  const [filters, setFilters] = useState({
    search: '',
    status: 'all'
  });
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newDatabase, setNewDatabase] = useState<CreateDatabaseRequest>({
    name: '',
    description: '',
    embed_model: 'text-embedding-ada-002',
    dimension: 1536
  })
  
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // 获取数据库列表
  const { data: databases, isLoading, refetch } = useQuery<DatabaseInfo[]>({
    queryKey: ['admin-databases'],
    queryFn: async () => {
      const response = await adminDatabaseApi.getDatabases()
      return response
    }
  })

  // 创建数据库
  const createMutation = useMutation({
    mutationFn: async (data: CreateDatabaseRequest) => {
      if (!data.name) {
        throw new Error('数据库名称不能为空')
      }
      
      const result = await adminDatabaseApi.createDatabase({
        name: data.name,
        description: data.description || undefined,
        embed_model: data.embed_model,
        dimension: data.dimension
      });
      return result;
    },
    onSuccess: () => {
      toast({
        title: '创建成功',
        description: '数据库已成功创建'
      })
      setIsCreateModalOpen(false)
      setNewDatabase({
        name: '',
        description: '',
        embed_model: 'text-embedding-ada-002',
        dimension: 1536
      })
      queryClient.invalidateQueries({ queryKey: ['admin-databases'] })
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
    mutationFn: async (dbId: string) => {
      return await adminDatabaseApi.deleteDatabase(dbId)
    },
    onSuccess: () => {
      toast({
        title: '删除成功',
        description: '数据库已成功删除'
      })
      queryClient.invalidateQueries({ queryKey: ['admin-databases'] })
    },
    onError: (error: any) => {
      toast({
        title: '删除失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 重建索引 (暂时使用模拟实现)
  const rebuildMutation = useMutation({
    mutationFn: async (dbId: string) => {
      // TODO: 实现真实的重建索引API
      console.log('重建索引:', dbId)
      await new Promise(resolve => setTimeout(resolve, 2000))
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '重建成功',
        description: '索引已成功重建'
      })
      queryClient.invalidateQueries({ queryKey: ['admin-databases'] })
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
  const filteredDatabases = databases?.filter(db => {
    const matchesSearch = db.name.toLowerCase().includes(filters.search.toLowerCase());
    const matchesStatus = filters.status === 'all' || (db.status || 'active') === filters.status;
    return matchesSearch && matchesStatus;
  }) || []

  const handleCreateDatabase = () => {
    createMutation.mutate(newDatabase)
  }

  const handleDeleteDatabase = (dbId: string) => {
    if (window.confirm('确定要删除这个数据库吗？此操作不可撤销。')) {
      deleteMutation.mutate(dbId)
    }
  }

  const handleRebuildIndex = (dbId: string) => {
    if (window.confirm('确定要重建索引吗？这可能需要一些时间。')) {
      rebuildMutation.mutate(dbId)
    }
  }

  const getStatusBadge = (status: DatabaseInfo['status']) => {
    const statusColors: { [key: string]: string } = {
      active: 'text-green-600',
      inactive: 'text-gray-500',
      building: 'text-blue-600'
    };

    const statusLabels: { [key: string]: string } = {
      active: '活跃',
      inactive: '未激活', 
      building: '构建中'
    };

    return (
      <div className={`inline-flex items-center gap-1 ${statusColors[status || 'active']}`}>
        <div className="w-2 h-2 rounded-full bg-current"></div>
        <span className="text-sm">{statusLabels[status || 'active']}</span>
      </div>
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
          <Button onClick={() => setIsCreateModalOpen(true)}>
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
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <Label>状态</Label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="bg-white border border-gray-300 rounded py-2 pl-3 pr-10 text-sm focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
              >
                <option value="all">全部</option>
                <option value="active">活跃</option>
                <option value="inactive">未激活</option>
                <option value="building">构建中</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 创建数据库表单 */}
      {isCreateModalOpen && (
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
            </div>
            <div className="space-y-2">
              <Label htmlFor="embed_model">嵌入模型 *</Label>
              <Input
                id="embed_model"
                placeholder="例如: text-embedding-ada-002"
                value={newDatabase.embed_model}
                onChange={(e) => setNewDatabase({
                  ...newDatabase,
                  embed_model: e.target.value
                })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="dimension">维度 *</Label>
              <Input
                id="dimension"
                placeholder="例如: 1536"
                value={newDatabase.dimension}
                onChange={(e) => setNewDatabase({
                  ...newDatabase,
                  dimension: parseInt(e.target.value)
                })}
              />
            </div>
            <div className="flex items-center gap-3 pt-4">
              <Button
                onClick={handleCreateDatabase}
                disabled={createMutation.isPending || !newDatabase.name || !newDatabase.embed_model || !newDatabase.dimension}
              >
                {createMutation.isPending ? '创建中...' : '创建数据库'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setIsCreateModalOpen(false)}
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
                {filters.search ? '尝试修改搜索条件' : '开始创建您的第一个数据库'}
              </p>
              {!filters.search && (
                <Button onClick={() => setIsCreateModalOpen(true)}>
                  <Plus className="h-4 w-4" />
                  创建数据库
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredDatabases.map((db) => (
              <Card key={db.db_id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg truncate">{db.name}</CardTitle>
                      <p className="text-sm text-muted-foreground text-center">
                        {db.description || '无描述'}
                      </p>
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
                      <span className="text-sm">{db.db_id}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-muted-foreground">
                        <HardDrive className="h-4 w-4" />
                        文件/大小
                      </span>
                      <span className="text-sm">{db.file_count || 0} 个文件</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        创建时间
                      </span>
                      <span className="text-sm">{formatDateTime(db.created_at)}</span>
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRebuildIndex(db.db_id)}
                      disabled={db.status === 'building'}
                      className="mr-2"
                    >
                      <Settings className="h-4 w-4" />
                      重建索引
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteDatabase(db.db_id)}
                      disabled={db.status === 'building'}
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
