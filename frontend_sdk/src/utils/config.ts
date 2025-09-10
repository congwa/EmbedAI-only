/**
 * 配置工具函数
 */
import { IntelliRecsConfig, I18nTexts } from '../types'

// 默认国际化文案
const defaultI18n: Record<string, I18nTexts> = {
  'zh-CN': {
    welcome: '你好，我是你的智能导购助手。想找点什么？',
    placeholder: '请输入您想要的商品...',
    send: '发送',
    retry: '重试',
    clear: '清空对话',
    minimize: '最小化',
    close: '关闭',
    typing: '正在输入...',
    networkError: '网络连接失败，请检查网络设置',
    serverError: '服务暂时不可用，请稍后重试',
    suggestions: [
      '推荐一款手机',
      '有什么新款包包吗？',
      '性价比高的耳机',
      '适合运动的鞋子'
    ]
  },
  'en-US': {
    welcome: 'Hello! I\'m your smart shopping assistant. What can I help you find?',
    placeholder: 'Tell me what you\'re looking for...',
    send: 'Send',
    retry: 'Retry',
    clear: 'Clear Chat',
    minimize: 'Minimize',
    close: 'Close',
    typing: 'Typing...',
    networkError: 'Network connection failed, please check your settings',
    serverError: 'Service temporarily unavailable, please try again later',
    suggestions: [
      'Recommend a smartphone',
      'Any new handbags?',
      'Best value headphones',
      'Sports shoes'
    ]
  }
}

// 默认配置
const defaultConfig: IntelliRecsConfig = {
  tenantId: '',
  apiBase: 'https://api.intellirecs.ai',
  theme: {
    primary: '#2563eb',
    corner: '16px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: '14px'
  },
  welcome: '',
  lang: 'zh-CN',
  productLinkMode: 'new_tab',
  enableHistory: true,
  maxHistoryLength: 20,
  debug: false,
  requestTimeout: 30000,
  retryAttempts: 3
}

/**
 * 应用默认配置
 */
export function applyDefaultConfig(userConfig: Partial<IntelliRecsConfig>): IntelliRecsConfig {
  const config = { ...defaultConfig, ...userConfig }
  
  // 合并主题配置
  config.theme = { ...defaultConfig.theme, ...userConfig.theme }
  
  // 设置默认国际化文案
  if (!config.welcome) {
    const langTexts = defaultI18n[config.lang] || defaultI18n['zh-CN']
    config.welcome = langTexts.welcome
  }
  
  // 合并国际化文案
  const defaultLangTexts = defaultI18n[config.lang] || defaultI18n['zh-CN']
  config.i18n = { ...defaultLangTexts, ...userConfig.i18n }
  
  return config
}

/**
 * 生成会话ID
 */
export function generateSessionId(): string {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 15)
  return `session_${timestamp}_${random}`
}

/**
 * 生成消息ID
 */
export function generateMessageId(): string {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 15)
  return `msg_${timestamp}_${random}`
}

/**
 * 验证配置
 */
export function validateConfig(config: Partial<IntelliRecsConfig>): string[] {
  const errors: string[] = []
  
  if (!config.tenantId) {
    errors.push('tenantId is required')
  }
  
  if (!config.apiBase) {
    errors.push('apiBase is required')
  } else if (!isValidUrl(config.apiBase)) {
    errors.push('apiBase must be a valid URL')
  }
  
  if (config.maxHistoryLength && (config.maxHistoryLength < 1 || config.maxHistoryLength > 100)) {
    errors.push('maxHistoryLength must be between 1 and 100')
  }
  
  if (config.requestTimeout && (config.requestTimeout < 1000 || config.requestTimeout > 120000)) {
    errors.push('requestTimeout must be between 1000ms and 120000ms')
  }
  
  return errors
}

/**
 * 检查是否为有效URL
 */
function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

/**
 * 深度合并对象
 */
export function deepMerge<T>(target: T, source: Partial<T>): T {
  const result = { ...target }
  
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      const sourceValue = source[key]
      const targetValue = result[key]
      
      if (isObject(sourceValue) && isObject(targetValue)) {
        result[key] = deepMerge(targetValue, sourceValue)
      } else {
        result[key] = sourceValue as T[Extract<keyof T, string>]
      }
    }
  }
  
  return result
}

/**
 * 检查是否为对象
 */
function isObject(item: any): item is Record<string, any> {
  return item && typeof item === 'object' && !Array.isArray(item)
}

/**
 * 获取安全的CSS值
 */
export function getSafeCSSValue(value: string): string {
  // 简单的CSS安全性检查
  const dangerousPatterns = [
    /javascript:/i,
    /expression\(/i,
    /import\s+/i,
    /@import/i,
    /behavior:/i
  ]
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(value)) {
      console.warn('[IntelliRecsAI] Potentially dangerous CSS value detected:', value)
      return ''
    }
  }
  
  return value
}
