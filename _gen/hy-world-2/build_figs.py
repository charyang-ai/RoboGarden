"""Figures for the HY-World 2.0 note. Numbers are the W7900 runs in charyang-ai/hy-world-2.0-mac-rocm results/;
the Radeon 8060S figure is from Vladimir Talyzin's README in the same repository.

Reads HW2_REPO (default: PhysicalAI/RadeonGarden/hy-world-2.0-mac-rocm next to this repository).
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "images"
OUT.mkdir(parents=True, exist_ok=True)
REPO = Path(os.environ.get("HW2_REPO", HERE.parents[2] / "RadeonGarden" / "hy-world-2.0-mac-rocm"))
PANO = REPO / "results" / "pano_multi"
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

font_manager.fontManager.addfont(FONT)
plt.rcParams.update(
    {
        "font.family": "Microsoft YaHei",
        "axes.unicode_minus": False,
        "figure.facecolor": "#f3efe6",
        "savefig.facecolor": "#f3efe6",
        "axes.facecolor": "#fffdf8",
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
PAPER_BG = (243, 239, 230)


def jpeg(img: Image.Image, name: str, max_w: int = 1600) -> None:
    img = img.convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.Resampling.LANCZOS)
    img.save(OUT / name, quality=88, optimize=True)


def pictures() -> None:
    # Three cards, CFG parallel, untiled VAE decode: 1952x960, 40 steps, seed 42, upstream's Landmark photo.
    jpeg(Image.open(PANO / "g3_1952x960_s40_notile.png"), "hw2-pano.jpg")


def sky(lang: str) -> None:
    """The same patch of sky, 2x nearest-neighbour: tiled decode (2 cards) above, untiled (3 cards) below."""
    labels = {"zh": ("分块解码（移植在 ROCm 上的默认）", "不分块（多卡时的新默认）"),
              "en": ("tiled decode (the port's ROCm default)", "untiled (the new default when split)")}[lang]
    crop = (700, 40, 1100, 240)
    tiled = Image.open(PANO / "g2_1952x960_s40.png").convert("RGB").crop(crop).resize((800, 400), Image.NEAREST)
    plain = Image.open(PANO / "g3_1952x960_s40_notile.png").convert("RGB").crop(crop).resize((800, 400), Image.NEAREST)
    head = 46
    sheet = Image.new("RGB", (800, 2 * (400 + head) + 12), PAPER_BG)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 24)
    for i, (img, text) in enumerate(((tiled, labels[0]), (plain, labels[1]))):
        y = i * (400 + head + 12)
        draw.text((6, y + 9), text, fill=INK, font=font)
        sheet.paste(img, (0, y + head))
    sheet.save(OUT / ("hw2-sky.jpg" if lang == "zh" else "hw2-sky_en.jpg"), quality=90)


def timing(lang: str) -> None:
    t = {
        "zh": {
            "left": "全景图：1952×960，每步秒数",
            "right": "重建：Park_Stone 32 张照片，推理秒数",
            "bars": ["Radeon 8060S\n（统一内存）", "W7900 ×2", "W7900 ×3\nCFG 并行", "W7900 ×4\nCFG 并行"],
            "cards": ["1 张卡", "2 张卡", "4 张卡"],
            "note": "8060S 的数字来自 Vladimir Talyzin 的 README；W7900 的数字来自这次运行。",
        },
        "en": {
            "left": "Panorama, 1952×960: seconds per step",
            "right": "Reconstruction, Park_Stone (32 photos): inference seconds",
            "bars": ["Radeon 8060S\n(unified memory)", "W7900 ×2", "W7900 ×3\nCFG parallel", "W7900 ×4\nCFG parallel"],
            "cards": ["1 card", "2 cards", "4 cards"],
            "note": "The 8060S figure is from Vladimir Talyzin's README; the W7900 figures are from this run.",
        },
    }[lang]
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.4, 5.0), dpi=160, gridspec_kw={"width_ratios": [1.35, 1]})
    pano = [38.0, 13.15, 6.86, 6.77]
    bars = a.bar(range(4), pano, 0.62, color=[SAND, GREEN, GREEN, GREEN], zorder=2)
    for bar, v in zip(bars, pano):
        a.text(bar.get_x() + bar.get_width() / 2, v + 0.8, f"{v:g}", ha="center", fontsize=11)
    a.set_xticks(range(4), t["bars"], fontsize=10)
    a.set_ylim(0, 44)
    a.set_title(t["left"], fontsize=13, loc="left", pad=10)
    recon = [8.44, 10.26, 11.19]
    bars = b.bar(range(3), recon, 0.55, color=[GREEN, CLAY, CLAY], zorder=2)
    for bar, v in zip(bars, recon):
        b.text(bar.get_x() + bar.get_width() / 2, v + 0.25, f"{v:g}", ha="center", fontsize=11)
    b.set_xticks(range(3), t["cards"], fontsize=10.5)
    b.set_ylim(0, 13)
    b.set_title(t["right"], fontsize=13, loc="left", pad=10)
    for ax in (a, b):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.grid(True, color=LINE, lw=0.8)
        ax.set_axisbelow(True)
    fig.text(0.01, 0.01, t["note"], fontsize=9.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / ("hw2-timing.png" if lang == "zh" else "hw2-timing_en.png"))
    plt.close(fig)


if __name__ == "__main__":
    pictures()
    for lang in ("zh", "en"):
        sky(lang)
        timing(lang)
    print(OUT)
