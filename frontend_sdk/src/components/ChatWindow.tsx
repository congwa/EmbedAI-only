/**
 * 聊天窗组件
 */
import React from 'react'
import { IntelliRecsConfig, WidgetState } from '../types'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

interface ChatWindowProps {
  state: WidgetState
  config: IntelliRecsConfig
  onClose: () => void
  onMinimize: () => void
  onSendMessage: (message: string) => void
  onClearChat: () => void
  onProductClick: (product: any) => void
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  state,
  config,
  onClose,
  onMinimize,
  onSendMessage,
  onClearChat,
  onProductClick
}) => {
  return (
    <div className="intellirecs-chat-window">
      {/* 窗口头部 */}
      <div className="intellirecs-chat-header">
        <div className="intellirecs-header-info">
          <div className="intellirecs-avatar">
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
          </div>
          <div className="intellirecs-header-text">
            <div className="intellirecs-title">智能导购助手</div>
            <div className="intellirecs-status">
              <span className="intellirecs-status-dot"></span>
              在线
            </div>
          </div>
        </div>
        
        <div className="intellirecs-header-actions">
          {/* 清空对话 */}
          <button
            className="intellirecs-action-btn"
            onClick={onClearChat}
            title={config.i18n?.clear}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zM10 11v6M14 11v6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          
          {/* 最小化 */}
          <button
            className="intellirecs-action-btn"
            onClick={onMinimize}
            title={config.i18n?.minimize}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M6 9l6 6 6-6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          
          {/* 关闭 */}
          <button
            className="intellirecs-action-btn"
            onClick={onClose}
            title={config.i18n?.close}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M18 6L6 18M6 6l12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="intellirecs-chat-content">
        <MessageList
          messages={state.messages}
          isLoading={state.isLoading}
          config={config}
          onProductClick={onProductClick}
        />
      </div>

      {/* 输入区域 */}
      <div className="intellirecs-chat-footer">
        <MessageInput
          value={state.currentInput}
          isLoading={state.isLoading}
          config={config}
          onSend={onSendMessage}
        />
      </div>
    </div>
  )
}
