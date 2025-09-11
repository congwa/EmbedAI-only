// API模块类型声明
declare module '@/apis' {
  export const adminApi: {
    getUsers: () => Promise<any[]>
    getOperationLogs: (params?: any) => Promise<any[]>
    getSystemStats: () => Promise<any>
  }
  
  export const adminDatabaseApi: {
    getDatabases: () => Promise<any[]>
    createDatabase: (data: any) => Promise<any>
    deleteDatabase: (id: string) => Promise<any>
    rebuildIndex: (id: string) => Promise<any>
  }
}

// 图谱API模块类型声明
declare module '@/apis/graph_api' {
  export const lightragApi: {
    getSubgraph: (params: any) => Promise<any>
    getDatabases: () => Promise<any>
    getLabels: (db_id: string) => Promise<any>
    getStats: (db_id: string) => Promise<any>
  }
  
  export const neo4jApi: {
    getSampleNodes: (kgdb_name?: string, num?: number) => Promise<any>
    queryNode: (entity_name: string) => Promise<any>
    addEntities: (file_path: string, kgdb_name?: string) => Promise<any>
    indexEntities: (kgdb_name?: string) => Promise<any>
    getInfo: () => Promise<any>
  }
  
  export const getEntityTypeColor: (entityType: string) => string
  export const calculateEdgeWidth: (weight: number, minWeight?: number, maxWeight?: number) => number
}
