# 图片收藏管理系统 - 技术栈文档

## 1. 开发环境

### 1.1 基础环境
- Python 3.x
- PyCharm 2022 (社区版)
- Git 版本控制
- Windows 操作系统

### 1.2 虚拟环境
- venv (Python虚拟环境)
- 依赖管理：requirements.txt

## 2. 后端技术栈

### 2.1 Web框架
- Flask 2.x
  - 轻量级Web框架
  - 路由系统
  - 模板引擎集成
  - 静态文件服务

### 2.2 数据库
- SQL Server
  - 关系型数据库
  - 事务支持
  - 数据完整性约束
  - 索引优化

### 2.3 数据库驱动
- pyodbc
  - SQL Server连接
  - 参数化查询
  - 事务管理

### 2.4 模板引擎
- Jinja2
  - HTML模板渲染
  - 模板继承
  - 宏定义
  - 过滤器

## 3. 前端技术栈

### 3.1 基础技术
- HTML5
- CSS3
- JavaScript (ES6+)

### 3.2 样式框架
- Bootstrap
  - 响应式布局
  - 组件库
  - 栅格系统

### 3.3 前端库
- jQuery
  - DOM操作
  - AJAX请求
  - 事件处理

## 4. 项目依赖

### 4.1 核心依赖
```python
Flask==2.x.x
pyodbc==4.x.x
Werkzeug==2.x.x
Jinja2==3.x.x
```

### 4.2 开发依赖
```python
python-dotenv==0.x.x
Flask-SQLAlchemy==3.x.x
Flask-Login==0.x.x
```

### 4.3 工具依赖
```python
Pillow==9.x.x  # 图片处理
python-dateutil==2.x.x  # 日期处理
```

## 5. 开发工具

### 5.1 IDE配置
- PyCharm 2022
  - Python解释器配置
  - 代码风格设置
  - 调试配置
  - 版本控制集成

### 5.2 代码质量工具
- pylint
  - 代码检查
  - 风格检查
  - 错误检测

### 5.3 版本控制
- Git
  - 分支管理
  - 代码提交
  - 版本回滚

## 6. 部署环境

### 6.1 服务器要求
- Windows Server 2019+
- Python 3.x
- SQL Server 2019+
- IIS 10+

### 6.2 部署工具
- Gunicorn
  - WSGI服务器
  - 进程管理
  - 负载均衡

### 6.3 监控工具
- Flask-Debug-toolbar
  - 调试信息
  - 性能分析
  - SQL查询监控

## 7. 安全工具

### 7.1 认证工具
- Flask-Login
  - 用户会话管理
  - 登录状态维护
  - 权限控制

### 7.2 安全中间件
- Flask-WTF
  - CSRF保护
  - 表单验证
  - 安全令牌

### 7.3 加密工具
- Werkzeug
  - 密码哈希
  - 会话加密
  - 安全Cookie 