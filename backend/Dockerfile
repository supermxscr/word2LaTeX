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
EXPOSE 8005
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
