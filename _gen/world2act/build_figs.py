"""Figures and the clip for the World2Act note, in Chinese and English. Numbers are the W7900 run in charyang-ai/world2act.

Reads W2A_RESULTS (default: PhysicalAI/RadeonGarden/world2act/results next to this repository) for robocasa.mp4,
and W2A_PAPER (default: _gen/zhihu-series/images/world2act) for the three figures from the project page.
"""

import os
import shutil
import subprocess
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "images"
OUT.mkdir(parents=True, exist_ok=True)
REPO = HERE.parents[1]
RESULTS = Path(os.environ.get("W2A_RESULTS", REPO.parent / "RadeonGarden" / "world2act" / "results"))
PAPER = Path(os.environ.get("W2A_PAPER", REPO / "_gen" / "zhihu-series" / "images" / "world2act"))
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

font_manager.fontManager.addfont(FONT)
plt.rcParams.update(
    {
        "font.family": "Microsoft YaHei",
        "axes.unicode_minus": False,
        "figure.facecolor": "#f3efe6",
        "savefig.facecolor": "#f3efe6",
        "axes.facecolor": "#f3efe6",
        "axes.edgecolor": "#1c1914",
        "axes.labelcolor": "#1c1914",
        "xtick.color": "#1c1914",
        "ytick.color": "#1c1914",
        "text.color": "#1c1914",
    }
)

INK = "#1c1914"
GREEN = "#1c4f3e"
CLAY = "#9a4e2c"
MUTED = "#5e584e"
SAND = "#c9bda6"
LINE = "#e2d8c6"
PAPER_HEX = "#f3efe6"
PAPER_BG = (243, 239, 230)


def paper_figs() -> None:
    for name in ("w2a-motivation.jpg", "w2a-method.jpg", "w2a-imagine-vs-real.jpg"):
        shutil.copy2(PAPER / name, OUT / name)


def frame_strip(lang: str, frames=(0, 8, 16, 40, 72, 92), cols: int = 3, tile_w: int = 600) -> None:
    cap = cv2.VideoCapture(str(RESULTS / "robocasa.mp4"))
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    tiles = []
    for n in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ok, bgr = cap.read()
        if not ok:
            raise SystemExit(f"cannot read frame {n}")
        im = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        tiles.append((n, n / fps, im.resize((tile_w, round(im.height * tile_w / im.width)), Image.Resampling.LANCZOS)))
    cap.release()
    gap, label_h = 14, 46
    tile_h = tiles[0][2].height
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w + (cols + 1) * gap, rows * (tile_h + label_h) + (rows + 1) * gap), PAPER_BG)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 26)
    for i, (n, t, im) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = gap + c * (tile_w + gap)
        y = gap + r * (tile_h + label_h + gap)
        label = f"第 {n} 帧 · {t:.2f} 秒" if lang == "zh" else f"frame {n} · {t:.2f} s"
        draw.text((x + 4, y + 6), label, fill=INK, font=font)
        sheet.paste(im, (x, y + label_h))
    sheet.save(OUT / ("frame-w2a-mango.jpg" if lang == "zh" else "frame-w2a-mango_en.jpg"), quality=90, optimize=True)


def memory_chart(lang: str) -> None:
    live, reserved, free_contig, need, card = 8.7, 24.7, 14.0, 25.63, 48.0
    t = {
        "zh": {
            "title": "25.6 GiB 是一张乘法表：因果 VAE 一层卷积要物化的 im2col",
            "formula": "96（输入通道）× 27（3×3×3 卷积核）× 16 × 432 × 768（输出的时间×高×宽）× 2 字节（bf16）≈ 25.63 GiB",
            "live": "活张量\n8.7",
            "reserved": "已保留、未占用 24.7\n（上一层的展开表还占着）",
            "free": "连续空闲\n14",
            "need": "下一层再要 25.6 → 放不下",
            "table": "这一层的展开表 25.6",
            "empty": "空闲",
            "card": "卡的容量 48 GiB",
            "rows": ["改之前：\n出错那一刻", "改之后：卷积前\nempty_cache()"],
            "x": "显存（GiB）",
            "foot": "数字来自这次运行的显存报告；第二条按同一时刻的活张量示意。T5-11B 此时已回到 CPU。",
        },
        "en": {
            "title": "25.6 GiB is a multiplication: the im2col one causal-VAE convolution materializes",
            "formula": "96 (input channels) × 27 (3×3×3 kernel) × 16 × 432 × 768 (output time × height × width) × 2 bytes (bf16) ≈ 25.63 GiB",
            "live": "live\n8.7",
            "reserved": "reserved, unused 24.7\n(the previous layer's table)",
            "free": "contiguous\nfree 14",
            "need": "the next layer asks for 25.6 → does not fit",
            "table": "this layer's table 25.6",
            "empty": "free",
            "card": "card capacity 48 GiB",
            "rows": ["before: the\nmoment it fails", "after: empty_cache()\nbefore the conv"],
            "x": "GPU memory (GiB)",
            "foot": "Numbers from this run's memory report; the second bar uses the live tensors of the same moment. T5-11B is back on the CPU by then.",
        },
    }[lang]
    fig, ax = plt.subplots(figsize=(12.8, 5.6), dpi=150)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.74, bottom=0.17)
    fig.text(0.03, 0.93, t["title"], fontsize=16.5, weight="bold", color=INK)
    fig.text(0.03, 0.855, t["formula"], fontsize=11.5, color=MUTED)
    y1, y2, h = 1.0, 0.0, 0.5
    ax.barh(y1, live, h, color=GREEN, ec=PAPER_HEX)
    ax.barh(y1, reserved, h, left=live, color=SAND, ec=PAPER_HEX)
    ax.barh(y1, free_contig, h, left=live + reserved, color=LINE, ec=PAPER_HEX)
    ax.text(live / 2, y1, t["live"], ha="center", va="center", fontsize=11, color="white", weight="bold")
    ax.text(live + reserved / 2, y1, t["reserved"], ha="center", va="center", fontsize=11, color=INK)
    ax.text(live + reserved + free_contig / 2, y1, t["free"], ha="center", va="center", fontsize=11, color=INK)
    start = live + reserved
    ax.add_patch(Rectangle((start, y1 + h / 2 + 0.06), need, 0.2, fc="none", ec=CLAY, lw=2.2, ls="--"))
    ax.text(start + need / 2, y1 + h / 2 + 0.16, t["need"], ha="center", va="center", fontsize=11, color=CLAY, weight="bold")
    ax.barh(y2, live, h, color=GREEN, ec=PAPER_HEX)
    ax.barh(y2, need, h, left=live, color=CLAY, ec=PAPER_HEX)
    ax.barh(y2, card - live - need, h, left=live + need, color=LINE, ec=PAPER_HEX)
    ax.text(live / 2, y2, t["live"], ha="center", va="center", fontsize=11, color="white", weight="bold")
    ax.text(live + need / 2, y2, t["table"], ha="center", va="center", fontsize=11, color="white", weight="bold")
    ax.text(live + need + (card - live - need) / 2, y2, t["empty"], ha="center", va="center", fontsize=11, color=MUTED)
    ax.axvline(card, color=INK, lw=1.4, ls=":")
    ax.text(card + 0.4, -0.42, t["card"], fontsize=10.5, color=INK, va="center")
    ax.set_yticks([y1, y2], t["rows"], fontsize=11.5)
    ax.set_xlim(0, 62)
    ax.set_ylim(-0.5, 1.75)
    ax.set_xlabel(t["x"], fontsize=11.5)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.text(0.03, 0.03, t["foot"], fontsize=10, color=MUTED)
    fig.savefig(OUT / ("w2a-memory.png" if lang == "zh" else "w2a-memory_en.png"))
    plt.close(fig)


def clip() -> None:
    # The run's output: conditioning image + "pick the mango from the cabinet", 93 frames at 16 fps.
    mp4 = OUT / "w2a-robocasa.mp4"
    shutil.copy2(RESULTS / "robocasa.mp4", mp4)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "3", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                    str(OUT / "frame-w2a-robocasa.jpg")], check=True)


if __name__ == "__main__":
    paper_figs()
    for lang in ("zh", "en"):
        frame_strip(lang)
        memory_chart(lang)
    clip()
    print(OUT)
