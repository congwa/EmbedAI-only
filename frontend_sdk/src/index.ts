/**
 * EmbedAI 聊天窗SDK 主入口
 */
import { createRoot } from 'react-dom/client'
import { ChatWidget } from './components/ChatWidget'
import { IntelliRecsConfig } from './types'
import { applyDefaultConfig } from './utils/config'

declare global {
  interface Window {
    IntelliRecsAI: {
      init: (config: Partial<IntelliRecsConfig>) => void
      destroy: () => void
      open: () => void
      close: () => void
    }
  }
}

let widgetInstance: any = null
let widgetRoot: any = null

/**
 * 初始化聊天窗SDK
 */
function init(userConfig: Partial<IntelliRecsConfig>) {
  try {
    // 合并默认配置
    const config = applyDefaultConfig(userConfig)
    
    // 检查必需参数
    if (!config.apiBase) {
      throw new Error('apiBase is required')
    }
    
    // 销毁现有实例
    if (widgetInstance) {
      destroy()
    }
    
    // 创建容器元素
    const containerId = `intellirecs-widget-${Date.now()}`
    let container = document.getElementById(containerId)
    
    if (!container) {
      container = document.createElement('div')
      container.id = containerId
      container.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      `
      document.body.appendChild(container)
    }
    
    // 创建React根节点
    widgetRoot = createRoot(container)
    
    // 渲染聊天窗组件
    widgetRoot.render(ChatWidget({ config }))
    
    widgetInstance = {
      config,
      container,
      root: widgetRoot
    }
    
    console.log('[IntelliRecsAI] 聊天窗初始化成功', config)
    
  } catch (error) {
    console.error('[IntelliRecsAI] 初始化失败:', error)
  }
}

/**
 * 销毁聊天窗
 */
function destroy() {
  if (widgetRoot) {
    widgetRoot.unmount()
    widgetRoot = null
  }
  
  if (widgetInstance?.container) {
    widgetInstance.container.remove()
  }
  
  widgetInstance = null
  console.log('[IntelliRecsAI] 聊天窗已销毁')
}

/**
 * 打开聊天窗
 */
function open() {
  if (widgetInstance) {
    // 触发打开事件
    const event = new CustomEvent('intellirecs:open')
    document.dispatchEvent(event)
  }
}

/**
 * 关闭聊天窗
 */
function close() {
  if (widgetInstance) {
    // 触发关闭事件
    const event = new CustomEvent('intellirecs:close')
    document.dispatchEvent(event)
  }
}

// 暴露全局API
const IntelliRecsAI = {
  init,
  destroy,
  open,
  close
}

// 挂载到window对象
if (typeof window !== 'undefined') {
  window.IntelliRecsAI = IntelliRecsAI
}

export { IntelliRecsAI, init, destroy, open, close }
export * from './types'
export * from './components'
