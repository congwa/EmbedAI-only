/**
 * SDK类型定义
 */

// 基础消息类型
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  products?: ProductRecommendation[]
}

// 商品推荐类型
export interface ProductRecommendation {
  sku: string
  title: string
  price: number
  currency: string
  imageUrl?: string
  productUrl?: string
  brand?: string
  category?: string
  rating?: number
  stock?: number
  reasons: string[]
  score: number
  tags: string[]
}

// 筛选条件类型
export interface ProductFilter {
  price?: [number, number]
  brand?: string[]
  category?: string[]
  tags?: string[]
}

// 主题配置
export interface ThemeConfig {
  primary: string
  corner: string
  fontFamily?: string
  fontSize?: string
}

// 事件回调类型
export interface EventCallbacks {
  onOpen?: () => void
  onClose?: () => void
  onSend?: (message: string) => void
  onReceive?: (response: any) => void
  onProductClick?: (product: ProductRecommendation) => void
  onError?: (error: Error) => void
}

// 国际化文案
export interface I18nTexts {
  welcome: string
  placeholder: string
  send: string
  retry: string
  clear: string
  minimize: string
  close: string
  typing: string
  networkError: string
  serverError: string
  suggestions: string[]
}

// 主配置接口
export interface IntelliRecsConfig {
  // 基础配置
  tenantId: string
  apiBase: string
  
  // UI配置
  theme: ThemeConfig
  welcome: string
  lang: 'zh-CN' | 'en-US' | string
  
  // 功能配置
  productLinkMode: 'current' | 'new_tab'
  enableHistory: boolean
  maxHistoryLength: number
  
  // 回调事件
  callbacks?: EventCallbacks
  
  // 国际化
  i18n?: Partial<I18nTexts>
  
  // 高级配置
  debug?: boolean
  requestTimeout?: number
  retryAttempts?: number
}

// API请求类型
export interface ChatRequest {
  tenantId: string
  sessionId: string
  message: string
  history: ChatMessage[]
  filters?: ProductFilter
  topK?: number
  lang?: string
}

// API响应类型
export interface ChatResponse {
  success: boolean
  reply: string
  products: ProductRecommendation[]
  evidence: Evidence[]
  traceId: string
  sessionId: string
  timestamp: number
}

// 证据类型
export interface Evidence {
  type: 'doc' | 'url'
  fileId?: string
  snippet: string
  href?: string
  title?: string
}

// Widget状态类型
export interface WidgetState {
  isOpen: boolean
  isMinimized: boolean
  isLoading: boolean
  messages: ChatMessage[]
  currentInput: string
  sessionId: string
}

// 错误类型
export interface SDKError {
  code: string
  message: string
  details?: any
}
