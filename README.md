# PeakShift - 工业用电成本与碳排放分析优化系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Security](https://img.shields.io/badge/Security-AES--128-green.svg)](https://cryptography.io/)

---

## 📋 项目简介

**PeakShift** 是一个面向高耗电量工业企业的智能能源管理系统，通过分析电力消费和碳排放情况，结合分时电价（TOU）数据，为企业提供电费优化建议，帮助降低电费支出并实现节能减排目标。

### 🎯 核心功能

- 📊 **实时监控**：追踪企业用电量和碳排放数据
- 💰 **成本优化**：基于分时电价提供生产时间调整建议
- 🌱 **减排分析**：计算不同电力来源的碳排放量
- 📈 **数据可视化**：直观展示用电趋势和优化效果
- 🔐 **数据安全**：敏感信息加密存储，保护商业隐私

---

## 🚀 快速开始

### 前置要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop) （推荐）
- 或 Python 3.11+ （传统方式）

### 使用 Docker（推荐）⭐

```bash
# 1. 克隆项目
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2

# 2. 配置加密密钥（首次运行）
python3 generate_encryption_key.py
# 复制生成的密钥，添加到 .env 文件中

# 3. 启动项目
docker-compose up --build

# 4. 访问应用
# 打开浏览器：http://localhost:5001
```

**首次启动需要 3-5 分钟构建镜像，数据库会自动初始化。**

### 传统方式

<details>
<summary>点击展开传统安装方式</summary>

```bash
# 1. 克隆项目
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置加密密钥
python3 generate_encryption_key.py
# 创建 .env 文件并添加生成的密钥

# 5. 运行应用
python microblog.py

# 6. 访问应用
# 打开浏览器：http://127.0.0.1:5001
```

</details>

---

## � 数据库加密配置

### 为什么需要加密？

保护用户隐私和商业敏感信息，即使数据库被盗，敏感数据仍是密文。

### 加密的字段

| 表名 | 字段 | 说明 |
|------|------|------|
| `user` | `email` | 用户邮箱地址 |
| `user` | `username` | 用户名 |
| `factory` | `name` | 工厂名称 |
| `factory` | `location` | 工厂地址 |
| `factory` | `industry_type` | 行业类型 |

### 快速配置

```bash
# 1. 生成加密密钥
python3 generate_encryption_key.py

# 2. 创建 .env 文件
# 将生成的密钥添加到 .env 文件中
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DEBUG=True
DATABASE_URL=sqlite:///greenlife.db
ENCRYPTION_MASTER_KEY=your-generated-key-here
SESSION_COOKIE_SECURE=False
REMEMBER_COOKIE_SECURE=False
EOF

# 3. 测试加密功能
python3 test_encryption.py

# 4. 迁移现有数据（如果有）
echo "yes" | python3 migrate_to_encrypted_db.py
```

### 安全提醒 ⚠️

- ✅ 密钥已自动添加到 `.gitignore`，不会提交到 Git
- ✅ 备份密钥到安全位置（密码管理器）
- ✅ 密钥丢失将导致数据无法恢复
- ✅ 不要通过不安全渠道传输密钥

---

## ✨ 已实现功能

### 1. 用户认证系统 ✅
- 单页认证界面（登录/注册）
- 动画交互效果
- 用户名/邮箱登录
- 密码哈希存储（PBKDF2）

### 2. 工厂管理 ✅
- 创建/编辑/删除工厂
- 工厂列表展示
- 工厂详情页面
- 用电数据配置

### 3. 数据库加密 ✅ 🔐
- 5 个敏感字段加密存储
- Fernet 对称加密（AES-128）
- 透明加解密（对开发者无感）
- 密钥管理工具
- 数据迁移脚本
- 完整测试套件

### 4. 成本分析 ✅
- 月度电费计算
- 峰谷平电价分析
- 容量费用计算
- 碳排放计算

### 5. 数据可视化 ✅
- 实时电价图表（Chart.js）
- 能源结构饼图
- 成本报告表格
- 优化建议展示

---

## 🛠️ 技术架构

### 前端技术栈
- **HTML5 + CSS3 + JavaScript (ES6+)**
- **Bootstrap 5** - 响应式 UI 框架
- **Chart.js** - 数据可视化

### 后端技术栈
- **Python 3.11+** - 编程语言
- **Flask 3.1+** - Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **Flask-Login** - 用户认证
- **Flask-WTF** - 表单处理与 CSRF 保护
- **Cryptography** - 数据加密（Fernet/AES-128）

### 数据库
- **SQLite** - 轻量级关系型数据库
- **字段级加密** - 敏感数据保护

### 容器化
- **Docker** - 容器化部署
- **Docker Compose** - 服务编排

---

## 📦 项目结构

```
software_project_2/
├── blogapp/                    # 应用主模块
│   ├── __init__.py            # 应用工厂
│   ├── models.py              # 数据模型（含加密字段）
│   ├── forms.py               # 表单定义
│   ├── routes/                # 路由模块
│   │   ├── auth.py           # 认证路由
│   │   ├── main.py           # 主要路由
│   │   ├── admin.py          # 管理员路由
│   │   └── visualization.py  # 数据可视化 API
│   ├── services/              # 业务逻辑
│   │   ├── electricity_cost.py      # 电费计算
│   │   └── supplier_optimizer.py   # 供应商优化
│   ├── utils/                 # 工具模块
│   │   ├── encryption.py     # 加密工具
│   │   └── price_sync.py     # 价格同步
│   ├── static/                # 静态文件
│   │   ├── css/              # 样式文件
│   │   └── js/               # JavaScript 文件
│   ├── templates/             # 模板文件
│   └── data/                  # 数据文件（Excel）
├── instance/                  # 数据库文件
├── logs/                      # 日志文件
├── tests/                     # 测试文件
├── Dockerfile                 # Docker 镜像配置
├── docker-compose.yml         # Docker 编排配置
├── requirements.txt           # Python 依赖
├── microblog.py              # 应用入口
├── generate_encryption_key.py # 密钥生成工具
├── migrate_to_encrypted_db.py # 数据迁移工具
└── test_encryption.py        # 加密测试
```

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

# 重启容器
docker-compose restart
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

<details>
<summary>Q: 端口被占用怎么办？</summary>

```bash
# 查找占用端口的进程
lsof -i :5001
# 停止进程
kill <PID>
```
</details>

<details>
<summary>Q: 代码修改不生效？</summary>

- 确保文件保存了
- 刷新浏览器（Ctrl+F5 强制刷新）
- 如果还不行，重启容器
</details>

<details>
<summary>Q: 新增了 Python 依赖怎么办？</summary>

- 更新 `requirements.txt`
- Docker Desktop → 点击 ⋯ → Rebuild
- 或命令行：`docker-compose up --build`
</details>

<details>
<summary>Q: 加密密钥丢失怎么办？</summary>

- ⚠️ **无法恢复加密数据**
- 从备份恢复密钥
- 如果没有备份，需要重置数据库
</details>

---

## 🧪 测试

### 运行所有测试

```bash
# 加密功能测试
python3 test_encryption.py

# 单元测试（如果有）
pytest tests/
```

### 测试结果示例

```
============================================================
🔐 Database Encryption Test Suite
============================================================

✅ PASS - Basic Encryption
✅ PASS - User Email & Username Encryption
✅ PASS - Factory Sensitive Fields Encryption
✅ PASS - Database Persistence

Total: 4/4 tests passed
✅ All tests passed! Encryption is working correctly.
```

---

## 📝 开发规范

### Git 工作流

```bash
# 1. 创建个人分支
git checkout -b feature/your-feature-name

# 2. 提交代码
git add .
git commit -m "feat: 添加新功能"
git push origin feature/your-feature-name

# 3. 创建 Pull Request
# 在 GitHub 上创建 PR，等待代码审查
```

### Commit 规范

```
feat: 添加新功能
fix: 修复 bug
refactor: 重构代码
docs: 更新文档
style: 代码格式调整
test: 添加测试
chore: 构建/工具变动
```

### 代码规范

- ✅ 所有新代码写在 `blogapp/` 文件夹下
- ✅ 遵循 PEP 8 代码风格
- ✅ 添加必要的注释和文档字符串
- ✅ 敏感字段使用加密存储
- ❌ 不要在项目根目录新增 `.py` 文件
- ❌ 不要提交 `.env` 文件到 Git

---

## � 安全特性

### 已实施的安全措施

| 功能 | 实现方式 | 安全等级 |
|------|----------|----------|
| 密码存储 | PBKDF2 哈希 + 盐 | ⭐⭐⭐⭐⭐ |
| 敏感数据加密 | AES-128 对称加密 | ⭐⭐⭐⭐ |
| CSRF 保护 | Flask-WTF | ⭐⭐⭐⭐⭐ |
| Session 安全 | 强保护模式 | ⭐⭐⭐⭐ |
| 密钥管理 | 环境变量隔离 | ⭐⭐⭐⭐ |

### 安全最佳实践

- ✅ 密钥存储在 `.env` 文件，不提交到 Git
- ✅ 所有表单自动添加 CSRF token
- ✅ 密码使用单向哈希，不可逆
- ✅ 敏感字段透明加解密
- ✅ Session cookie 保护

---

## � 部署到生产环境

### 使用 Docker 部署（推荐）

```bash
# 1. 在服务器上安装 Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker

# 2. 克隆项目
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，设置生产环境配置

# 4. 启动服务
docker-compose up -d

# 5. 查看状态
docker-compose ps
docker-compose logs -f
```

### 生产环境配置建议

```env
# .env 文件示例
SECRET_KEY=your-production-secret-key
DEBUG=False
ENCRYPTION_MASTER_KEY=your-encryption-key
SESSION_COOKIE_SECURE=True
REMEMBER_COOKIE_SECURE=True
```

### 访问应用

```
http://服务器IP:5001
```

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 加密开销 | ~1-2ms | 每次写入 |
| 解密开销 | ~1-2ms | 每次读取 |
| 存储开销 | +50-100% | 密文比明文长 |
| 响应时间 | <100ms | 平均页面加载 |

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📞 联系方式

- **项目仓库**: https://github.com/LittleJohn0601/software_project_2
- **问题反馈**: [Issues](https://github.com/LittleJohn0601/software_project_2/issues)
- **项目文档**: 查看本 README

---

## 🙏 致谢

感谢所有为本项目做出贡献的团队成员！

特别感谢：
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Bootstrap](https://getbootstrap.com/) - UI 框架
- [Chart.js](https://www.chartjs.org/) - 图表库
- [Cryptography](https://cryptography.io/) - 加密库

---

**最后更新**: 2026-04-21  
**版本**: 1.0.0  
**状态**: ✅ 生产就绪
