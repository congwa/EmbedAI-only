import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  TrendingUp,
  Users,
  MessageCircle,
  ThumbsUp,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'

interface AnalyticsData {
  overview: {
    totalUsers: number
    totalChats: number
    totalRecommendations: number
    successRate: number
    avgResponseTime: number
    topProducts: Array<{
      name: string
      recommendations: number
      clickRate: number
    }>
  }
  trends: {
    daily: Array<{
      date: string
      chats: number
      recommendations: number
      users: number
    }>
    hourly: Array<{
      hour: number
      chats: number
      recommendations: number
    }>
  }
  tenants: Array<{
    tenant_id: string
    name: string
    total_chats: number
    total_recommendations: number
    success_rate: number
    last_active: string
  }>
}

export function Analytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [selectedTenant, setSelectedTenant] = useState('')

  const { data: analytics, isLoading, refetch } = useQuery<AnalyticsData>({
    queryKey: ['analytics', dateRange, selectedTenant],
    queryFn: async () => {
      // 模拟数据，实际应该从API获取
      return {
        overview: {
          totalUsers: 2847,
          totalChats: 15632,
          totalRecommendations: 8934,
          successRate: 0.78,
          avgResponseTime: 1.2,
          topProducts: [
            { name: 'MacBook Pro', recommendations: 234, clickRate: 0.85 },
            { name: 'iPhone 15', recommendations: 198, clickRate: 0.92 },
            { name: 'AirPods Pro', recommendations: 156, clickRate: 0.76 },
            { name: 'iPad Air', recommendations: 134, clickRate: 0.81 },
            { name: 'Apple Watch', recommendations: 98, clickRate: 0.68 }
          ]
        },
        trends: {
          daily: Array.from({ length: 7 }, (_, i) => {
            const date = new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000)
            return {
              date: date.toISOString().split('T')[0],
              chats: Math.floor(Math.random() * 500) + 200,
              recommendations: Math.floor(Math.random() * 300) + 100,
              users: Math.floor(Math.random() * 200) + 50
            }
          }),
          hourly: Array.from({ length: 24 }, (_, hour) => ({
            hour,
            chats: Math.floor(Math.random() * 50) + 10,
            recommendations: Math.floor(Math.random() * 30) + 5
          }))
        },
        tenants: [
          {
            tenant_id: 'tenant_1',
            name: '电子产品推荐',
            total_chats: 5832,
            total_recommendations: 3421,
            success_rate: 0.82,
            last_active: '2024-01-21T14:30:00Z'
          },
          {
            tenant_id: 'tenant_2',
            name: '时尚服装',
            total_chats: 3294,
            total_recommendations: 1876,
            success_rate: 0.74,
            last_active: '2024-01-21T13:45:00Z'
          },
          {
            tenant_id: 'tenant_3',
            name: '家居建材',
            total_chats: 2156,
            total_recommendations: 1243,
            success_rate: 0.69,
            last_active: '2024-01-21T12:20:00Z'
          }
        ]
      }
    }
  })

  const exportData = () => {
    // 模拟导出数据
    const csvContent = `日期,聊天数,推荐数,用户数\n${
      analytics?.trends.daily.map(item => 
        `${item.date},${item.chats},${item.recommendations},${item.users}`
      ).join('\n') || ''
    }`
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `analytics_${dateRange.start}_${dateRange.end}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">数据分析</h1>
          <p className="text-muted-foreground mt-1">
            查看系统使用情况和推荐效果分析
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={exportData} disabled={isLoading}>
            <Download className="h-4 w-4" />
            导出数据
          </Button>
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
        </div>
      </div>

      {/* 筛选器 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-end gap-4">
            <div>
              <Label htmlFor="start-date">开始日期</Label>
              <Input
                id="start-date"
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({
                  ...dateRange,
                  start: e.target.value
                })}
              />
            </div>
            <div>
              <Label htmlFor="end-date">结束日期</Label>
              <Input
                id="end-date"
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({
                  ...dateRange,
                  end: e.target.value
                })}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="tenant-filter">租户筛选</Label>
              <Input
                id="tenant-filter"
                placeholder="输入租户ID（留空显示全部）"
                value={selectedTenant}
                onChange={(e) => setSelectedTenant(e.target.value)}
              />
            </div>
            <Button>
              <Filter className="h-4 w-4" />
              应用筛选
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 概览统计 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总用户数</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '-' : analytics?.overview.totalUsers.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              活跃用户总数
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">聊天会话</CardTitle>
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '-' : analytics?.overview.totalChats.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              总聊天会话数
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">推荐次数</CardTitle>
            <ThumbsUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '-' : analytics?.overview.totalRecommendations.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              成功推荐数量
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">成功率</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '-' : `${(analytics?.overview.successRate * 100 || 0).toFixed(1)}%`}
            </div>
            <p className="text-xs text-muted-foreground">
              推荐成功率
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">响应时间</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? '-' : `${analytics?.overview.avgResponseTime || 0}s`}
            </div>
            <p className="text-xs text-muted-foreground">
              平均响应时间
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 趋势图表和热门商品 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* 每日趋势 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              每日趋势
            </CardTitle>
            <CardDescription>
              过去7天的聊天和推荐趋势
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
              </div>
            ) : (
              <div className="space-y-4">
                {analytics?.trends.daily.map((item, index) => (
                  <div key={item.date} className="flex items-center gap-4">
                    <div className="w-20 text-sm text-muted-foreground">
                      {new Date(item.date).toLocaleDateString('zh-CN', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${(item.chats / 500) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs w-12 text-right">{item.chats}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${(item.recommendations / 300) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs w-12 text-right">{item.recommendations}</span>
                      </div>
                    </div>
                  </div>
                ))}
                <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full" />
                    <span>聊天数</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                    <span>推荐数</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 热门商品 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              热门商品
            </CardTitle>
            <CardDescription>
              推荐次数最多的商品
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="flex items-center justify-between mb-2">
                      <div className="h-4 bg-muted rounded w-1/3" />
                      <div className="h-4 bg-muted rounded w-1/4" />
                    </div>
                    <div className="h-2 bg-muted rounded" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {analytics?.overview.topProducts.map((product, index) => (
                  <div key={product.name}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{product.name}</span>
                      <div className="text-right">
                        <div className="text-sm font-medium">{product.recommendations}</div>
                        <div className="text-xs text-muted-foreground">
                          点击率 {(product.clickRate * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          index === 0 ? 'bg-blue-500' : 
                          index === 1 ? 'bg-green-500' : 
                          index === 2 ? 'bg-yellow-500' : 
                          index === 3 ? 'bg-purple-500' : 'bg-gray-500'
                        }`}
                        style={{ 
                          width: `${(product.recommendations / 250) * 100}%` 
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 租户统计 */}
      <Card>
        <CardHeader>
          <CardTitle>租户统计</CardTitle>
          <CardDescription>
            各租户的使用情况和表现
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <div className="h-4 bg-muted rounded w-32" />
                      <div className="h-3 bg-muted rounded w-24" />
                    </div>
                    <div className="flex gap-8">
                      <div className="text-center">
                        <div className="h-6 bg-muted rounded w-12 mx-auto mb-1" />
                        <div className="h-3 bg-muted rounded w-8 mx-auto" />
                      </div>
                      <div className="text-center">
                        <div className="h-6 bg-muted rounded w-12 mx-auto mb-1" />
                        <div className="h-3 bg-muted rounded w-8 mx-auto" />
                      </div>
                      <div className="text-center">
                        <div className="h-6 bg-muted rounded w-12 mx-auto mb-1" />
                        <div className="h-3 bg-muted rounded w-8 mx-auto" />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {analytics?.tenants.map((tenant) => (
                <div key={tenant.tenant_id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-medium">{tenant.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {tenant.tenant_id} · 最后活跃: {formatRelativeTime(tenant.last_active)}
                    </p>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <div className="text-lg font-bold">{tenant.total_chats.toLocaleString()}</div>
                      <div className="text-xs text-muted-foreground">聊天数</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold">{tenant.total_recommendations.toLocaleString()}</div>
                      <div className="text-xs text-muted-foreground">推荐数</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold">{(tenant.success_rate * 100).toFixed(1)}%</div>
                      <div className="text-xs text-muted-foreground">成功率</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
