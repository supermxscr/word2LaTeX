# Word to LaTeX backend: Pandoc + optional TeX Live for PDF
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Optional: uncomment to enable PDF compile in jobs
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     texlive-latex-base texlive-latex-extra latexmk \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV OUTPUT_PDF_DIR=/tmp/word2latex_pdfs
ENV PORT=8005
EXPOSE 8005
# Render 会注入 PORT，用 shell 形式以读取环境变量
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8005}"]
