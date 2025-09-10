/**
 * 悬浮按钮组件
 */
import React from 'react'
import { IntelliRecsConfig } from '../types'

interface FloatingButtonProps {
  isOpen: boolean
  unreadCount: number
  onClick: () => void
  config: IntelliRecsConfig
}

export const FloatingButton: React.FC<FloatingButtonProps> = ({
  isOpen,
  unreadCount,
  onClick,
  config
}) => {
  return (
    <button
      className={`intellirecs-floating-btn ${isOpen ? 'open' : ''}`}
      onClick={onClick}
      aria-label={isOpen ? config.i18n?.close : "打开智能助手"}
    >
      {/* 未读消息气泡 */}
      {unreadCount > 0 && !isOpen && (
        <span className="intellirecs-unread-badge">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {/* 按钮图标 */}
      <div className="intellirecs-btn-icon">
        {isOpen ? (
          // 关闭图标
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          // 聊天图标
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
      
      {/* 悬停提示 */}
      {!isOpen && (
        <div className="intellirecs-tooltip">
          {config.i18n?.welcome?.split('，')[0] || '智能助手'}
        </div>
      )}
    </button>
  )
}
