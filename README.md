# Word 一键转 LaTeX

将 Word (.docx) 按期刊/格式预设一键转换为 LaTeX，支持 Aries Systems (Editorial Manager) 等预设。

## 结构

- **frontend/** — Next.js 16 + shadcn/ui，部署于 Vercel
- **backend/** — FastAPI + Pandoc，部署于 Railway/Render
- **EM_PM_LaTeX_Guide.pdf** — Aries EM 提交规范参考

## 本地开发

### 后端

需要 Python 3.11+ 与 [Pandoc](https://pandoc.org/)。

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8005
```

- 同步转换：`POST /convert`（返回 zip）、`POST /convert/tex`（返回 .tex 预览）
- 异步任务（需 Redis）：设置 `REDIS_URL`，运行 `rq worker`，使用 `POST /jobs` 与 `GET /jobs/:id`，可选 `compile_pdf=true` 生成 PDF

### 前端

```bash
cd frontend
npm install
npm run dev
```

设置 `NEXT_PUBLIC_API_URL=http://localhost:8005`（或后端地址）。

## 部署

- **前端**：Vercel 连接本仓库，根目录选 `frontend`，配置 `NEXT_PUBLIC_API_URL` 为后端地址
- **后端**：Railway 或 Render 连接本仓库，根目录选 `backend`，使用自带 Dockerfile（内装 Pandoc）；需 TeX Live 时在 Dockerfile 中取消注释 latexmk 相关行；异步任务需提供 Redis 并运行 RQ worker

## 预设

默认内置 **Aries EM** 预设（`presets/aries_em.json`）：扁平 zip、无子目录、文件名与图片引用符合 EM 规范。可在此目录增加更多 JSON 预设并在前端下拉中选择。
