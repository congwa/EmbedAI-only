import { apiAdminGet, apiAdminPost, apiAdminDelete } from './base'

/**
 * 管理员API模块
 * 包含用户管理、权限管理、操作日志、系统统计等功能
 */

// =============================================================================
// === 用户管理API ===
// =============================================================================

export const userApi = {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @returns {Promise} - 用户列表
   */
  getUsers: async (params = {}) => {
    const { skip = 0, limit = 100 } = params
    return apiAdminGet(`/api/admin/users?skip=${skip}&limit=${limit}`)
  }
}

// =============================================================================
// === 操作日志API ===
// =============================================================================

export const logApi = {
  /**
   * 获取操作日志
   * @param {Object} params - 查询参数
   * @returns {Promise} - 操作日志列表
   */
  getLogs: async (params = {}) => {
    const { skip = 0, limit = 100, user_id, operation } = params
    let url = `/api/admin/logs?skip=${skip}&limit=${limit}`
    
    if (user_id) {
      url += `&user_id=${user_id}`
    }
    if (operation) {
      url += `&operation=${encodeURIComponent(operation)}`
    }
    
    return apiAdminGet(url)
  }
}

// =============================================================================
// === 数据库管理API ===
// =============================================================================

export const adminDatabaseApi = {
  /**
   * 获取数据库列表
   * @param {Object} params - 查询参数
   * @returns {Promise} - 数据库列表
   */
  getDatabases: async (params = {}) => {
    const { skip = 0, limit = 100 } = params
    return apiAdminGet(`/api/admin/databases?skip=${skip}&limit=${limit}`)
  },

  /**
   * 创建数据库
   * @param {Object} databaseData - 数据库数据
   * @returns {Promise} - 创建结果
   */
  createDatabase: async (databaseData) => {
    return apiAdminPost('/api/admin/databases', databaseData)
  },

  /**
   * 获取数据库详情
   * @param {string} dbId - 数据库ID
   * @returns {Promise} - 数据库详情
   */
  getDatabaseDetail: async (dbId) => {
    return apiAdminGet(`/api/admin/databases/${dbId}`)
  },

  /**
   * 删除数据库
   * @param {string} dbId - 数据库ID
   * @returns {Promise} - 删除结果
   */
  deleteDatabase: async (dbId) => {
    return apiAdminDelete(`/api/admin/databases/${dbId}`)
  }
}

// =============================================================================
// === 系统统计API ===
// =============================================================================

export const statsApi = {
  /**
   * 获取系统统计信息
   * @returns {Promise} - 系统统计数据
   */
  getSystemStats: async () => {
    return apiAdminGet('/api/admin/stats')
  }
}
