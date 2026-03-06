# Word to LaTeX Backend

FastAPI + Pandoc conversion API with format presets (e.g. Aries EM).

## Setup

- Python 3.11+
- [Pandoc](https://pandoc.org/) installed and on PATH
- （可选）若需「转换并预览」生成 PDF：本机安装 TeX Live

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 安装 TeX Live（用于 PDF 预览）

- **macOS**  
  - 完整版（约 4GB）：`brew install --cask mactex`  
  - 或从 [MacTeX](https://www.tug.org/mactex/) 下载安装包。  
  - 安装后新开终端，确认 `pdflatex`、`latexmk` 在 PATH 中。

- **Ubuntu / Debian**  
  ```bash
  sudo apt-get update && sudo apt-get install -y texlive-latex-base texlive-latex-extra latexmk
  ```

- **Windows**  
  安装 [MiKTeX](https://miktex.org/) 或 [TeX Live](https://www.tug.org/texlive/)，安装程序会配置 PATH。

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

- `GET /presets` — list presets
- `POST /convert` — upload .docx, get zip with main.tex、媒体文件及 main.pdf（若编译成功）
- `POST /convert/tex` — upload .docx, get raw .tex
- `POST /convert/preview` — upload .docx, returns JSON `{ tex_content, pdf_base64?, compile_log? }`（一步生成 LaTeX + PDF，需本机安装 TeX Live 才有 PDF）

## Presets

Presets live in `presets/*.json`. Default: `aries_em` (Editorial Manager).

## EM/PM LaTeX 规范（参考 EM_PM_LaTeX_Guide.pdf）

- **字体**：规范中**未**对正文/文档字体（如 Times、Computer Modern）做要求。仅有一处与字体相关：**EPS 图片中不得使用嵌入字体**（"Can I use embedded fonts in an EPS image file? No."），上传前需移除或改为 PDF 等格式。
- 其余要求：单层目录（无子文件夹）、保留文件名限制等见 `converter/postprocess.py` 与文档。
