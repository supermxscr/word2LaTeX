# Word to LaTeX backend: Pandoc + TeX Live（支持转换并预览 PDF、ZIP 内带 PDF）
FROM python:3.11-slim
# 安装 lmodern 等字体：texlive-latex-recommended 含 Latin Modern，避免缓存可改下方注释
ARG CACHEBUST=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    latexmk \
    && rm -rf /var/lib/apt/lists/* \
    && kpsewhich lmodern.sty || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV OUTPUT_PDF_DIR=/tmp/word2latex_pdfs
ENV PORT=8005
EXPOSE 8005
# Render 会注入 PORT，用 shell 形式以读取环境变量
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8005}"]
