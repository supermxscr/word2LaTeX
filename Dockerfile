# 从仓库根目录构建后端（供 Render 等未设置 Root Directory 时使用）
# 含 TeX Live + lmodern，支持「转换并预览 PDF」与 ZIP 内 main.pdf
FROM python:3.11-slim
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
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

ENV OUTPUT_PDF_DIR=/tmp/word2latex_pdfs
ENV PORT=8005
EXPOSE 8005
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8005}"]
