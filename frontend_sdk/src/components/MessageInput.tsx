/**
 * 消息输入组件
 */
import React, { useState, useRef, KeyboardEvent } from 'react'
import { IntelliRecsConfig } from '../types'

interface MessageInputProps {
  value: string
  isLoading: boolean
  config: IntelliRecsConfig
  onSend: (message: string) => void
}

export const MessageInput: React.FC<MessageInputProps> = ({
  value,
  isLoading,
  config,
  onSend
}) => {
  const [inputValue, setInputValue] = useState(value)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 处理发送
  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSend(inputValue.trim())
      setInputValue('')
    }
  }

  // 处理键盘事件
  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 自动调整输入框高度
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target
    setInputValue(textarea.value)
    
    // 重置高度再计算
    textarea.style.height = 'auto'
    const scrollHeight = textarea.scrollHeight
    const maxHeight = 120 // 最大高度
    textarea.style.height = Math.min(scrollHeight, maxHeight) + 'px'
  }

  return (
    <div className="intellirecs-input-container">
      {/* 建议快捷问题 */}
      {inputValue === '' && config.i18n?.suggestions && (
        <div className="intellirecs-quick-suggestions">
          {config.i18n.suggestions.slice(0, 3).map((suggestion, index) => (
            <button
              key={index}
              className="intellirecs-quick-suggestion"
              onClick={() => setInputValue(suggestion)}
              disabled={isLoading}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="intellirecs-input-wrapper">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={config.i18n?.placeholder || '请输入您想要的商品...'}
          className="intellirecs-textarea"
          rows={1}
          disabled={isLoading}
          maxLength={1000}
        />
        
        <button
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading}
          className="intellirecs-send-btn"
          title={config.i18n?.send}
        >
          {isLoading ? (
            <svg width="20" height="20" viewBox="0 0 24 24" className="intellirecs-loading-icon">
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                strokeDasharray="31.416"
                strokeDashoffset="31.416"
              >
                <animate
                  attributeName="stroke-dasharray"
                  dur="2s"
                  values="0 31.416;15.708 15.708;0 31.416;0 31.416"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="stroke-dashoffset"
                  dur="2s"
                  values="0;-15.708;-31.416;-31.416"
                  repeatCount="indefinite"
                />
              </circle>
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </button>
      </div>

      {/* 字数统计 */}
      <div className="intellirecs-input-footer">
        <div className="intellirecs-char-count">
          {inputValue.length}/1000
        </div>
        <div className="intellirecs-input-hint">
          回车发送，Shift+回车换行
        </div>
      </div>
    </div>
  )
}
