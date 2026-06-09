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
python3 scripts/security/generate_encryption_key.py
# 复制生成的密钥，添加到 .env 文件中

# 3. 启动项目
docker-compose up --build

# 4. 访问应用
# 打开浏览器：http://localhost:5001
```

**首次启动需要 3-5 分钟构建镜像，数据库会自动初始化。**

### 虚拟机手动 Docker 运行注意事项

应用默认使用 SQLite 数据库，文件位于容器内 `/app/instance/greenlife.db`。如果使用 `docker rm` 删除旧容器后再直接 `docker run`，而没有挂载宿主机目录，用户、工厂等运行时数据会随旧容器一起丢失。

在虚拟机上手动运行时，请固定挂载 `instance` 和 `logs`：

```bash
cd ~/software_project_2
git pull
mkdir -p instance logs
sudo docker build --no-cache -t software_project_2-web:latest .
sudo docker stop software_project_2 2>/dev/null || true
sudo docker rm software_project_2 2>/dev/null || true
sudo docker run -d \
  -p 80:5001 \
  --name software_project_2 \
  -v "$PWD/instance:/app/instance" \
  -v "$PWD/logs:/app/logs" \
  software_project_2-web:latest
```

只要 `~/software_project_2/instance/greenlife.db` 不被删除，重建镜像、删除旧容器、启动新容器都不会清空数据库。

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
python3 scripts/security/generate_encryption_key.py
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
python3 scripts/security/generate_encryption_key.py

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
python3 scripts/security/test_encryption.py

# 4. 迁移现有数据（如果有）
echo "yes" | python3 scripts/database/migrate_to_encrypted_db.py
```

### 开发环境配置 🔧

**团队协作模式：**

- ✅ `instance/greenlife.db` 数据库已同步到仓库（包含测试数据）
- ✅ `.env` 文件不同步（密钥由团队负责人手动分发）
- ✅ 所有人使用相同的加密密钥，可以读取相同的数据

**快速开始（团队成员）：**

```bash
# 1. 克隆项目
git clone <仓库地址>
cd software_project_2

# 2. 创建 .env 文件（从团队负责人获取密钥）
cp .env.example .env
# 编辑 .env 文件，填入团队负责人提供的密钥：
# - SECRET_KEY=<团队负责人提供>
# - ENCRYPTION_MASTER_KEY=<团队负责人提供>

# 3. 启动项目
docker-compose up

# 4. 访问应用
# http://localhost:5001
```

**团队负责人分发密钥：**

当前项目使用的密钥（通过安全渠道发送给队友）：
```
SECRET_KEY=34e8b019bc442035b4816e712a529e18a27ee720523cb750a1fd1adbbec84ff1
ENCRYPTION_MASTER_KEY=ar5r93oB646IVE5i76w5WAnt_lR9nNpoREwUZixHdtY=
```

### 安全提醒 ⚠️

- ⚠️ **仅适用于开发/学习环境**
- ⚠️ **通过安全渠道分发密钥**（微信/钉钉/邮件等）
- ⚠️ **生产环境必须使用独立密钥，不要提交到 Git**
- ✅ 备份密钥到安全位置（密码管理器）
- ✅ 密钥丢失将导致数据无法恢复

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
│   ├── decorators.py          # 装饰器
│   ├── routes/                # 路由模块
│   │   ├── auth.py           # 认证路由
│   │   ├── main.py           # 主要路由
│   │   ├── admin.py          # 管理员路由
│   │   ├── public.py         # 公共路由
│   │   └── visualization.py  # 数据可视化 API
│   ├── services/              # 业务逻辑
│   │   ├── electricity_cost.py      # 电费计算
│   │   └── supplier_optimizer.py   # 供应商优化
│   ├── utils/                 # 工具模块
│   │   ├── encryption.py     # 加密工具
│   │   ├── price_sync.py     # 价格同步
│   │   └── sensitive_word_filter.py # 敏感词过滤
│   ├── static/                # 静态文件
│   │   ├── css/              # 样式文件
│   │   ├── js/               # JavaScript 文件
│   │   └── music-player/     # 音乐播放器组件
│   └── templates/             # 模板文件
│       ├── auth/             # 认证相关模板
│       ├── dashboard.html    # 用户仪表板
│       └── admin_dashboard.html # 管理员仪表板
├── scripts/                   # 🆕 工具脚本目录
│   ├── admin/                # 管理员相关脚本
│   │   └── create_admin.py  # 创建管理员账号
│   ├── database/             # 数据库相关脚本
│   │   ├── init_db.py       # 初始化数据库
│   │   └── migrate_to_encrypted_db.py # 数据加密迁移
│   └── security/             # 安全相关脚本
│       ├── generate_encryption_key.py # 密钥生成
│       └── test_encryption.py        # 加密测试
├── data/                      # 🆕 数据文件目录
│   ├── excel/                # Excel 数据文件
│   │   ├── hourly_avg_30days(1).xlsx # 分时电价
│   │   ├── 电网售卖价格.xlsx  # 电网价格
│   │   └── 分时价格详情.xlsx  # 价格详情
│   └── xml/                  # XML 配置文件
│       └── dirtywords.xml   # 敏感词库
├── tests/                     # 测试文件
│   ├── conftest.py           # 测试配置
│   ├── test_models.py        # 模型测试
│   ├── test_electricity_cost.py # 电费计算测试
│   ├── test_supplier_optimizer.py # 优化器测试
│   ├── test_encryption.py    # 🆕 加密功能测试
│   └── test_sensitive_words.py # 🆕 敏感词测试
├── instance/                  # 数据库文件
│   └── greenlife.db          # SQLite 数据库
├── logs/                      # 日志文件
│   └── greenlife.log         # 应用日志
├── Dockerfile                 # Docker 镜像配置
├── docker-compose.yml         # Docker 编排配置
├── requirements.txt           # Python 依赖
├── microblog.py              # 应用入口
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略配置
└── README.md                 # 项目文档
```

### 🎯 目录说明

- **blogapp/**：核心应用代码，包含路由、模型、服务等
- **scripts/**：各类工具脚本，按功能分类（管理员、数据库、安全）
- **data/**：数据文件，包含 Excel 和 XML 配置文件
- **tests/**：单元测试和集成测试
- **instance/**：SQLite 数据库文件（开发环境）
- **logs/**：应用运行日志

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

## 🔧 工具脚本使用

项目提供了多个工具脚本，按功能分类存放在 `scripts/` 目录下。所有脚本都应该从项目根目录运行。

### 管理员脚本

#### 创建管理员账号
```bash
python scripts/admin/create_admin.py
```
交互式创建管理员账号，支持更新已有账号的密码。

### 数据库脚本

#### 初始化数据库
```bash
python scripts/database/init_db.py
```
手动初始化数据库表结构（通常不需要，应用启动时会自动初始化）。

#### 数据加密迁移
```bash
python scripts/database/migrate_to_encrypted_db.py
```
将现有未加密数据迁移到加密格式。**运行前请备份数据库！**

### 安全脚本

#### 生成加密密钥
```bash
python scripts/security/generate_encryption_key.py
```
生成新的加密密钥，用于数据库字段加密。

#### 测试加密功能
```bash
python scripts/security/test_encryption.py
```
运行加密功能测试套件，验证加密/解密是否正常工作。

---

## 📊 数据文件管理

项目的数据文件存放在 `data/` 目录下，按类型分类。

### Excel 数据文件 (`data/excel/`)

| 文件名 | 用途 | 更新方式 |
|--------|------|----------|
| `hourly_avg_30days(1).xlsx` | 供应商分时电价数据（24小时） | 应用启动时自动导入 |
| `电网售卖价格.xlsx` | 不同电压等级的电网售卖价格 | 应用启动时自动导入 |
| `分时价格详情.xlsx` | 峰谷平时段划分 | 应用启动时自动导入 |

**更新流程：**
1. 直接编辑 Excel 文件
2. 重启应用，数据会自动检测并导入
3. 查看日志确认导入成功

**注意事项：**
- ⚠️ 请勿修改 Excel 文件的列结构
- ✅ 修改前请备份原始文件
- ✅ 确保文件使用 UTF-8 编码

### XML 配置文件 (`data/xml/`)

| 文件名 | 用途 | 更新方式 |
|--------|------|----------|
| `dirtywords.xml` | 敏感词库，用于内容过滤 | 修改后需重启应用 |

**敏感词库格式：**
```xml
<dirtywords>
    <dirtyword word="敏感词1"/>
    <dirtyword word="敏感词2"/>
</dirtywords>
```

---

## 🧪 测试

### 运行所有测试

```bash
# 加密功能测试
python3 scripts/security/test_encryption.py

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
