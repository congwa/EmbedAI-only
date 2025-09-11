import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
  Network,
  Database,
  Search,
  RefreshCw,
  Play,
  Settings,
  BarChart3,
  Layers,
  Plus,
  Upload,
  Eye,
  GitBranch,
  Target
} from 'lucide-react'

import { lightragApi, neo4jApi } from '@/apis/graph_api'

export function GraphManagement() {
  const [activeTab, setActiveTab] = useState<'lightrag' | 'neo4j'>('lightrag')
  const [selectedDatabase, setSelectedDatabase] = useState<string>('')
  // 可以在需要时添加搜索功能
  const [neo4jParams, setNeo4jParams] = useState({
    kgdb_name: 'neo4j',
    num_nodes: 100,
    entity_name: '',
    file_path: ''
  })

  const queryClient = useQueryClient()

  // 获取LightRAG数据库列表
  const { data: lightragDatabases, isLoading: loadingLightrag, refetch: refetchLightrag } = useQuery({
    queryKey: ['lightrag-databases'],
    queryFn: async () => {
      const response = await lightragApi.getDatabases()
      return response.data?.databases || []
    }
  })

  // 获取LightRAG统计信息
  const { data: lightragStats, isLoading: loadingStats } = useQuery({
    queryKey: ['lightrag-stats', selectedDatabase],
    queryFn: async () => {
      if (!selectedDatabase) return null
      const response = await lightragApi.getStats(selectedDatabase)
      return response.data
    },
    enabled: !!selectedDatabase && activeTab === 'lightrag'
  })

  // 获取Neo4j信息
  const { data: neo4jInfo, isLoading: loadingNeo4j, refetch: refetchNeo4j } = useQuery({
    queryKey: ['neo4j-info'],
    queryFn: async () => {
      const response = await neo4jApi.getInfo()
      return response.data
    },
    enabled: activeTab === 'neo4j'
  })

  // Neo4j索引节点
  const indexMutation = useMutation({
    mutationFn: async (kgdb_name: string) => {
      return await neo4jApi.indexEntities(kgdb_name)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['neo4j-info'] })
    }
  })

  // Neo4j添加实体
  const addEntitiesMutation = useMutation({
    mutationFn: async ({ file_path, kgdb_name }: { file_path: string; kgdb_name: string }) => {
      return await neo4jApi.addEntities(file_path, kgdb_name)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['neo4j-info'] })
    }
  })

  const handleIndexEntities = () => {
    indexMutation.mutate(neo4jParams.kgdb_name)
  }

  const handleAddEntities = () => {
    if (!neo4jParams.file_path) return
    addEntitiesMutation.mutate({
      file_path: neo4jParams.file_path,
      kgdb_name: neo4jParams.kgdb_name
    })
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">图数据库管理</h1>
          <p className="text-muted-foreground mt-1">
            管理LightRAG知识图谱和Neo4j图数据库
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => activeTab === 'lightrag' ? refetchLightrag() : refetchNeo4j()}
            disabled={loadingLightrag || loadingNeo4j}
          >
            <RefreshCw className={`h-4 w-4 ${(loadingLightrag || loadingNeo4j) ? 'animate-spin' : ''}`} />
            刷新
          </Button>
        </div>
      </div>

      {/* 标签切换 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-4">
            <Button
              variant={activeTab === 'lightrag' ? 'default' : 'outline'}
              onClick={() => setActiveTab('lightrag')}
              className="flex items-center gap-2"
            >
              <Network className="h-4 w-4" />
              LightRAG 知识图谱
            </Button>
            <Button
              variant={activeTab === 'neo4j' ? 'default' : 'outline'}
              onClick={() => setActiveTab('neo4j')}
              className="flex items-center gap-2"
            >
              <Database className="h-4 w-4" />
              Neo4j 图数据库
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* LightRAG 管理界面 */}
      {activeTab === 'lightrag' && (
        <div className="space-y-6">
          {/* 数据库选择 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                LightRAG 数据库
              </CardTitle>
              <CardDescription>
                选择要管理的LightRAG知识图谱数据库
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingLightrag ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                  <span className="ml-2">加载数据库列表...</span>
                </div>
              ) : lightragDatabases && lightragDatabases.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {lightragDatabases.map((db: any) => (
                    <Card 
                      key={db.db_id} 
                      className={`cursor-pointer transition-colors ${
                        selectedDatabase === db.db_id ? 'ring-2 ring-primary' : 'hover:bg-muted/50'
                      }`}
                      onClick={() => setSelectedDatabase(db.db_id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{db.name}</h4>
                          <Badge variant="default">LightRAG</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {db.description || '无描述'}
                        </p>
                        <div className="text-xs text-muted-foreground">
                          ID: {db.db_id}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">暂无LightRAG数据库</p>
                  <p className="text-muted-foreground">
                    请先创建LightRAG类型的知识库
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 图谱统计信息 */}
          {selectedDatabase && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  图谱统计信息
                </CardTitle>
                <CardDescription>
                  {selectedDatabase} 的知识图谱统计数据
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loadingStats ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin" />
                    <span className="ml-2">加载统计信息...</span>
                  </div>
                ) : lightragStats ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-blue-500" />
                          <div>
                            <p className="text-sm text-muted-foreground">总节点数</p>
                            <p className="text-2xl font-bold">{lightragStats.total_nodes}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2">
                          <GitBranch className="h-4 w-4 text-green-500" />
                          <div>
                            <p className="text-sm text-muted-foreground">总关系数</p>
                            <p className="text-2xl font-bold">{lightragStats.total_edges}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2">
                          <Layers className="h-4 w-4 text-purple-500" />
                          <div>
                            <p className="text-sm text-muted-foreground">实体类型</p>
                            <p className="text-2xl font-bold">{lightragStats.entity_types?.length || 0}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2">
                          <Eye className="h-4 w-4 text-orange-500" />
                          <div>
                            <p className="text-sm text-muted-foreground">数据状态</p>
                            <Badge variant={lightragStats.is_truncated ? "secondary" : "default"}>
                              {lightragStats.is_truncated ? '部分加载' : '完整'}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      无法获取统计信息
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Neo4j 管理界面 */}
      {activeTab === 'neo4j' && (
        <div className="space-y-6">
          {/* Neo4j 信息 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Neo4j 数据库信息
              </CardTitle>
              <CardDescription>
                Neo4j图数据库状态和统计信息
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingNeo4j ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                  <span className="ml-2">加载Neo4j信息...</span>
                </div>
              ) : neo4jInfo ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {Object.entries(neo4jInfo).map(([key, value]) => (
                    <Card key={key}>
                      <CardContent className="p-4">
                        <p className="text-sm text-muted-foreground">{key}</p>
                        <p className="text-lg font-medium">{String(value)}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">Neo4j数据库未连接</p>
                  <p className="text-muted-foreground">
                    请检查Neo4j服务状态
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Neo4j 操作 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Neo4j 管理操作
              </CardTitle>
              <CardDescription>
                执行Neo4j图数据库的管理任务
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 数据库配置 */}
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">数据库名称</label>
                  <Input
                    value={neo4jParams.kgdb_name}
                    onChange={(e) => setNeo4jParams({ ...neo4jParams, kgdb_name: e.target.value })}
                    placeholder="neo4j"
                  />
                </div>
              </div>

              {/* 节点索引 */}
              <div className="border rounded-lg p-4">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  节点嵌入向量索引
                </h4>
                <p className="text-sm text-muted-foreground mb-4">
                  为图谱节点添加嵌入向量，提升查询性能
                </p>
                <Button 
                  onClick={handleIndexEntities}
                  disabled={indexMutation.isPending}
                  className="w-full"
                >
                  {indexMutation.isPending ? (
                    <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  {indexMutation.isPending ? '索引中...' : '开始索引'}
                </Button>
              </div>

              {/* 添加实体 */}
              <div className="border rounded-lg p-4">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  批量添加实体
                </h4>
                <p className="text-sm text-muted-foreground mb-4">
                  通过JSONL文件批量添加图谱实体
                </p>
                <div className="space-y-3">
                  <Input
                    value={neo4jParams.file_path}
                    onChange={(e) => setNeo4jParams({ ...neo4jParams, file_path: e.target.value })}
                    placeholder="请输入JSONL文件路径"
                  />
                  <Button 
                    onClick={handleAddEntities}
                    disabled={addEntitiesMutation.isPending || !neo4jParams.file_path}
                    className="w-full"
                  >
                    {addEntitiesMutation.isPending ? (
                      <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Plus className="h-4 w-4 mr-2" />
                    )}
                    {addEntitiesMutation.isPending ? '添加中...' : '添加实体'}
                  </Button>
                </div>
              </div>

              {/* 节点查询 */}
              <div className="border rounded-lg p-4">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Search className="h-4 w-4" />
                  节点查询
                </h4>
                <p className="text-sm text-muted-foreground mb-4">
                  根据实体名称查询图节点信息
                </p>
                <div className="flex gap-2">
                  <Input
                    value={neo4jParams.entity_name}
                    onChange={(e) => setNeo4jParams({ ...neo4jParams, entity_name: e.target.value })}
                    placeholder="请输入实体名称"
                  />
                  <Button variant="outline">
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
