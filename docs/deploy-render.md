# 在 Render 上部署后端

将 Word→LaTeX 后端（FastAPI + Pandoc）部署到 [Render](https://render.com)。

## 一、需要修改的代码（已完成）

以下已在本仓库中改好，无需你再改：

1. **CORS**：`backend/main.py` 从环境变量 `CORS_ORIGINS` 读取允许的前端域名（逗号分隔），便于生产环境填写前端地址。
2. **端口**：`backend/Dockerfile` 使用 `PORT` 环境变量（Render 自动注入），启动命令为 `uvicorn ... --port ${PORT:-8005}`。

## 二、部署步骤

### 1. 准备 GitHub 仓库

确保代码已推送到 GitHub（例如 `supermxscr/word2LaTeX`）。

### 2. 在 Render 创建 Web Service

1. 打开 [Render Dashboard](https://dashboard.render.com/) 并登录。
2. 点击 **New +** → **Web Service**。
3. **Connect a repository**：若未连过 GitHub，先连接账号并选择 `supermxscr/word2LaTeX`（或你的 fork）。
4. 选择仓库 **word2LaTeX**，点击 **Connect**。

### 3. 配置服务

| 配置项 | 值 |
|--------|-----|
| **Name** | 随意，如 `word2latex-api` |
| **Region** | 选离你/用户近的（如 Singapore） |
| **Root Directory** | 留空（用 Docker 时见下） |
| **Runtime** | **Docker** |
| **Dockerfile Path** | 若 Root 留空填：`backend/Dockerfile`；若 Root 填 `backend` 则填：`Dockerfile` |
| **Docker Context** | 若 Root 留空填：`backend`；若 Root 填 `backend` 可留空 |

更简单的一种：

- **Root Directory** 填：`backend`
- **Runtime**：Docker  
  → Render 会在 `backend` 下找 `Dockerfile`，无需再填路径。

### 4. 环境变量（Environment）

在 **Environment** 里添加：

| Key | Value | 说明 |
|-----|--------|------|
| `CORS_ORIGINS` | 你的前端访问地址 | 本仓库前端：`https://word2-latex.vercel.app`。多个用逗号分隔，不要加空格。 |

本仓库前端已部署在 **https://word2-latex.vercel.app**，请将 `CORS_ORIGINS` 设为该地址。若暂时只做 API 测试可不填；不填时仅允许 `http://localhost:3000`（本地前端）。

### 5. 实例类型与限制

- **Free**：服务一段时间无请求会 sleep，首请求会冷启动几秒；有带宽与时长限制。
- **Starter（付费）**：常驻、无 sleep，适合正式使用。

按需选择后点击 **Create Web Service**。

### 6. 等待构建与运行

- Render 会用 `backend/Dockerfile` 构建镜像（安装 Python、Pandoc 等），首次约 2–5 分钟。
- 构建完成后服务会启动，日志里看到类似 `Uvicorn running on ...` 即正常。

### 7. 获取后端地址

在服务详情页的 **Settings** 或顶部可以看到 **URL**，例如：

- `https://word2latex-api.onrender.com`

用浏览器访问该 URL，应看到：

```json
{"service":"word2latex","status":"ok"}
```

### 8. 前端接上后端

在前端项目里把 API 基地址设为 Render 的 URL，例如：

- **Next.js**：在 Vercel 的 **Environment Variables** 中设置  
  `NEXT_PUBLIC_API_URL=https://你的Render服务名.onrender.com`  
  （例如 `https://word2latex-api.onrender.com`），这样 https://word2-latex.vercel.app 会请求你的 Render 后端。

重新构建/部署前端后，即可在线上用前端调 Render 上的后端。

## 三、注意事项

1. **Pandoc**：当前 Dockerfile 已安装 Pandoc，Word→LaTeX 转换可用。**PDF 编译**（预览/下载 PDF）未在 Dockerfile 中安装 TeX Live，因此：
   - 在 Render 上 **转换并预览 PDF**、**ZIP 内带 PDF** 会失败或只得到 LaTeX；
   - 若要在 Render 上也能出 PDF，需在 Dockerfile 中取消注释 TeX Live 安装（镜像会变大、构建更慢）。
2. **请求超时**：大文档或复杂排版时，/convert 与 /convert/preview 可能较慢；Free 实例有请求超时限制，长时间转换建议用付费实例或本地/自建。
3. **CORS**：前端若部署在不同域名，务必在 Render 的 `CORS_ORIGINS` 中加上该域名（如 Vercel 的地址），否则浏览器会拦请求。

## 四、使用 Blueprint（可选）

仓库根目录有 `render.yaml`，在 Render 里可以：

1. **New +** → **Blueprint**。
2. 连接同一 GitHub 仓库。
3. Render 会按 `render.yaml` 创建 Web Service，你只需在 Dashboard 里补填 `CORS_ORIGINS` 等环境变量即可。
