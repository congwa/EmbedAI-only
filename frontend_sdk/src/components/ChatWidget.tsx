/**
 * 聊天窗主组件
 */
import React, { useState, useEffect, useCallback } from 'react'
import { IntelliRecsConfig, WidgetState, ChatMessage, ChatResponse } from '../types'
import { generateSessionId, generateMessageId } from '../utils/config'
import { FloatingButton } from './FloatingButton'
import { ChatWindow } from './ChatWindow'
import { apiService } from '../services/api'

import '../styles/widget.css'

interface ChatWidgetProps {
  config: IntelliRecsConfig
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ config }) => {
  const [state, setState] = useState<WidgetState>({
    isOpen: false,
    isMinimized: false,
    isLoading: false,
    messages: [],
    currentInput: '',
    sessionId: generateSessionId()
  })

  // 初始化欢迎消息
  useEffect(() => {
    if (config.welcome) {
      const welcomeMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        content: config.welcome,
        timestamp: Date.now()
      }
      setState(prev => ({
        ...prev,
        messages: [welcomeMessage]
      }))
    }
  }, [config.welcome])

  // 监听全局事件
  useEffect(() => {
    const handleOpen = () => setState(prev => ({ ...prev, isOpen: true }))
    const handleClose = () => setState(prev => ({ ...prev, isOpen: false }))

    document.addEventListener('intellirecs:open', handleOpen)
    document.addEventListener('intellirecs:close', handleClose)

    return () => {
      document.removeEventListener('intellirecs:open', handleOpen)
      document.removeEventListener('intellirecs:close', handleClose)
    }
  }, [])

  // 打开聊天窗
  const handleOpen = useCallback(() => {
    setState(prev => ({ ...prev, isOpen: true }))
    config.callbacks?.onOpen?.()
  }, [config.callbacks])

  // 关闭聊天窗
  const handleClose = useCallback(() => {
    setState(prev => ({ ...prev, isOpen: false }))
    config.callbacks?.onClose?.()
  }, [config.callbacks])

  // 最小化聊天窗
  const handleMinimize = useCallback(() => {
    setState(prev => ({ ...prev, isMinimized: true }))
  }, [])

  // 发送消息
  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim() || state.isLoading) return

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      role: 'user',
      content: message.trim(),
      timestamp: Date.now()
    }

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      currentInput: '',
      isLoading: true
    }))

    config.callbacks?.onSend?.(message)

    try {
      // 调用API
      const response: ChatResponse = await apiService.sendMessage({
        tenantId: config.tenantId,
        sessionId: state.sessionId,
        message: message.trim(),
        history: state.messages.slice(-config.maxHistoryLength || -10),
        topK: 10,
        lang: config.lang
      })

      if (response.success) {
        // 添加AI回复
        const aiMessage: ChatMessage = {
          id: generateMessageId(),
          role: 'assistant',
          content: response.reply,
          timestamp: Date.now(),
          products: response.products
        }

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, aiMessage],
          isLoading: false
        }))

        config.callbacks?.onReceive?.(response)
      } else {
        throw new Error('API请求失败')
      }
    } catch (error) {
      console.error('[ChatWidget] 发送消息失败:', error)
      
      // 添加错误消息
      const errorMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        content: config.i18n?.serverError || '抱歉，发送消息时遇到了问题，请稍后重试。',
        timestamp: Date.now()
      }

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false
      }))

      config.callbacks?.onError?.(error as Error)
    }
  }, [state, config])

  // 清空对话
  const handleClearChat = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: config.welcome ? [{
        id: generateMessageId(),
        role: 'assistant',
        content: config.welcome,
        timestamp: Date.now()
      }] : [],
      sessionId: generateSessionId()
    }))
  }, [config.welcome])

  // 商品点击处理
  const handleProductClick = useCallback((product: any) => {
    config.callbacks?.onProductClick?.(product)
    
    // 打开商品链接
    if (product.productUrl) {
      const target = config.productLinkMode === 'new_tab' ? '_blank' : '_self'
      window.open(product.productUrl, target)
    }
  }, [config])

  // 应用主题样式
  const themeStyle = {
    '--primary-color': config.theme.primary,
    '--border-radius': config.theme.corner,
    '--font-family': config.theme.fontFamily,
    '--font-size': config.theme.fontSize
  } as React.CSSProperties

  return (
    <div className="intellirecs-widget" style={themeStyle}>
      {/* 悬浮按钮 */}
      <FloatingButton
        isOpen={state.isOpen}
        unreadCount={0}
        onClick={handleOpen}
        config={config}
      />

      {/* 聊天窗 */}
      {state.isOpen && (
        <ChatWindow
          state={state}
          config={config}
          onClose={handleClose}
          onMinimize={handleMinimize}
          onSendMessage={handleSendMessage}
          onClearChat={handleClearChat}
          onProductClick={handleProductClick}
        />
      )}
    </div>
  )
}
