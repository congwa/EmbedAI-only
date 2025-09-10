/**
 * 消息列表组件
 */
import React, { useEffect, useRef } from 'react'
import { ChatMessage, IntelliRecsConfig } from '../types'
import { ProductCard } from './ProductCard'
import { LoadingIndicator } from './LoadingIndicator'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading: boolean
  config: IntelliRecsConfig
  onProductClick: (product: any) => void
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  config,
  onProductClick
}) => {
  const scrollRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="intellirecs-message-list" ref={scrollRef}>
      {messages.length === 0 && !isLoading && (
        <div className="intellirecs-empty-state">
          <div className="intellirecs-empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8 10h8M8 14h4"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="intellirecs-empty-text">
            {config.welcome || '开始对话，寻找您想要的商品'}
          </div>
          
          {/* 建议问题 */}
          {config.i18n?.suggestions && config.i18n.suggestions.length > 0 && (
            <div className="intellirecs-suggestions">
              <div className="intellirecs-suggestions-title">试试问我：</div>
              <div className="intellirecs-suggestions-list">
                {config.i18n.suggestions.slice(0, 4).map((suggestion, index) => (
                  <button
                    key={index}
                    className="intellirecs-suggestion-item"
                    onClick={() => {/* 这里需要传递消息发送函数 */}}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`intellirecs-message ${message.role === 'user' ? 'user' : 'assistant'}`}
        >
          {/* 消息头像 */}
          <div className="intellirecs-message-avatar">
            {message.role === 'user' ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>

          {/* 消息内容 */}
          <div className="intellirecs-message-content">
            <div className="intellirecs-message-text">
              {message.content}
            </div>
            
            {/* 商品推荐卡片 */}
            {message.products && message.products.length > 0 && (
              <div className="intellirecs-products-grid">
                {message.products.map((product, index) => (
                  <ProductCard
                    key={`${product.sku}-${index}`}
                    product={product}
                    onClick={() => onProductClick(product)}
                    config={config}
                  />
                ))}
              </div>
            )}
            
            {/* 消息时间 */}
            <div className="intellirecs-message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}

      {/* 加载指示器 */}
      {isLoading && (
        <div className="intellirecs-message assistant">
          <div className="intellirecs-message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="intellirecs-message-content">
            <LoadingIndicator text={config.i18n?.typing || '正在思考...'} />
          </div>
        </div>
      )}
    </div>
  )
}
