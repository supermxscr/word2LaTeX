This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## 环境变量

- `NEXT_PUBLIC_API_URL`：后端 API 地址。本地开发不设则默认 `http://localhost:8005`；生产环境（Vercel）需在 **Settings → Environment Variables** 中设置为 `https://word2latex.onrender.com`（或实际后端域名）。可参考 `.env.example`。

## Deploy on Vercel

部署时在 Vercel 项目 **Settings → Environment Variables** 添加：

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://word2latex.onrender.com` |

保存后重新部署，前端（如 https://word2-latex.vercel.app）会请求该后端。
