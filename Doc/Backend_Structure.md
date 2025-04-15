# 图片收藏管理系统 - 后端结构文档

## 1. 系统架构

### 1.1 技术栈
- Web框架：Flask
- 数据库：SQL Server
- 模板引擎：Jinja2
- 静态文件：Flask静态文件服务

### 1.2 目录结构
```
Img_System/
├── app.py              # 主应用入口
├── routes/             # 路由模块
│   ├── login.py        # 用户认证
│   ├── main.py         # 主页面
│   ├── upload.py       # 图片上传
│   ├── show_img.py     # 图片展示
│   ├── favorite.py     # 收藏功能
│   ├── comment.py      # 评论系统
│   ├── search.py       # 搜索功能
│   └── delete_img.py   # 图片删除
├── templates/          # HTML模板
├── static/            # 静态资源
└── SQL.py             # 数据库操作
```

## 2. 数据库设计

### 2.1 用户表 (Users)
```sql
CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    create_time DATETIME
);
```

### 2.2 图片表 (Image)
```sql
CREATE TABLE Image (
    img_id INT PRIMARY KEY,
    user_id INT,
    title VARCHAR(100),
    description TEXT,
    upload_time DATETIME,
    file_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
```

### 2.3 评论表 (Comment)
```sql
CREATE TABLE Comment (
    comment_id INT PRIMARY KEY,
    img_id INT,
    user_id INT,
    content TEXT,
    create_time DATETIME,
    FOREIGN KEY (img_id) REFERENCES Image(img_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
```

### 2.4 标签表 (Tag)
```sql
CREATE TABLE Tag (
    tag_id INT PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE
);
```

### 2.5 标签索引表 (Tag_index)
```sql
CREATE TABLE Tag_index (
    img_id INT,
    tag_id INT,
    PRIMARY KEY (img_id, tag_id),
    FOREIGN KEY (img_id) REFERENCES Image(img_id),
    FOREIGN KEY (tag_id) REFERENCES Tag(tag_id)
);
```

### 2.6 收藏表 (Favorite)
```sql
CREATE TABLE Favorite (
    favorite_id INT PRIMARY KEY,
    user_id INT,
    img_id INT,
    create_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (img_id) REFERENCES Image(img_id)
);
```

## 3. API接口设计

### 3.1 用户认证接口
```
POST /register
- 功能：用户注册
- 参数：username, password
- 返回：注册结果

POST /login
- 功能：用户登录
- 参数：username, password
- 返回：登录状态

GET /logout
- 功能：用户登出
- 返回：登出结果
```

### 3.2 图片管理接口
```
POST /upload
- 功能：上传图片
- 参数：file, title, description
- 返回：上传结果

GET /image/<img_id>
- 功能：获取图片详情
- 参数：img_id
- 返回：图片信息

DELETE /image/<img_id>
- 功能：删除图片
- 参数：img_id
- 返回：删除结果
```

### 3.3 收藏功能接口
```
POST /favorite
- 功能：收藏图片
- 参数：img_id
- 返回：收藏结果

GET /favorites
- 功能：获取收藏列表
- 返回：收藏图片列表

DELETE /favorite/<img_id>
- 功能：取消收藏
- 参数：img_id
- 返回：取消结果
```

### 3.4 评论系统接口
```
POST /comment
- 功能：发表评论
- 参数：img_id, content
- 返回：评论结果

GET /comments/<img_id>
- 功能：获取图片评论
- 参数：img_id
- 返回：评论列表
```

### 3.5 标签管理接口
```
POST /tag
- 功能：添加标签
- 参数：img_id, tag_name
- 返回：添加结果

GET /tags/<img_id>
- 功能：获取图片标签
- 参数：img_id
- 返回：标签列表
```

### 3.6 搜索接口
```
GET /search
- 功能：搜索图片
- 参数：keyword, tags
- 返回：搜索结果
```

## 4. 安全设计

### 4.1 用户认证
- 密码加密存储
- Session管理
- 登录状态维护

### 4.2 权限控制
- 用户权限验证
- 资源访问控制
- 操作权限检查

### 4.3 数据安全
- SQL注入防护
- XSS防护
- CSRF防护 