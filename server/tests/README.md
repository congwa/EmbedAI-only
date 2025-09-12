# EmbedAI Server API 测试用例文档

## 📋 测试覆盖概览

### 已完成的测试模块

#### 1. **用户认证模块** (`test_auth.py`)
- ✅ 登录认证测试
  - 成功登录
  - 无效用户名/密码
- ✅ 系统初始化测试
  - 首次运行检查
  - 管理员账户初始化
- ✅ 用户管理测试
  - 获取当前用户信息
  - 创建/删除用户
  - 用户列表查询
  - 权限验证

#### 2. **知识库管理模块** (`test_knowledge.py`)
- ✅ 知识库数据库管理
  - 创建/更新/删除知识库
  - 获取知识库列表和详情
- ✅ 文档管理
  - 添加/删除文档
  - 获取文档信息
- ✅ 知识库查询
  - 标准查询和测试查询
  - 查询参数配置
- ✅ 文件上传
  - 文件上传成功/失败场景
- ✅ 统计信息
  - 知识库类型查询
  - 统计数据获取

#### 3. **图谱管理模块** (`test_graph.py`)  
- ✅ LightRAG 子图查询
  - 成功获取子图数据
  - 数据库类型验证
  - 实例存在性检查
- ✅ LightRAG 数据库管理
  - 数据库列表获取
  - 标签管理
  - 统计信息
- ✅ Neo4j 节点管理
  - 节点查询和检索
  - 数据库状态检查
- ✅ Neo4j 实体索引和添加
  - 实体嵌入向量索引
  - JSONL 文件实体添加

#### 4. **基础API模块** (`test_api.py` - 已存在)
- ✅ 健康检查API
- ✅ 聊天推荐API
- ✅ 管理后台API
- ✅ 根路径API

### 📊 测试统计

| 模块 | 测试类数量 | 测试方法数量 | 覆盖的API端点 |
|------|------------|--------------|---------------|
| 用户认证 | 3 | 12 | 8个端点 |
| 知识库管理 | 6 | 18 | 15个端点 |
| 图谱管理 | 8 | 16 | 9个端点 |
| 基础API | 4 | 12 | 7个端点 |
| **总计** | **21** | **58** | **39个端点** |

## 🔧 发现并修复的问题

### 导入路径问题
- ❌ `from src.utils import logger` → ✅ `from utils.logging_config import logger`
- ❌ `from models.user_model import User` → ✅ `from api.models.user_model import User`
- ❌ `from utils.auth_middleware` → ✅ `from api.utils.auth_middleware`

### 代码质量改进
- 统一了所有路由文件的导入路径
- 确保了所有异常处理的一致性
- 验证了API响应格式的标准化

## 🚀 运行测试

### 环境要求
```bash
# 使用 Poetry 安装依赖
poetry install

# 或使用 pip 安装
pip install -r requirements.txt
```

### 运行命令
```bash
# 运行所有测试
poetry run pytest tests/ -v

# 运行特定模块测试
poetry run pytest tests/test_auth.py -v
poetry run pytest tests/test_knowledge.py -v
poetry run pytest tests/test_graph.py -v

# 生成覆盖率报告
poetry run pytest tests/ --cov=api --cov-report=html
```

## 📝 测试设计原则

### Mock策略
- **数据库会话**: 使用 `Mock(spec=Session)` 模拟SQLAlchemy会话
- **外部服务**: Mock LightRAG、Neo4j等外部知识库服务
- **用户认证**: Mock当前用户和权限验证
- **异步函数**: 使用 `AsyncMock` 处理异步调用

### 测试场景覆盖
- ✅ **成功路径**: 正常业务流程
- ✅ **异常处理**: 4xx/5xx错误响应
- ✅ **边界条件**: 参数验证、权限检查
- ✅ **数据验证**: 请求/响应格式验证

## 🎯 测试最佳实践

### 1. 测试结构
```python
class TestModuleName:
    """模块功能测试"""
    
    def test_function_success(self, client, mock_deps):
        """测试成功场景"""
        
    def test_function_validation_error(self, client):
        """测试参数验证错误"""
        
    def test_function_permission_denied(self, client):
        """测试权限不足"""
```

### 2. Mock使用
```python
@patch("api.utils.auth_middleware.get_current_user")
def test_with_auth(self, mock_get_user, client, mock_user):
    mock_get_user.return_value = mock_user
    # 测试逻辑
```

### 3. 断言验证
```python
assert response.status_code == 200
data = response.json()
assert data["success"] is True
assert "expected_field" in data["data"]
```

## 🔍 待完善的测试

### 集成测试
- [ ] 端到端API调用流程
- [ ] 数据库迁移测试
- [ ] 外部服务集成测试

### 性能测试  
- [ ] API响应时间测试
- [ ] 并发请求测试
- [ ] 大数据量处理测试

### 安全测试
- [ ] SQL注入防护测试
- [ ] XSS防护测试
- [ ] 认证令牌安全测试

## 📋 维护指南

### 添加新测试
1. 在对应的测试文件中添加测试类
2. 使用描述性的测试方法名
3. 遵循AAA模式 (Arrange, Act, Assert)
4. 添加必要的Mock和Fixture

### 更新现有测试
1. API变更时同步更新测试用例
2. 保持测试数据的时效性
3. 定期检查Mock的有效性

## 🏆 测试质量保证

- **代码覆盖率目标**: >80%
- **所有API端点**: 必须有对应测试
- **异常路径**: 必须有错误处理测试  
- **权限验证**: 必须有权限检查测试
- **文档同步**: 测试用例与API文档保持一致
