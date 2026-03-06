# EM_PM_LaTeX_Guide.pdf 规范对照说明

当前「Aries EM」预设（`backend/presets/aries_em.json` + `backend/converter/postprocess.py`）**按根目录 `EM_PM_LaTeX_Guide.pdf` 中的 EM/PM 提交规范**做了对齐，具体如下。

## 已实现的规范（与 PDF 一致）

| PDF 规范 | 实现位置 | 说明 |
|----------|----------|------|
| **禁止子目录** | 后处理 + ZIP | 所有文件须在同一层级；`\includegraphics` 只保留文件名、去掉路径；ZIP 内仅平铺单层（`main.tex`）。 |
| **保留文件名禁用** | `postprocess.py` `_RESERVED` | CON, PRN, AUX, NUL, COM1–COM9, LPT1–LPT9；若图片等引用到这类名会替换为 `file_xxx`。 |
| **文件名仅一个英文句点** | `_safe_basename()` | 扩展名只保留一个点；含特殊字符的会替换为 `_`，避免如 `G+.eps` 被 EM 拒绝。 |
| **图片引用不得含路径** | `normalize_includegraphics_paths()` | 将 `\includegraphics{path/to/fig.png}` 改为 `\includegraphics{fig.png}`，与 PDF 中 “correctly referenced image” 示例一致。 |
| **ZIP 内无子文件夹** | `main.py` 打 ZIP | 使用 Pandoc `--extract-media` 从 Word 提取图片，与 `main.tex` 一起**扁平**写入 ZIP（无 media/ 等子目录），符合 “subfolders within a zip file interfere with the PDF building process”。 |
| **文档类与常用包** | `aries_em.json` | `article`、graphicx/amsmath/hyperref 等，与 EM 常用环境兼容；可选 XeLaTeX/Biber 首行指令（预设中默认关闭）。 |

## 部分依赖 Pandoc / 未单独实现的点

- **文件上传顺序**（主 .tex → .bib → .sty → 图）：PDF 建议的是在 EM 网页上传时的顺序。本工具输出为**单文件 .tex 或单层 ZIP**，用户若在 EM 上传多文件需自行按该顺序排列。
- **参考文献**：预设里可配 `bibliography_style`；实际 .bib 内容由 Pandoc 从 Word 解析，若 Word 中无引用则不会生成 .bib，符合“按需”逻辑。
- **公式**：对 Pandoc 输出的常见问题做了简单后处理（如 `\deltat` → `\delta t`），与 PDF 中 “Bad math environment delimiter” 等 FAQ 相呼应；复杂公式仍以 Pandoc 为准。
- **.sty 数量**：PDF 建议仅一个 style file；当前预设只注入通用包，不自动加入期刊专用 .sty，需期刊提供时由用户自备。

## 未实现的规范（或由环境决定）

- **EM 保留文件名扩展名**（如 `NUL.txt`）：当前仅对“无扩展名”的保留名做了替换，对“保留名 + 任意扩展名”的严格禁止未在代码里强制（实际很少出现）。
- **图片格式**：PDF 支持 .png/.pdf/.jpg/.eps 等；预设中 `image_format` 仅影响命名偏好，未做格式转换或校验。
- **hyperref dvips**：若某模板带 `dvips` 会导致 DVI 错误；PDF 建议改为 `%dvips`。当前未对现成 .tex 做此替换（Pandoc 默认产出多为 pdftex 友好）。

**结论**：当前转换与打包逻辑**按照 EM_PM_LaTeX_Guide.pdf 的核心提交要求**（单层结构、无子目录、文件名与图片引用规范）实现；其余多为 EM 站点操作或期刊特定要求，本工具在预设中做了兼容，未逐条硬编码。
