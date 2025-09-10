/**
 * API服务
 */
import { ChatRequest, ChatResponse } from '../types'

class APIService {
  private baseURL: string = ''
  private timeout: number = 30000
  private retryAttempts: number = 3

  /**
   * 设置API配置
   */
  configure(baseURL: string, timeout?: number, retryAttempts?: number) {
    this.baseURL = baseURL.replace(/\/$/, '') // 移除末尾斜杠
    this.timeout = timeout || 30000
    this.retryAttempts = retryAttempts || 3
  }

  /**
   * 发送消息
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const url = `${this.baseURL}/api/chat/recommendations`
    
    const payload = {
      tenantId: request.tenantId,
      sessionId: request.sessionId,
      message: request.message,
      history: request.history.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      filters: request.filters,
      topK: request.topK || 10,
      lang: request.lang || 'zh-CN'
    }

    return this.request('POST', url, payload)
  }

  /**
   * 获取会话历史
   */
  async getSessionHistory(sessionId: string, tenantId: string, limit: number = 50): Promise<any> {
    const url = `${this.baseURL}/api/chat/sessions/${sessionId}/history?tenant_id=${tenantId}&limit=${limit}`
    return this.request('GET', url)
  }

  /**
   * 清空会话
   */
  async clearSession(sessionId: string, tenantId: string): Promise<any> {
    const url = `${this.baseURL}/api/chat/sessions/${sessionId}?tenant_id=${tenantId}`
    return this.request('DELETE', url)
  }

  /**
   * 通用请求方法
   */
  private async request(method: string, url: string, data?: any, attempt: number = 1): Promise<any> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeout)

      const options: RequestInit = {
        method,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      }

      if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data)
      }

      const response = await fetch(url, options)
      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      // 检查业务层面的成功状态
      if (result.success === false) {
        throw new SDKError(
          result.error?.code || 'API_ERROR',
          result.error?.message || '请求处理失败',
          result.error
        )
      }

      return result

    } catch (error: any) {
      console.error(`[APIService] 请求失败 (尝试 ${attempt}/${this.retryAttempts}):`, error)

      // 如果是网络错误且还有重试机会，则重试
      if (attempt < this.retryAttempts && this.isRetryableError(error)) {
        await this.delay(1000 * attempt) // 递增延迟
        return this.request(method, url, data, attempt + 1)
      }

      // 转换错误类型
      if (error instanceof SDKError) {
        throw error
      }

      if (error?.name === 'AbortError') {
        throw new SDKError('TIMEOUT_ERROR', '请求超时，请检查网络连接')
      }

      if (error?.message?.includes('Failed to fetch')) {
        throw new SDKError('NETWORK_ERROR', '网络连接失败，请检查网络设置')
      }

      throw new SDKError('UNKNOWN_ERROR', error?.message || '未知错误')
    }
  }

  /**
   * 检查是否为可重试的错误
   */
  private isRetryableError(error: any): boolean {
    if (error.name === 'AbortError') return false
    if (error instanceof SDKError) return false
    
    // 网络错误可以重试
    if (error.message.includes('Failed to fetch')) return true
    if (error.message.includes('NetworkError')) return true
    
    return false
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// 导出单例实例
export const apiService = new APIService()

// SDK错误类
export class SDKError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'SDKError'
  }
}
