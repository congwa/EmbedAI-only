/**
 * 加载指示器组件
 */
import React from 'react'

interface LoadingIndicatorProps {
  text?: string
  size?: 'small' | 'medium' | 'large'
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  text = '加载中...',
  size = 'medium'
}) => {
  return (
    <div className={`intellirecs-loading intellirecs-loading-${size}`}>
      <div className="intellirecs-loading-content">
        <div className="intellirecs-loading-spinner">
          <div className="intellirecs-dot intellirecs-dot-1"></div>
          <div className="intellirecs-dot intellirecs-dot-2"></div>
          <div className="intellirecs-dot intellirecs-dot-3"></div>
        </div>
        {text && <div className="intellirecs-loading-text">{text}</div>}
      </div>
    </div>
  )
}
