# 校体育管理系统

框架：
- 前端：Vue 3 + Vite
- 后端：FastAPI + MySQL

## 运行方式（Docker）

1. 确保已安装 Docker 和 Docker Compose。
2. 在项目根目录执行：
```bash
docker compose up --build
```
3. 访问：
   - 前端：`http://localhost:5173`
   - 后端：`http://localhost:8000`

## 运行方式（开发模式，非 Docker）

### 后端

1. 创建并激活虚拟环境（任选其一）：
```bash
python -m venv .venv
.\.venv\Scripts\activate
```
2. 安装依赖：
```bash
pip install -r backend/requirements.txt
```
3. 配置数据库：
   - 安装并启动本地 MySQL
   - 新建数据库 `sport`
   - 在项目根目录 `.env` 中填写数据库连接信息
4. 启动后端：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

1. 安装依赖：
```bash
cd frontend
npm install
```
2. 启动开发服务器：
```bash
npm run dev
```
3. 访问前端：
   - `http://localhost:5173`

## 账号流程

- 首次登录需注册邮箱。
- 支持通过邮箱修改密码（示例实现，不含真实邮件发送）。

## 模块说明

1. 运动员管理
   - Excel 导入/导出（表头需匹配：学院、姓名、学号、性别、项目、组别、成绩、排名、积分、电话）
   - 支持查询、修改、增加、删除（API 已提供）

2. 分组管理
   - 预设多轮次项目：100米、200米、400米、4*100米
   - 混合项目：4*200米、混合4*100米
   - 分组采用“同学院优先分散”策略，自动分组与随机分道
   - 支持保存分组，写回运动员信息表中的组别字段

3. 项目管理
   - 初始化表：自动统计参加人数、历史最高纪录、最高纪录保持者

4. 成绩管理
   - 按项目、学号录入成绩，并写回分组表与个人信息表
   - 决赛成绩自动计算排名并回填

5. 排名管理
   - 个人排名：按名次计分（1-10、2-8、3-6、4-5、5-4、6-3、7-2、8-1），破纪录额外 +9
   - 学院排名：统计项目数量、参加人数、学院总积分

## API 概览

- `POST /auth/register` 注册
- `POST /auth/login` 登录
- `POST /auth/reset-password` 修改密码

- `GET /athletes` 查询运动员
- `POST /athletes` 新增运动员
- `PUT /athletes/{id}` 修改运动员
- `DELETE /athletes/{id}` 删除运动员
- `POST /athletes/import` 导入 Excel
- `GET /athletes/export` 导出 Excel

- `POST /groups/generate` 生成分组
- `POST /groups/confirm` 保存分组
- `GET /export/groups` 导出分组表

- `POST /events/initialize` 初始化项目表
- `GET /events/list` 查询项目表
- `GET /export/events` 导出项目表

- `POST /results/submit` 录入成绩
- `POST /results/initialize` 初始化成绩表
- `GET /results/list` 查询成绩表
- `GET /export/results` 导出成绩表

- `POST /rankings/personal/initialize` 初始化个人排名
- `GET /rankings/personal/list` 查询个人排名
- `GET /export/personal-rankings` 导出个人排名

- `POST /rankings/college/initialize` 初始化学院排名
- `GET /rankings/college/list` 查询学院排名
- `GET /export/college-rankings` 导出学院排名

## 说明与可调项

- 排名规则中“距离类项目成绩越大越好”的判断使用项目名关键词（跳、掷、远、高、铅球）。
- 邮箱注册与修改密码仅做流程示例，未接入真实邮件服务。
