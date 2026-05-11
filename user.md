# 本地直跑开发环境说明

这份文档用于在新的 Windows 电脑上，以“本地直跑”的方式启动和开发 `sport1.0.1` 项目，不使用 Docker。

## 1. 项目结构

项目分为两部分：

1. 后端：`backend`
2. 前端：`frontend`

后端技术栈：

1. `FastAPI`
2. `SQLAlchemy`
3. `MySQL`
4. `Pandas`
5. `OpenPyXL`

前端技术栈：

1. `Vue 3`
2. `Vite`
3. `Vue Router`
4. `Axios`

## 2. 本地直跑所需软件环境

新电脑建议安装以下软件：

1. `Git`
2. `Python 3.12`
3. `Node.js 20.x`
4. `npm`
5. `MySQL 8.0`
6. `PowerShell`

建议：

1. 项目目录尽量放在不含空格和中文的路径中，例如：`D:\Project_Engineering\sport1.0.1`
2. 如果电脑里已经装了旧版本 Python 或 Node，优先确认命令行里实际生效的版本

## 3. 后端 Python 依赖库

后端依赖文件：`backend/requirements.txt`

需要安装的库如下：

1. `fastapi==0.115.6`
2. `uvicorn[standard]==0.30.6`
3. `SQLAlchemy==2.0.36`
4. `pymysql==1.1.1`
5. `python-jose==3.3.0`
6. `passlib[bcrypt]==1.7.4`
7. `bcrypt==3.2.2`
8. `python-multipart==0.0.9`
9. `pydantic==2.9.2`
10. `pydantic-settings==2.5.2`
11. `email-validator==2.2.0`
12. `pandas==2.2.3`
13. `openpyxl==3.1.5`
14. `cryptography==42.0.8`

## 4. 前端 Node 依赖库

前端依赖文件：`frontend/package.json`

运行依赖：

1. `vue`
2. `vue-router`
3. `axios`

开发依赖：

1. `vite`
2. `@vitejs/plugin-vue`

## 5. 数据库环境依赖

项目本地直跑依赖 `MySQL 8.0`。

当前项目 `.env` 中使用到的数据库配置项如下：

1. `DB_USER`
2. `DB_PASSWORD`
3. `DB_HOST`
4. `DB_PORT`
5. `DB_NAME`
6. `MYSQL_ROOT_PASSWORD`
7. `MYSQL_DATABASE`
8. `MYSQL_USER`
9. `MYSQL_PASSWORD`

当前项目里的默认配置示例：

```env
DB_USER=root
DB_PASSWORD=123456789
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sport_system1.0.1

MYSQL_ROOT_PASSWORD=123456789
MYSQL_DATABASE=sport_system1.0.1
MYSQL_USER=root
MYSQL_PASSWORD=123456789
```

说明：

1. 本地开发时，后端主要使用的是 `DB_*` 这一组配置
2. `MYSQL_*` 这一组更多是给 `docker-compose` 使用
3. 新电脑如果不用 Docker，也建议保留这两组配置，避免后续切换运行方式时重复修改

## 6. 新电脑上的完整操作流程

### 6.1 拉取或复制项目代码

如果使用 Git：

```powershell
git clone <你的仓库地址>
cd D:\Project_Engineering\sport1.0.1
```

如果是直接拷贝项目文件夹：

1. 把整个项目目录复制到新电脑
2. 推荐放到：`D:\Project_Engineering\sport1.0.1`

### 6.2 配置数据库

1. 安装 `MySQL 8.0`
2. 启动 MySQL 服务
3. 确保本地能用 `root` 登录，或者改成你自己的用户名密码
4. 创建数据库：

```sql
CREATE DATABASE `sport_system1.0.1` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

5. 检查项目根目录下的 `.env` 是否和本机数据库一致

如果数据库用户名、密码或端口和当前 `.env` 不一致，就修改 `.env` 中这些值：

1. `DB_USER`
2. `DB_PASSWORD`
3. `DB_HOST`
4. `DB_PORT`
5. `DB_NAME`

### 6.3 创建并安装后端虚拟环境

在项目根目录执行：

```powershell
cd D:\Project_Engineering\sport1.0.1
python -m venv backend\.venv
```

激活虚拟环境：

```powershell
.\backend\.venv\Scripts\activate
```

如果 PowerShell 阻止激活脚本执行，可以先执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\backend\.venv\Scripts\activate
```

安装后端依赖：

```powershell
pip install -r backend\requirements.txt
```

建议升级一下基础工具：

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 6.4 安装前端依赖

打开新的终端窗口，执行：

```powershell
cd D:\Project_Engineering\sport1.0.1\frontend
npm install
```

### 6.5 启动后端

在后端终端中执行：

```powershell
cd D:\Project_Engineering\sport1.0.1\backend
..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

说明：

1. 这里使用 `python -m uvicorn` 方式启动，更稳一些
2. 可以避开 `uvicorn.exe` 在某些 Windows 路径下的启动器问题

启动成功后，后端地址为：

`http://127.0.0.1:8000`

### 6.6 启动前端

在前端终端中执行：

```powershell
cd D:\Project_Engineering\sport1.0.1\frontend
npm run dev
```

启动成功后，前端地址一般为：

`http://127.0.0.1:5173`

## 7. 推荐启动顺序

建议每次本地开发按这个顺序启动：

1. 先启动 `MySQL`
2. 再启动后端 `FastAPI`
3. 最后启动前端 `Vite`

## 8. 本地直跑验证清单

启动后可以按下面顺序检查：

1. 浏览器访问 `http://127.0.0.1:8000/docs`
2. 确认后端 Swagger 文档能打开
3. 浏览器访问 `http://127.0.0.1:5173`
4. 确认前端页面能打开
5. 尝试进入系统页面，检查接口是否正常返回数据

## 9. 常见问题

### 9.1 `uvicorn` 启动失败

如果你看到类似启动器报错，优先改用：

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

不要优先用：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 9.2 PowerShell 不允许执行激活脚本

执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

然后再激活虚拟环境。

### 9.3 MySQL 连不上

检查以下内容：

1. MySQL 服务是否启动
2. `.env` 中的用户名密码是否正确
3. `DB_HOST` 是否是 `127.0.0.1`
4. `DB_PORT` 是否是 `3306`
5. `DB_NAME` 对应数据库是否已经创建

### 9.4 前端接口请求失败

检查以下内容：

1. 后端是否已经启动在 `8000` 端口
2. 前端是否启动在 `5173` 端口
3. 浏览器控制台是否有跨域或网络报错

## 10. 不建议直接复制到新电脑的目录

以下目录可以不带过去，新电脑重新安装即可：

1. `backend\.venv`
2. `frontend\node_modules`
3. `frontend\dist`

## 11. 建议保留的关键文件

迁移到新电脑时，建议确保这些文件都在：

1. `.env`
2. `backend/requirements.txt`
3. `frontend/package.json`
4. `frontend/package-lock.json`
5. `docker-compose.yml`
6. `backend/app` 整个目录
7. `frontend/src` 整个目录

## 12. 一套最简本地直跑命令

后端：

```powershell
cd D:\Project_Engineering\sport1.0.1
python -m venv backend\.venv
.\backend\.venv\Scripts\activate
pip install -r backend\requirements.txt
cd backend
..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```powershell
cd D:\Project_Engineering\sport1.0.1\frontend
npm install
npm run dev
```
