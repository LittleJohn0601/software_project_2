# PeakShift - 工业用电成本与碳排放分析优化系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 项目简介

**PeakShift** 是一个面向高耗电量工业企业的智能能源管理系统，旨在通过分析电力消费和碳排放情况，结合分时电价（TOU）数据，为企业提供电费优化建议，帮助企业降低电费支出并实现节能减排目标。

### 🎯 核心目标

- 📊 **实时监控**：追踪企业用电量和碳排放数据
- 💰 **成本优化**：基于分时电价提供生产时间调整建议
- 🌱 **减排分析**：计算不同电力来源的碳排放量
- 📈 **数据可视化**：直观展示用电趋势和优化效果

---

## 🚀 快速开始（推荐使用 Docker）

### 方法 1：使用 Docker（推荐）⭐

**为什么用 Docker？**
- ✅ 一键配置环境，无需手动安装 Python、依赖
- ✅ 所有人环境完全一致（Mac/Windows）
- ✅ 代码修改自动生效，无需重启
- ✅ 方便部署到虚拟机

#### 第一步：安装 Docker Desktop
- 下载：https://www.docker.com/products/docker-desktop
- 双击安装，就像装普通软件
- 打开 Docker Desktop，等待启动完成

#### 第二步：克隆项目
```bash
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2
```

#### 第三步：启动项目
```bash
docker-compose up --build
```
首次启动需要 3-5 分钟构建镜像，数据库会自动初始化，看到 `Running on http://0.0.0.0:5001` 就成功了。

#### 第四步：访问应用
打开浏览器：http://localhost:5001

#### 日常使用
- **启动**：打开 Docker Desktop → 找到 `peakshift-app` → 点 ▶️
- **停止**：点 ⏸️ 或按 `Ctrl+C`
- **拉取最新代码**：`git pull` 后直接点 ▶️ 运行（不需要重新构建）
- **写代码**：正常用 VS Code 写，保存后自动生效

---

### 方法 2：传统方式（不推荐）

<details>
<summary>点击展开传统安装方式</summary>

#### 环境要求
- Python 3.11 或更高版本
- pip 包管理器
- Git

#### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/LittleJohn0601/software_project_2.git
   cd software_project_2
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化数据库**
   ```bash
   python init_db.py
   ```

5. **运行应用**
   ```bash
   python microblog.py
   ```

6. **访问应用**
   打开浏览器：http://127.0.0.1:5001

</details>

---

## 🐳 Docker 使用指南

### 常用命令

```bash
# 启动项目（前台运行）
docker-compose up

# 启动项目（后台运行）
docker-compose up -d

# 停止项目
docker-compose down

# 查看日志
docker-compose logs -f

# 重新构建（新增依赖时）
docker-compose up --build
```

### Docker Desktop 操作

| 操作 | 位置 | 说明 |
|------|------|------|
| **启动** | 点击 ▶️ | 启动容器 |
| **停止** | 点击 ⏸️ | 停止容器 |
| **重启** | 点击 🔄 | 重启容器 |
| **查看日志** | 点击容器名 → Logs | 查看运行日志 |
| **重新构建** | 点击 ⋯ → Rebuild | 新增依赖时用 |

### 常见问题

**Q: 端口被占用怎么办？**
```bash
# 查找占用端口的进程
lsof -i :5001
# 停止进程
kill <PID>
```

**Q: 代码修改不生效？**
- 确保文件保存了
- 刷新浏览器
- 如果还不行，重启容器

**Q: 新增了 Python 依赖怎么办？**
- Docker Desktop → 点击 ⋯ → Rebuild

**Q: 首次运行没有数据库？**
- 数据库会在首次启动时自动创建
- 如果遇到问题，重新构建：`docker-compose up --build`

---

## ✨ 已实现功能

### 1. 用户认证系统 ✅
- 单页认证界面（登录/注册）
- 动画交互效果
- 用户名/邮箱登录
- 密码加密存储

### 2. 工厂管理 ✅
- 创建工厂
- 查看工厂列表
- 删除工厂
- 工厂基本信息展示

### 3. 全局音乐播放器 ✅
- 独立模块设计
- 自动播放
- 进度保存
- 可安全删除

---

## 🛠️ 技术架构

### 前端技术栈
- **HTML5** + **CSS3** + **JavaScript (ES6+)**
- **Bootstrap 5** - 响应式 UI 框架
- **Chart.js** - 数据可视化（规划中）

### 后端技术栈
- **Python 3.11+** - 编程语言
- **Flask 3.1+** - Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **Flask-Login** - 用户认证
- **Flask-WTF** - 表单处理与 CSRF 保护

### 容器化
- **Docker** - 容器化部署
- **Docker Compose** - 服务编排

### 数据库
- **SQLite** - 轻量级关系型数据库

---

## 📦 项目结构

```
software_project_2/
├── blogapp/                    # 应用主模块（所有代码写这里）
│   ├── __init__.py            # 应用工厂
│   ├── models.py              # 数据模型
│   ├── forms.py               # 表单定义
│   ├── routes/                # 路由模块
│   │   ├── auth.py           # 认证路由
│   │   ├── main.py           # 主要路由
│   │   └── public.py         # 公共路由
│   ├── static/                # 静态文件
│   │   ├── css/              # 样式文件
│   │   ├── js/               # JavaScript 文件
│   │   └── music-player/     # 音乐播放器模块
│   └── templates/             # 模板文件
│       ├── auth/             # 认证页面
│       └── dashboard.html    # 主应用页面
├── instance/                  # 数据库文件
├── logs/                      # 日志文件
├── Dockerfile                 # Docker 镜像配置
├── docker-compose.yml         # Docker 编排配置
├── requirements.txt           # Python 依赖
├── microblog.py              # 应用入口
└── init_db.py                # 数据库初始化
```

---

## � 团队协作规范

### Git 工作流

1. **个人分支开发**
   ```bash
   git checkout -b branch-your-name
   ```

2. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin branch-your-name
   ```

3. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 等待代码审查
   - 合并到 main 分支

### Commit 规范

```
feat: 添加新功能
fix: 修复 bug
refactor: 重构代码
docs: 更新文档
style: 代码格式调整
```

### 开发规范

**⚠️ 重要：所有新代码必须写在 `blogapp/` 文件夹下！**

- ✅ 新增路由 → `blogapp/routes/`
- ✅ 新增模板 → `blogapp/templates/`
- ✅ 新增样式 → `blogapp/static/css/`
- ✅ 新增脚本 → `blogapp/static/js/`
- ❌ 不要在项目根目录新增 `.py` 文件

### 数据库开发规范

**数据库自动初始化机制：**
- 应用启动时会自动调用 `db.create_all()`
- 读取 `blogapp/models.py` 中的所有模型并创建对应表
- 如果表已存在，不会覆盖或删除数据
- 如果表不存在，自动创建

**添加新表的流程：**

1. 在 `blogapp/models.py` 中定义新模型
   ```python
   class YourNewTable(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(100))
       # 添加其他字段...
   ```

2. 提交代码到 Git
   ```bash
   git add blogapp/models.py
   git commit -m "feat: 添加新表 YourNewTable"
   git push
   ```

3. 队友拉取代码后重启容器
   ```bash
   git pull
   docker-compose restart
   ```

4. 新表自动创建，无需手动操作 ✅

**修改已有表结构的流程：**

⚠️ **重要**：SQLite 不支持直接修改表结构，需要删除旧数据库重新创建

1. 修改 `blogapp/models.py` 中的模型定义

2. 删除旧数据库文件
   ```bash
   # 停止容器
   docker-compose down
   
   # 删除数据库
   rm instance/greenlife.db
   
   # 重启容器（数据库会自动重建）
   docker-compose up
   ```

3. 数据库会根据新的模型结构自动创建 ✅

**注意事项：**
- 所有数据模型必须定义在 `blogapp/models.py` 中
- 修改表结构后需要删除数据库并重启应用
- `db.create_all()` 不会修改已存在的表结构
- 删除数据库会丢失所有数据，生产环境请使用数据库迁移工具（如 Flask-Migrate）

---

## 📝 开发计划

### Phase 1 - 基础功能 ✅
- [x] 用户认证系统
- [x] 工厂管理功能
- [x] Docker 容器化
- [x] 单页应用架构

### Phase 2 - 核心功能（进行中）
- [ ] 仪表盘页面
- [ ] 用电数据录入
- [ ] 碳排放计算
- [ ] 成本分析

### Phase 3 - 数据可视化
- [ ] Chart.js 图表集成
- [ ] 实时数据展示
- [ ] 对比分析功能

### Phase 4 - 优化与部署
- [ ] 报告生成系统
- [ ] 优化建议引擎
- [ ] 虚拟机部署
- [ ] 性能优化

---

## � 部署到虚拟机

### 使用 Docker 部署（推荐）

**在虚拟机上：**
```bash
# 1. 安装 Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker

# 2. 克隆项目
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2

# 3. 启动
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

**访问应用：**
```
http://虚拟机IP:5001
```

---

## 📊 代码统计

- **总提交次数**: 10+
- **新增代码**: ~3,000 行
- **删除旧代码**: ~760,000 行
- **主要语言**: Python, HTML, CSS, JavaScript

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b branch-your-name`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin branch-your-name`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 📞 联系方式

- **项目仓库**: https://github.com/LittleJohn0601/software_project_2
- **问题反馈**: [Issues](https://github.com/LittleJohn0601/software_project_2/issues)

---

## 🙏 致谢

感谢所有为本项目做出贡献的团队成员！

---

**最后更新**: 2026-03-22
