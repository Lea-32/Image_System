# 图片收藏管理系统 - 文件结构文档

## 1. 项目根目录结构

```
Img_System/
├── app.py                 # 主应用入口文件
├── SQL.py                 # 数据库操作和配置
├── requirements.txt       # 项目依赖文件
├── 说明文档.txt           # 项目说明文档
├── routes/               # 路由模块目录
├── templates/            # HTML模板目录
├── static/              # 静态资源目录
├── venv/                # Python虚拟环境
└── .git/                # Git版本控制目录
```

## 2. 路由模块 (routes/)

```
routes/
├── __init__.py          # 路由包初始化文件
├── login.py             # 用户认证相关路由
├── main.py              # 主页面路由
├── upload.py            # 图片上传路由
├── show_img.py          # 图片展示路由
├── favorite.py          # 收藏功能路由
├── comment.py           # 评论系统路由
├── search.py            # 搜索功能路由
├── delete_img.py        # 图片删除路由
├── statistics.py        # 统计功能路由
└── db_config.py         # 数据库配置文件
```

## 3. 模板目录 (templates/)

```
templates/
├── base.html            # 基础模板
├── login.html           # 登录页面
├── register.html        # 注册页面
├── main.html           # 主页面
├── upload.html         # 上传页面
├── show_img.html       # 图片展示页面
├── favorite.html       # 收藏列表页面
├── comment.html        # 评论页面
└── search.html         # 搜索结果页面
```

## 4. 静态资源目录 (static/)

```
static/
├── css/                # CSS样式文件
│   ├── main.css       # 主样式文件
│   ├── login.css      # 登录页面样式
│   └── upload.css     # 上传页面样式
├── js/                 # JavaScript文件
│   ├── main.js        # 主脚本文件
│   ├── upload.js      # 上传功能脚本
│   └── search.js      # 搜索功能脚本
├── images/            # 图片资源
│   ├── logo.png       # 网站logo
│   └── icons/         # 图标文件
└── uploads/           # 用户上传图片存储目录
```

## 5. 配置文件

### 5.1 数据库配置 (db_config.py)
```python
# 数据库连接配置
def config(user_type):
    if user_type == 'root':
        return 'DRIVER={SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...'
    else:
        return 'DRIVER={SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...'
```

### 5.2 应用配置 (app.py)
```python
app = Flask(__name__)
app.secret_key = 'key'  # 会话密钥
```

## 6. 主要文件说明

### 6.1 app.py
- 应用入口文件
- 路由注册
- 应用配置
- 启动服务器

### 6.2 SQL.py
- 数据库连接配置
- SQL查询执行
- 数据库操作封装
- 事务管理

### 6.3 routes/*.py
- 路由处理函数
- 业务逻辑实现
- 数据验证
- 响应处理

### 6.4 templates/*.html
- 页面模板
- 动态内容渲染
- 用户界面布局
- 交互元素

### 6.5 static/*
- 静态资源文件
- 样式定义
- 客户端脚本
- 图片资源

## 7. 文件命名规范

### 7.1 Python文件
- 使用小写字母
- 单词间用下划线连接
- 模块名应简短且具有描述性
- 避免使用特殊字符

### 7.2 模板文件
- 使用小写字母
- 单词间用下划线连接
- 使用.html扩展名
- 名称应反映页面功能

### 7.3 静态文件
- CSS文件：功能名.css
- JS文件：功能名.js
- 图片文件：描述性名称.png/jpg
- 图标文件：icon_功能名.png

## 8. 文件组织原则

### 8.1 模块化
- 相关功能放在同一目录
- 清晰的目录层次结构
- 避免循环依赖

### 8.2 可维护性
- 文件职责单一
- 合理的文件大小
- 清晰的命名规范

### 8.3 安全性
- 敏感配置单独管理
- 静态资源访问控制
- 上传文件安全处理 