# 在线考试系统（星途学堂）

基于 **微信小程序 + Flask + MySQL** 的前后端分离在线考试系统。教师可上传/发布试卷，学生可下载试卷并在作答后交卷，系统同时提供用户注册、登录、个人中心等完整闭环功能。

> 项目当前处于 **课程设计 / 功能迭代中** 的阶段：登录注册与「上传试卷 → 下载 → 交卷」主流程已跑通；`database.sql` 中已预留试卷库、交卷记录等表结构，但后端尚未完全接入。

---

## 一、系统架构

```
┌─────────────────────────┐        HTTP / JSON         ┌──────────────────────────────┐
│     前端（微信小程序）      │  ────────────────────────▶  │      后端（Flask 服务）        │
│  ─────────────────────  │                            │  ──────────────────────────  │
│  · 登录 / 注册           │    /api/login              │  app.py  —— 业务接口层         │
│  · 学生端：下载试卷、交卷    │    /api/register           │     │                       │
│  · 教师端：上传试卷、发布    │    /File/upload            │     ▼                       │
│  · 个人中心、班级选择       │    /File/download          │  db.py   —— 数据库访问层       │
│                          │    /File/check_upload      │     │                       │
│                          │    /File/submit            │     ▼                       │
│  app.js（全局登录/登出）    │  ────────────────────────▶  │   MySQL（exam_system 库）    │
└─────────────────────────┘                            └──────────────────────────────┘
```

- **后端地址（默认）**：`http://192.168.31.108:5000`（局域网内其他设备亦可访问）
- **技术栈**：前端使用微信小程序原生框架（WXML / WXSS / JS），后端使用 Python Flask，数据层通过 MySQL `mysql-connector` 驱动访问，环境配置读取 `python-dotenv`。

---

## 二、功能特性

### 按角色划分
| 角色 | 主要功能 |
|------|----------|
| 学生 | 登录、下载教师发布的试卷（Word/PDF 等）、作答后交卷、查看已完成/待提交考试 |
| 教师 | 登录、上传试卷（多格式，≤100MB）、查看已交卷情况 |
| 管理员 | 登录时可选择以「教师」或「学生」身份进入对应考试首页 |

### 前端功能清单
| 页面 | 说明 | 状态 |
|------|------|------|
| `pages/login` | 登录（账号+密码，可选班级/身份；管理员二次选择入口身份） | ✅ 可用 |
| `pages/register-info` | 注册（学号/工号、昵称、密码、姓名、头像、生日、性别、班级、身份） | ✅ 可用 |
| `pages/Exam-student` | 学生考试首页：轮播 + 检查是否已有试卷 → 下载 / 交卷 | ✅ 可用 |
| `pages/Exam-teacher` | 教师考试首页：上传试卷（带进度条） | ✅ 可用 |
| `pages/Exam-paper` | 试卷列表：已完成 / 待提交 / 未参加（当前为静态示例数据） | 🚧 静态示例 |
| `pages/profile` | 个人中心：展示用户信息、登出、注册页入口 | ✅ 可用 |
| `pages/logs` | 日志占位页（模板遗留） | ➖ 遗留 |

### 后端接口清单
| 方法 | 路径 | 说明 | 返回 |
|------|------|------|------|
| GET | `/` | 服务器连通性测试 | `Hello World!` |
| GET | `/api/health` | 健康检查（服务与数据库状态） | `success/status/database` |
| POST | `/File/upload` | 教师上传试卷（multipart，字段 `file`） | `{success, filename}` |
| GET | `/File/check_upload` | 检查当前是否已有已上传试卷 | `{has_file[, filename]}` |
| GET | `/File/download` | 下载最新一份试卷 | 文件流 / 404 |
| POST | `/File/submit` | 学生交卷（字段 `file` + `student_id`） | `{success, filename}` |
| POST | `/api/register` | 用户注册（JSON），按身份自动补建学生/教师记录 | `{success, user_id}` |
| POST | `/api/login` | 用户登录校验 | `{success, user_info}` / 401 |
| GET | `/api/user/<id>` | 按用户 ID 查询信息 | `{success, user_info}` / 404 |

> ⚠️ 文件上传后保存于服务端 `File/upload`、`File/submit` 目录（以 `uuid_原名` / `学号_uuid_原名` 命名防冲突）。

---

## 三、目录结构

```
qimozuoye/
├── Frontend/                    # 微信小程序前端
│   ├── app.js                   # 全局逻辑：登录/注册/登出、角色路由、API 基址
│   ├── app.json                 # 全局配置：页面注册、tabBar、超时
│   ├── app.wxss                 # 全局样式
│   ├── project.config.json      # 小程序项目配置（appid: wx103174eafd685219）
│   ├── sitemap.json             # 页面收录配置
│   ├── images/                  # 静态图标资源
│   ├── utils/util.js            # 工具函数（时间格式化）
│   └── pages/                   # 页面目录（见上方功能清单）
│
├── Server/                      # Flask 后端
│   ├── app.py                   # 主服务：全部 HTTP 接口 + CORS + 文件存储逻辑
│   ├── db.py                    # 数据库操作类 Database（连接/增删改查封装）
│   ├── database.sql             # 建库建表脚本（users/students/teachers/exam_papers/student_submissions）
│   ├── .env                     # 环境配置示例（数据库/服务参数）
│   ├── .pytest_cache/           # 测试缓存
│   ├── test_db_connection.py    # 数据库连接测试脚本
│   ├── test_register.py         # 注册接口测试脚本
│   ├── File/upload/             # 教师上传试卷存放目录（运行时自动创建）
│   ├── File/submit/             # 学生交卷存放目录（运行时自动创建）
│   └── uploads/                 # 早期版本遗留的上传文件
│
├── .venv/                       # 项目虚拟环境（Python 3.11，含完整依赖）
├── .idea/                       # IDE 配置
└── test.txt                     # 临时文件
```

---

## 四、技术栈与依赖

### 后端
| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.11.3 | 运行环境 |
| Flask | 3.1.x | Web 服务框架 |
| Flask-Cors | 1.x | 跨域支持（允许前端跨端口/跨来源调用） |
| mysql-connector-python | 2.2.9 | MySQL 驱动 |
| python-dotenv | 1.2.x | 读取 `.env` 环境配置 |

> 依赖集中在仓库根目录的 `.venv` 虚拟环境中；`Server/.venv` 为不完整的旧环境，开发请以根目录 `.venv` 为准。
> 目前项目未提供 `requirements.txt`，可在根虚拟环境中执行 `pip freeze > requirements.txt` 按需生成。

### 前端
- 微信小程序原生框架（WXML / WXSS / JavaScript），基础库版本设为 `trial`。
- 通过 `wx.request` / `wx.uploadFile` / `wx.downloadFile` 与后端通信。

---

## 五、快速开始

### 1. 环境准备
- [Python 3.11+](https://www.python.org/downloads/)
- [MySQL 5.7 / 8.x](https://dev.mysql.com/downloads/)
- [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)（调试小程序用）

### 2. 初始化数据库
```bash
mysql -u root -p < Server/database.sql
```
执行后创建数据库 `exam_system`，以及 `users`、`students`、`teachers`、`exam_papers`、`student_submissions` 五张表。

### 3. 配置后端环境变量
复制/创建 `Server/.env`（参考现有文件）：
```ini
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=exam_system

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=True
```

### 4. 启动后端服务
```bash
# 使用根目录虚拟环境
.venv/Scripts/python.exe Server/app.py
# 或先激活环境再运行
source .venv/Scripts/activate
cd Server && python app.py
```

验证：浏览器访问 `http://localhost:5000/api/health`，应返回
`{"success": true, "status": "UP", "database": "connected"}`。

> ⚠️ `app.py` 底部当前硬编码 `app.run(host='192.168.31.108', port=5000, debug=True)`，请改成你本机的局域网 IP（或 `0.0.0.0`）以保证小程序真机/模拟器可访问。

### 5. 运行微信小程序
1. 打开**微信开发者工具**，选择「导入项目」，目录指向 `Frontend/`（appid 已配置为 `wx103174eafd685219`）。
2. 如需使用自己的 appid，可替换 `project.config.json` 中的 `appid`。
3. 确认前端 API 地址与后端一致：全局基址在 `Frontend/app.js` 的 `globalData.apiBaseUrl`；部分页面（如 `Exam-student`、`Exam-teacher`）的请求地址是硬编码的 `http://192.168.31.108:5000`，请一并修改为你的后端地址。
4. 开发阶段若提示「不在以下 request 合法域名列表中」，请在开发者工具中勾选 **「详情 → 本地设置 → 不校验合法域名」**。

> 已注册的账号即可登录；也可通过「注册页」用学号/工号 + 身份完成新账号注册。

---

## 六、数据库设计

| 表 | 说明 | 关键字段 |
|----|------|----------|
| `users` | 用户主表（所有角色） | id、username(唯一)、password、name、avatar_url、gender、birthday、role(student/teacher/admin)、class_name |
| `students` | 学生信息表 | id、user_id(FK)、student_id(学号，唯一) |
| `teachers` | 教师信息表 | id、user_id(FK)、teacher_id(工号，唯一)、department |
| `exam_papers` | 试卷表（**已建表，未接入**） | id、title、description、file_path、file_name、uploader_id(FK) |
| `student_submissions` | 交卷记录表（**已建表，未接入**） | id、student_id(FK)、exam_paper_id(FK)、file_path、file_name、score |

设计上注册采用「主表 + 角色子表」的纵向拆分：学生注册额外写入 `students`，教师注册额外写入 `teachers`。

---

## 七. 已知限制与后续规划

- **试卷/交卷尚未入库**：当前试卷与答卷以文件形式落在服务器磁盘，`exam_papers` / `student_submissions` 两张表尚未被后端读写，交卷人数统计、打分（`score`）等能力待接入。
- **试卷列表为静态数据**：`Exam-paper` 页面使用写死的示例考试数据，未请求后端。
- **鉴权简单**：登录成功后以「用户 ID + 时间戳」临时充当 token 存于本地缓存，`validateToken` 尚未真正调用后端校验，接口层也未做登录态拦截。
- **代码风格不统一**：部分页面请求地址硬编码（未走 `apiBaseUrl`）；`app.py` 的 host/port 建议统一读取 `.env`。

---

## 八、测试脚本

`Server/` 下提供了轻量测试脚本（运行前请确认服务已启动、依赖已安装）：
- `test_db_connection.py` —— 测试数据库能否连通。
- `test_register.py` —— 对注册接口发起测试请求。

```bash
cd Server
python test_db_connection.py
python test_register.py
```
