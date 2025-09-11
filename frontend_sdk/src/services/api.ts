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
      sessionId: request.sessionId.trim(),
      message: request.message.trim(),
      history: Array.isArray(request.history) ? request.history.map(msg => ({
        role: msg.role,
        content: msg.content || ''
      })) : [],
      filters: request.filters || {},
      topK: Math.min(Math.max(request.topK || 10, 1), 20), // 限制在1-20之间
      lang: request.lang || 'zh-CN'
    }

    try {
      const response = await this.request('POST', url, payload)
      
      // 验证响应结构
      if (!this.validateResponse(response)) {
        throw new SDKError('INVALID_RESPONSE', '服务器返回的数据格式不正确')
      }
      
      return response
    } catch (error: any) {
      if (error instanceof SDKError) {
        throw error
      }
      throw new SDKError('REQUEST_FAILED', `请求失败: ${error?.message || '未知错误'}`)
    }
  }

  /**
   * 获取会话历史
   */
  async getSessionHistory(sessionId: string, limit: number = 50): Promise<any> {
    // 参数验证
    if (!sessionId) {
      throw new SDKError('INVALID_PARAMS', '会话ID不能为空')
    }

    const url = `${this.baseURL}/api/chat/sessions/${encodeURIComponent(sessionId)}/history`
    const params = new URLSearchParams({
      limit: Math.min(Math.max(limit, 1), 100).toString() // 限制在1-100之间
    })

    return this.request('GET', `${url}?${params}`)
  }

  /**
   * 清空会话
   */
  async clearSession(sessionId: string): Promise<any> {
    // 参数验证
    if (!sessionId) {
      throw new SDKError('INVALID_PARAMS', '会话ID不能为空')
    }

    const url = `${this.baseURL}/api/chat/sessions/${encodeURIComponent(sessionId)}`

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
   * 验证响应结构
   */
  private validateResponse(response: any): boolean {
    if (!response || typeof response !== 'object') {
      return false
    }
    
    // 检查必要字段
    if (typeof response.reply !== 'string') {
      return false
    }
    
    if (!Array.isArray(response.products)) {
      return false
    }
    
    if (!Array.isArray(response.evidence)) {
      return false
    }
    
    if (typeof response.traceId !== 'string') {
      return false
    }
    
    if (typeof response.sessionId !== 'string') {
      return false
    }
    
    if (typeof response.timestamp !== 'number') {
      return false
    }
    
    // 验证商品结构
    for (const product of response.products) {
      if (!product.sku || !product.title || typeof product.price !== 'number') {
        return false
      }
    }
    
    return true
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
