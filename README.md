# PeakShift - 工业用电成本与碳排放分析优化系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
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

## ✨ 主要功能

### 1. 碳排放计算（Carbon Emission Calculation）

- 根据企业的电力来源（火电、风电、太阳能等）计算碳排放
- 支持每日/每月电力使用数据的自动碳排放量计算
- 使用标准碳排放因子（如火电 820gCO₂/kWh，风电 11gCO₂/kWh）

**示例场景：**
> 某电解铝厂 60% 的电力来源于火电，40% 来自新能源。系统根据不同电力来源的碳排放因子，自动计算工厂的总碳排放量，并提供减排建议。

### 2. 电费优化建议（Electricity Cost Optimization）

- 基于分时电价（TOU）数据分析用电成本
- 提供生产时间调整建议，避开高峰电价时段
- 智能推荐低电价时段的生产计划

**示例场景：**
> 系统检测到白天高峰时段电价较高，建议将部分生产负荷转移至中午太阳能发电量高、电价较低的时段，预计每月可节省电费 ¥12,000。

### 3. 多工厂管理

- 支持用户管理多个工厂案例
- 独立配置每个工厂的电力来源和运行时间
- 对比分析不同工厂的能耗和成本

### 4. 报告生成

- 自动生成碳排放分析报告
- 电费支出详细分析报告
- 生产时间优化建议报告
- 支持 PDF 导出和分享

---

## 🔄 系统流程

```
1. 用户注册与登录
   └─> 创建账号，管理多个工厂案例

2. 输入工厂数据
   └─> 配置用电量、电力来源、运行时间等

3. 自动分析与计算
   └─> 计算碳排放量和电费支出
   └─> 基于分时电价生成优化建议

4. 报告生成与优化建议
   └─> 生成分析报告
   └─> 提供生产时间调整方案
```

---

## 💡 创新点

### 🔗 碳排放与电费结合分析
将碳排放数据与分时电价相结合，提供综合的电费与碳排放优化建议，帮助企业在降低成本的同时实现环保目标。

### ⏰ 智能生产时间优化
通过分析不同时间段的电价波动，在保证生产需求的前提下，智能推荐最优生产时段，最大化降低电费支出。

### 📊 可视化数据分析
使用 Chart.js 提供直观的数据可视化，包括电价曲线、碳排放趋势、成本对比等，帮助企业快速做出决策。

---

## 🛠️ 技术架构

### 前端技术栈
- **HTML5** - 页面结构
- **CSS3** - 样式设计
- **JavaScript (ES6+)** - 交互逻辑
- **Bootstrap 5** - 响应式 UI 框架
- **Chart.js** - 数据可视化图表库

### 后端技术栈
- **Python 3.11+** - 编程语言
- **Flask 3.1+** - Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **Flask-Login** - 用户认证
- **Flask-WTF** - 表单处理与 CSRF 保护

### 数据库
- **SQLite** - 轻量级关系型数据库
- 存储用户、工厂信息、电力使用、碳排放数据等

### 部署环境
- **UCD VM + Nginx** - 生产环境部署
- Nginx 反向代理，将外部 Port 80 请求转发至 Flask 内部端口（如 5000）

---

## 📦 项目结构

```
software_project_2/
├── blogapp/                    # 应用主模块
│   ├── __init__.py            # 应用工厂
│   ├── models.py              # 数据模型
│   ├── forms.py               # 表单定义
│   ├── decorators.py          # 装饰器
│   ├── routes/                # 路由模块
│   │   ├── auth.py           # 认证路由
│   │   ├── main.py           # 主要路由
│   │   ├── public.py         # 公共路由
│   │   └── visualization.py  # 可视化路由
│   ├── static/                # 静态文件
│   │   ├── css/              # 样式文件
│   │   │   └── login.css     # 登录页面样式
│   │   └── js/               # JavaScript 文件
│   │       └── login.js      # 登录页面交互
│   └── templates/             # 模板文件
│       └── auth/             # 认证相关模板
│           └── login.html    # 登录页面
├── instance/                  # 实例文件夹
│   └── greenlife.db          # SQLite 数据库
├── logs/                      # 日志文件
├── venv/                      # Python 虚拟环境
├── microblog.py              # 应用入口
├── init_db.py                # 数据库初始化脚本
├── .gitignore                # Git 忽略文件
└── README.md                 # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11 或更高版本
- pip 包管理器
- Git

### 安装步骤

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
   pip install flask flask-sqlalchemy flask-login flask-wtf python-dotenv cryptography
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
   
   打开浏览器访问：http://127.0.0.1:5000

---

## 👥 团队协作规范

### Git 分支管理

- **main** - 主分支，保持稳定可部署状态
- **branch-[姓名]** - 个人开发分支（如 `branch-bole-wu`）
- 所有开发工作必须在个人分支进行
- 完成功能后通过 Pull Request 合并到 main

### Commit 规范

使用语义化提交信息：

```
feat: 添加新功能
fix: 修复 bug
refactor: 重构代码
docs: 更新文档
style: 代码格式调整
test: 添加测试
chore: 构建/工具链更新
```

**示例：**
```bash
git commit -m "feat: 实现工厂管理功能"
git commit -m "fix: 修复电费计算精度问题"
git commit -m "docs: 更新 API 文档"
```

### 代码审查

- 所有 Pull Request 需要至少一位团队成员审查
- 管理员（Administrator）拥有最终合并权限
- 保持代码质量和一致性

---

## 🔒 安全注意事项

### 开发环境

- ⚠️ **严禁使用 sudo** 运行后端程序
- ⚠️ **SSH 密码必须 16 位以上**，且非字典词
- 使用 `.env` 文件管理敏感配置（不要提交到 Git）

### 远程访问

- 软件必须能从爱尔兰远程访问
- 代码中不得写死 `127.0.0.1` 或 `raw IP`
- 必须使用 `Hostname` 进行配置

---

## 📝 开发计划

### Phase 1 - 基础功能（当前）
- [x] 用户认证系统（登录/注册）
- [x] 数据库模型设计
- [ ] 工厂管理功能
- [ ] 电力来源配置

### Phase 2 - 核心功能
- [ ] 用电数据录入
- [ ] 碳排放计算引擎
- [ ] 分时电价管理
- [ ] 电费优化算法

### Phase 3 - 数据可视化
- [ ] 仪表盘设计
- [ ] 图表集成（Chart.js）
- [ ] 实时数据展示
- [ ] 对比分析功能

### Phase 4 - 报告与优化
- [ ] 报告生成系统
- [ ] PDF 导出功能
- [ ] 优化建议引擎
- [ ] 生产时间调整工具

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b branch-your-name`)
3. 提交你的更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin branch-your-name`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **项目仓库**: https://github.com/LittleJohn0601/software_project_2
- **问题反馈**: [Issues](https://github.com/LittleJohn0601/software_project_2/issues)

---

## 🙏 致谢

感谢所有为本项目做出贡献的团队成员！

---

**最后更新**: 2026-03-14
