import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import {
  Settings as SettingsIcon,
  Save,
  RefreshCw,
  Key,
  Database,
  Globe,
  Shield,
  Zap,
  AlertTriangle,
  Info,
  Eye,
  EyeOff
} from 'lucide-react'

interface SystemSettings {
  siliconflow: {
    api_key: string
    base_url: string
    llm_model: string
    embedding_model: string
    reranker_model: string
  }
  milvus: {
    host: string
    port: number
    username: string
    password: string
    collection_name: string
  }
  neo4j: {
    uri: string
    username: string
    password: string
    database: string
  }
  minio: {
    endpoint: string
    access_key: string
    secret_key: string
    bucket_name: string
  }
  security: {
    allowed_origins: string[]
    rate_limit_per_minute: number
    max_file_size_mb: number
  }
  performance: {
    max_concurrent_requests: number
    request_timeout_seconds: number
    cache_ttl_minutes: number
  }
}

export function Settings() {
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({})
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  
  const { toast } = useToast()

  // 获取系统设置
  const { data: currentSettings, isLoading, refetch } = useQuery<SystemSettings>({
    queryKey: ['system-settings'],
    queryFn: async () => {
      // 模拟数据，实际应该从API获取
      return {
        siliconflow: {
          api_key: 'sk-xxxxxxxxxxxxxxxxxxxxxxxxx',
          base_url: 'https://api.siliconflow.cn/v1',
          llm_model: 'deepseek-chat',
          embedding_model: 'BAAI/bge-large-zh-v1.5',
          reranker_model: 'BAAI/bge-reranker-v2-m3'
        },
        milvus: {
          host: 'localhost',
          port: 19530,
          username: 'root',
          password: 'Milvus123',
          collection_name: 'embedai_vectors'
        },
        neo4j: {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password123',
          database: 'neo4j'
        },
        minio: {
          endpoint: 'localhost:9000',
          access_key: 'minioadmin',
          secret_key: 'minioadmin',
          bucket_name: 'embedai-files'
        },
        security: {
          allowed_origins: ['http://localhost:3000', 'https://example.com'],
          rate_limit_per_minute: 100,
          max_file_size_mb: 100
        },
        performance: {
          max_concurrent_requests: 50,
          request_timeout_seconds: 30,
          cache_ttl_minutes: 60
        }
      }
    }
  })

  // 使用useEffect来设置数据
  useEffect(() => {
    if (currentSettings) {
      setSettings(currentSettings)
    }
  }, [currentSettings])

  // 保存设置
  const saveMutation = useMutation({
    mutationFn: async (newSettings: SystemSettings) => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))
      return { success: true }
    },
    onSuccess: () => {
      toast({
        title: '保存成功',
        description: '系统设置已成功保存'
      })
      refetch()
    },
    onError: (error: any) => {
      toast({
        title: '保存失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  // 测试连接
  const testConnectionMutation = useMutation({
    mutationFn: async (service: string) => {
      // 模拟连接测试
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 随机成功或失败
      if (Math.random() > 0.2) {
        return { success: true, message: '连接成功' }
      } else {
        throw new Error('连接失败，请检查配置')
      }
    },
    onSuccess: (data) => {
      toast({
        title: '测试成功',
        description: data.message
      })
    },
    onError: (error: any) => {
      toast({
        title: '测试失败',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  const handleSave = () => {
    if (settings) {
      saveMutation.mutate(settings)
    }
  }

  const handleTestConnection = (service: string) => {
    testConnectionMutation.mutate(service)
  }

  const togglePasswordVisibility = (field: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  const updateSettings = (section: keyof SystemSettings, field: string, value: any) => {
    if (!settings) return
    
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [field]: value
      }
    })
  }

  const updateArraySettings = (section: keyof SystemSettings, field: string, value: string) => {
    if (!settings) return
    
    const array = value.split(',').map(item => item.trim()).filter(item => item)
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [field]: array
      }
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">系统设置</h1>
            <p className="text-muted-foreground mt-1">配置系统参数和第三方服务</p>
          </div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-1/4" />
                <div className="h-4 bg-muted rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="h-10 bg-muted rounded" />
                  <div className="h-10 bg-muted rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">系统设置</h1>
          <p className="text-muted-foreground mt-1">
            配置系统参数和第三方服务连接
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            重新加载
          </Button>
          <Button
            onClick={handleSave}
            disabled={saveMutation.isPending || !settings}
          >
            <Save className="h-4 w-4" />
            {saveMutation.isPending ? '保存中...' : '保存设置'}
          </Button>
        </div>
      </div>

      {/* 警告提示 */}
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-yellow-800">重要提示</h3>
              <p className="text-sm text-yellow-700 mt-1">
                修改系统设置可能会影响服务运行，请确保配置正确后再保存。建议在维护时间窗口进行修改。
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* SiliconFlow API 设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            SiliconFlow API 配置
          </CardTitle>
          <CardDescription>
            配置 SiliconFlow 的 API 密钥和模型参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sf-api-key">API Key *</Label>
              <div className="relative">
                <Input
                  id="sf-api-key"
                  type={showPasswords.sfApiKey ? 'text' : 'password'}
                  value={settings?.siliconflow.api_key || ''}
                  onChange={(e) => updateSettings('siliconflow', 'api_key', e.target.value)}
                  placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxx"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => togglePasswordVisibility('sfApiKey')}
                >
                  {showPasswords.sfApiKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="sf-base-url">Base URL</Label>
              <Input
                id="sf-base-url"
                value={settings?.siliconflow.base_url || ''}
                onChange={(e) => updateSettings('siliconflow', 'base_url', e.target.value)}
                placeholder="https://api.siliconflow.cn/v1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sf-llm-model">LLM 模型</Label>
              <Input
                id="sf-llm-model"
                value={settings?.siliconflow.llm_model || ''}
                onChange={(e) => updateSettings('siliconflow', 'llm_model', e.target.value)}
                placeholder="deepseek-chat"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sf-embedding-model">Embedding 模型</Label>
              <Input
                id="sf-embedding-model"
                value={settings?.siliconflow.embedding_model || ''}
                onChange={(e) => updateSettings('siliconflow', 'embedding_model', e.target.value)}
                placeholder="BAAI/bge-large-zh-v1.5"
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="sf-reranker-model">Reranker 模型</Label>
              <Input
                id="sf-reranker-model"
                value={settings?.siliconflow.reranker_model || ''}
                onChange={(e) => updateSettings('siliconflow', 'reranker_model', e.target.value)}
                placeholder="BAAI/bge-reranker-v2-m3"
              />
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => handleTestConnection('siliconflow')}
            disabled={testConnectionMutation.isPending}
          >
            {testConnectionMutation.isPending ? '测试中...' : '测试连接'}
          </Button>
        </CardContent>
      </Card>

      {/* Milvus 设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Milvus 向量数据库
          </CardTitle>
          <CardDescription>
            配置 Milvus 向量数据库连接参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="milvus-host">主机地址</Label>
              <Input
                id="milvus-host"
                value={settings?.milvus.host || ''}
                onChange={(e) => updateSettings('milvus', 'host', e.target.value)}
                placeholder="localhost"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="milvus-port">端口</Label>
              <Input
                id="milvus-port"
                type="number"
                value={settings?.milvus.port || ''}
                onChange={(e) => updateSettings('milvus', 'port', parseInt(e.target.value) || 19530)}
                placeholder="19530"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="milvus-username">用户名</Label>
              <Input
                id="milvus-username"
                value={settings?.milvus.username || ''}
                onChange={(e) => updateSettings('milvus', 'username', e.target.value)}
                placeholder="root"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="milvus-password">密码</Label>
              <div className="relative">
                <Input
                  id="milvus-password"
                  type={showPasswords.milvusPassword ? 'text' : 'password'}
                  value={settings?.milvus.password || ''}
                  onChange={(e) => updateSettings('milvus', 'password', e.target.value)}
                  placeholder="Milvus123"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => togglePasswordVisibility('milvusPassword')}
                >
                  {showPasswords.milvusPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="milvus-collection">Collection 名称</Label>
              <Input
                id="milvus-collection"
                value={settings?.milvus.collection_name || ''}
                onChange={(e) => updateSettings('milvus', 'collection_name', e.target.value)}
                placeholder="embedai_vectors"
              />
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => handleTestConnection('milvus')}
            disabled={testConnectionMutation.isPending}
          >
            {testConnectionMutation.isPending ? '测试中...' : '测试连接'}
          </Button>
        </CardContent>
      </Card>

      {/* Neo4j 设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Neo4j 图数据库
          </CardTitle>
          <CardDescription>
            配置 Neo4j 图数据库连接参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="neo4j-uri">连接URI</Label>
              <Input
                id="neo4j-uri"
                value={settings?.neo4j.uri || ''}
                onChange={(e) => updateSettings('neo4j', 'uri', e.target.value)}
                placeholder="bolt://localhost:7687"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="neo4j-database">数据库名</Label>
              <Input
                id="neo4j-database"
                value={settings?.neo4j.database || ''}
                onChange={(e) => updateSettings('neo4j', 'database', e.target.value)}
                placeholder="neo4j"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="neo4j-username">用户名</Label>
              <Input
                id="neo4j-username"
                value={settings?.neo4j.username || ''}
                onChange={(e) => updateSettings('neo4j', 'username', e.target.value)}
                placeholder="neo4j"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="neo4j-password">密码</Label>
              <div className="relative">
                <Input
                  id="neo4j-password"
                  type={showPasswords.neo4jPassword ? 'text' : 'password'}
                  value={settings?.neo4j.password || ''}
                  onChange={(e) => updateSettings('neo4j', 'password', e.target.value)}
                  placeholder="password123"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => togglePasswordVisibility('neo4jPassword')}
                >
                  {showPasswords.neo4jPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => handleTestConnection('neo4j')}
            disabled={testConnectionMutation.isPending}
          >
            {testConnectionMutation.isPending ? '测试中...' : '测试连接'}
          </Button>
        </CardContent>
      </Card>

      {/* 安全设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            安全配置
          </CardTitle>
          <CardDescription>
            配置系统安全参数和访问控制
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="allowed-origins">允许的源域名 (CORS)</Label>
            <Input
              id="allowed-origins"
              value={settings?.security.allowed_origins?.join(', ') || ''}
              onChange={(e) => updateArraySettings('security', 'allowed_origins', e.target.value)}
              placeholder="http://localhost:3000, https://example.com"
            />
            <p className="text-xs text-muted-foreground">
              用逗号分隔多个域名
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="rate-limit">API 限流 (次/分钟)</Label>
              <Input
                id="rate-limit"
                type="number"
                value={settings?.security.rate_limit_per_minute || ''}
                onChange={(e) => updateSettings('security', 'rate_limit_per_minute', parseInt(e.target.value) || 100)}
                placeholder="100"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="max-file-size">最大文件大小 (MB)</Label>
              <Input
                id="max-file-size"
                type="number"
                value={settings?.security.max_file_size_mb || ''}
                onChange={(e) => updateSettings('security', 'max_file_size_mb', parseInt(e.target.value) || 100)}
                placeholder="100"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 性能设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            性能配置
          </CardTitle>
          <CardDescription>
            配置系统性能参数和缓存设置
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="max-concurrent">最大并发请求</Label>
              <Input
                id="max-concurrent"
                type="number"
                value={settings?.performance.max_concurrent_requests || ''}
                onChange={(e) => updateSettings('performance', 'max_concurrent_requests', parseInt(e.target.value) || 50)}
                placeholder="50"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="request-timeout">请求超时 (秒)</Label>
              <Input
                id="request-timeout"
                type="number"
                value={settings?.performance.request_timeout_seconds || ''}
                onChange={(e) => updateSettings('performance', 'request_timeout_seconds', parseInt(e.target.value) || 30)}
                placeholder="30"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cache-ttl">缓存TTL (分钟)</Label>
              <Input
                id="cache-ttl"
                type="number"
                value={settings?.performance.cache_ttl_minutes || ''}
                onChange={(e) => updateSettings('performance', 'cache_ttl_minutes', parseInt(e.target.value) || 60)}
                placeholder="60"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 操作按钮 */}
      <div className="flex items-center justify-end gap-3 pt-6 border-t">
        <Button
          variant="outline"
          onClick={() => {
            setSettings(currentSettings)
            toast({
              title: '已重置',
              description: '设置已重置为保存的状态'
            })
          }}
          disabled={saveMutation.isPending}
        >
          重置
        </Button>
        <Button
          onClick={handleSave}
          disabled={saveMutation.isPending || !settings}
        >
          <Save className="h-4 w-4" />
          {saveMutation.isPending ? '保存中...' : '保存所有设置'}
        </Button>
      </div>
    </div>
  )
}
