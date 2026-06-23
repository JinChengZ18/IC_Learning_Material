# -*- coding: utf-8 -*-
"""真实成稿校对：用 LibreOffice 把 .pptx 渲染成 PDF，再用 PyMuPDF 渲成逐页 PNG。
这是「真正 PowerPoint 长什么样」的校对（matplotlib 预览只是近似，字体/换行/自动缩字号会差一点）。
用法：python tools/pptx_qa.py [pptx]  →  <pptx 同级>/_qa/qa_NN.png
依赖：LibreOffice（soffice）+ PyMuPDF。"""
import sys
import os
import subprocess

DEFAULT_PPTX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "..", "IC_Backend_Notes", "slides", "05_Floorplan.pptx")
SOFFICE_CANDS = [r"C:\Program Files\LibreOffice\program\soffice.exe",
                 r"C:\Program Files (x86)\LibreOffice\program\soffice.exe", "soffice"]


def _soffice():
    for c in SOFFICE_CANDS:
        if c == "soffice" or os.path.isfile(c):
            return c
    return "soffice"


def render(pptx, dpi=120):
    import fitz  # PyMuPDF
    pptx = os.path.abspath(pptx)
    out = os.path.join(os.path.dirname(pptx), "_qa")
    os.makedirs(out, exist_ok=True)
    subprocess.run([_soffice(), "--headless", "--convert-to", "pdf", "--outdir", out, pptx],
                   check=False, capture_output=True)
    pdf = os.path.join(out, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    doc = fitz.open(pdf)
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(matrix=mat).save(os.path.join(out, f"qa_{i:02d}.png"))
    print(f"rendered {len(doc)} pages -> {out}  (真实 PowerPoint 成稿)")
    return out


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PPTX)
