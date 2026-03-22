# 🐳 PeakShift Docker 使用指南

## 📋 前置要求

### 安装 Docker Desktop

**Mac 用户：**
1. 访问 https://www.docker.com/products/docker-desktop
2. 下载 Docker Desktop for Mac
3. 双击安装包，拖到 Applications 文件夹
4. 打开 Docker Desktop，等待启动完成（顶部菜单栏会出现 Docker 图标）

**Windows 用户：**
1. 访问 https://www.docker.com/products/docker-desktop
2. 下载 Docker Desktop for Windows
3. 双击安装包，按提示安装
4. 重启电脑
5. 打开 Docker Desktop，等待启动完成

**验证安装：**
```bash
docker --version
docker-compose --version
```

---

## 🚀 快速开始

### 1. 克隆项目（如果还没有）
```bash
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2
```

### 2. 启动项目（首次需要几分钟构建）
```bash
docker-compose up
```

### 3. 访问应用
打开浏览器，访问：http://localhost:5001

### 4. 停止项目
按 `Ctrl+C` 或在新终端运行：
```bash
docker-compose down
```

---

## 📝 常用命令

### 启动项目
```bash
# 前台运行（可以看到日志）
docker-compose up

# 后台运行
docker-compose up -d

# 重新构建并启动
docker-compose up --build
```

### 停止项目
```bash
# 停止容器
docker-compose down

# 停止并删除数据卷（慎用！会删除数据库）
docker-compose down -v
```

### 查看日志
```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看最后 50 行
docker-compose logs --tail=50
```

### 进入容器
```bash
# 进入容器的 bash
docker-compose exec web bash

# 在容器内运行命令
docker-compose exec web python init_db.py
```

---

## 🔧 开发工作流

### 日常开发
1. 启动项目：`docker-compose up`
2. 修改代码（用 VS Code 等编辑器）
3. 刷新浏览器查看效果（代码自动生效）
4. 提交代码：`git add .` → `git commit` → `git push`

### 拉取最新代码
```bash
# 停止容器
docker-compose down

# 拉取代码
git pull

# 重新启动
docker-compose up
```

### 重置数据库
```bash
# 停止容器
docker-compose down

# 删除数据库文件
rm instance/greenlife.db

# 重新启动（会自动初始化数据库）
docker-compose up
```

---

## 🐛 常见问题

### 1. 端口被占用
**错误**：`Bind for 0.0.0.0:5001 failed: port is already allocated`

**解决**：
```bash
# 查找占用端口的进程
lsof -i :5001

# 停止进程
kill <PID>

# 或者修改 docker-compose.yml 中的端口
ports:
  - "5002:5001"  # 改成 5002
```

### 2. Docker Desktop 没启动
**错误**：`Cannot connect to the Docker daemon`

**解决**：打开 Docker Desktop 应用，等待启动完成

### 3. 代码修改不生效
**解决**：
```bash
# 重新构建镜像
docker-compose up --build
```

### 4. 权限问题（Mac/Linux）
**错误**：`Permission denied`

**解决**：
```bash
# 给文件夹添加权限
chmod -R 755 instance logs
```

---

## 📦 部署到虚拟机

### 方法 1：使用 Docker Compose（推荐）

**在虚拟机上：**
```bash
# 1. 安装 Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER

# 2. 克隆项目
git clone https://github.com/LittleJohn0601/software_project_2.git
cd software_project_2

# 3. 启动
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

### 方法 2：使用 Docker 镜像

**在本地打包：**
```bash
# 构建镜像
docker build -t peakshift:latest .

# 导出镜像
docker save -o peakshift.tar peakshift:latest

# 上传到虚拟机
scp peakshift.tar user@vm_ip:/home/user/
```

**在虚拟机上：**
```bash
# 加载镜像
docker load -i peakshift.tar

# 运行容器
docker run -d -p 5001:5001 \
  -v /home/user/data:/app/instance \
  --name peakshift-app \
  peakshift:latest

# 查看日志
docker logs peakshift-app
```

---

## 🎯 优势总结

### 开发阶段
✅ 一键启动，不用配置 Python 环境  
✅ 所有人环境完全一致（Mac/Windows）  
✅ 代码修改自动生效  
✅ 数据持久化，重启不丢失  

### 部署阶段
✅ 打包一次，到处运行  
✅ 不用担心虚拟机环境配置  
✅ 一条命令启动  
✅ 易于维护和更新  

---

## 📞 需要帮助？

遇到问题可以：
1. 查看日志：`docker-compose logs`
2. 查看容器状态：`docker-compose ps`
3. 联系团队成员

---

**最后更新**：2026-03-22
