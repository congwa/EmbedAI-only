import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Database, Upload, MessageCircle, TrendingUp, Activity, Clock } from 'lucide-react'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'

interface DashboardStats {
  totalDatabases: number
  totalFiles: number
  totalChats: number
  totalRecommendations: number
  recentActivity: Array<{
    id: string
    type: 'database' | 'upload' | 'chat' | 'recommendation'
    description: string
    timestamp: string
  }>
}

export function Dashboard() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // 模拟数据，实际应该从API获取
      return {
        totalDatabases: 5,
        totalFiles: 1247,
        totalChats: 3456,
        totalRecommendations: 8923,
        recentActivity: [
          {
            id: '1',
            type: 'upload',
            description: '上传了新的商品数据文件 products.csv',
            timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
          },
          {
            id: '2',
            type: 'database',
            description: '创建了新的知识库 "电子产品推荐"',
            timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString()
          },
          {
            id: '3',
            type: 'chat',
            description: '用户咨询了关于笔记本电脑的推荐',
            timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
          },
          {
            id: '4',
            type: 'recommendation',
            description: '成功推荐了 MacBook Pro 给用户',
            timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString()
          },
        ]
      }
    }
  })

  const statsCards = [
    {
      title: '知识库数量',
      value: stats?.totalDatabases || 0,
      icon: Database,
      description: '当前管理的知识库数量',
      color: 'text-blue-600'
    },
    {
      title: '上传文件',
      value: stats?.totalFiles || 0,
      icon: Upload,
      description: '总计上传的文件数量',
      color: 'text-green-600'
    },
    {
      title: '聊天会话',
      value: stats?.totalChats || 0,
      icon: MessageCircle,
      description: '用户聊天会话总数',
      color: 'text-purple-600'
    },
    {
      title: '推荐次数',
      value: stats?.totalRecommendations || 0,
      icon: TrendingUp,
      description: '成功推荐商品次数',
      color: 'text-orange-600'
    }
  ]

  const activityIcons = {
    database: Database,
    upload: Upload,
    chat: MessageCircle,
    recommendation: TrendingUp
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">仪表板</h1>
          <p className="text-muted-foreground mt-1">
            欢迎使用 EmbedAI RAG 推荐系统管理后台
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>最后更新: {formatDateTime(new Date())}</span>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat) => (
          <Card key={stat.title} className="relative overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '-' : stat.value.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 最近活动 */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              最近活动
            </CardTitle>
            <CardDescription>
              系统最近的操作和事件
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="flex items-start gap-3">
                      <div className="h-8 w-8 rounded-full bg-muted" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-muted rounded w-3/4" />
                        <div className="h-3 bg-muted rounded w-1/2" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {stats?.recentActivity.map((activity) => {
                  const Icon = activityIcons[activity.type]
                  return (
                    <div key={activity.id} className="flex items-start gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium leading-5">
                          {activity.description}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatRelativeTime(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 系统状态 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              系统状态
            </CardTitle>
            <CardDescription>
              当前系统运行状态概览
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API 服务</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm text-muted-foreground">正常</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">知识库连接</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm text-muted-foreground">正常</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">文件存储</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-yellow-500" />
                  <span className="text-sm text-muted-foreground">警告</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">SiliconFlow API</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm text-muted-foreground">正常</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
