# -*- coding: utf-8 -*-
"""文献插图提取流水线（pipeline 第 1 步）：从 PDF（如 IC_Backend_Notes/lectures/*.pdf）
提取**嵌入的位图**插图，供 PPT 在「恰当处」引用以增强说明力——务必在使用处标注参考文献。

设计取舍：只提取**嵌入位图**（真实照片 / 版图截图 / IR 颜色图等），矢量框图不在此列
（那些简单框图已用 deck 的原生形状重画，见 deck.DIAGRAMS）。这样提取出来的，恰好是
「程序画不出、值得引用的真图」。

用法：
    python tools/extract_figs.py <pdf> [out_dir] [min_w] [min_h]
例：
    python tools/extract_figs.py ../IC_Backend_Notes/lectures/Lecture-6-Import-Design-and-Floorplan.pdf

产物：<out_dir>/pNN_xNN.png + manifest.csv（页码 / xref / 宽 / 高 / 文件名），便于挑选。
默认 out_dir = <pdf 同级>/lit/<pdf 名>/。

⚠️ 版权：提取出的图片版权属原作者 / 原始来源（课程讲义本身也多处转引 Cadence / Rabaey /
CMOS VLSI Design 等）。**仅供个人学习**，使用时必须在图旁标注来源（见 slides.py 的
credit= 与 refs 页），且**不要随仓库分发**——`assets/**/lit/` 已在 .gitignore 忽略。

依赖：PyMuPDF（`pip install pymupdf`）。
"""
import sys
import os
import csv


def extract(pdf, out_dir=None, min_w=200, min_h=140):
    import fitz  # PyMuPDF
    doc = fitz.open(pdf)
    base = os.path.splitext(os.path.basename(pdf))[0]
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(pdf)), "lit", base)
    os.makedirs(out_dir, exist_ok=True)
    rows, seen = [], set()
    for pno in range(len(doc)):
        for img in doc.get_page_images(pno, full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception:
                continue
            if pix.width < min_w or pix.height < min_h:     # 跳过图标 / 小装饰
                pix = None
                continue
            if pix.n - pix.alpha >= 4:                       # CMYK/其它 → RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
            name = f"p{pno + 1:02d}_x{xref}.png"
            pix.save(os.path.join(out_dir, name))
            rows.append((pno + 1, xref, pix.width, pix.height, name))
            pix = None
    with open(os.path.join(out_dir, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["page", "xref", "w", "h", "file"])
        w.writerows(rows)
    print(f"extracted {len(rows)} bitmap figs -> {out_dir}")
    print("[!] 版权属原始来源；仅供个人学习、使用处须标注参考文献、勿随仓库分发（lit/ 已 gitignore）。")
    return out_dir


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    a = sys.argv
    extract(a[1], a[2] if len(a) > 2 else None,
            int(a[3]) if len(a) > 3 else 200, int(a[4]) if len(a) > 4 else 140)
