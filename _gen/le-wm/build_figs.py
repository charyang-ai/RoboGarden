"""Figures and clips for the LeWorldModel note. Numbers are the W7900 runs in charyang-ai/le-wm results/.

Reads LEWM_RESULTS (default: PhysicalAI/RadeonGarden/le-wm/results next to this repository).
"""

import os
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = Path(os.environ.get("LEWM_RESULTS", Path(__file__).resolve().parents[3] / "RadeonGarden" / "le-wm" / "results"))
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
FONT = r"C:\Windows\Fonts\msyh.ttc"

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


def results() -> None:
    envs = ["Two-Room", "Push-T", "OGBench-Cube", "Reacher"]
    paper = [87, 96, 74, 86]
    # Released checkpoints on the W7900; Two-Room and Reacher are the mean of seeds 42, 1 and 2 (150 episodes).
    released = [88.7, 94, 68, 79.3]
    trained = [93.3, None, None, None]  # Two-Room from scratch, 10 epochs, three seeds
    random = [26.7, 6, 48, 4]
    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=160)
    w = 0.26
    xs = range(len(envs))
    b1 = ax.bar([x - w for x in xs], paper, w, color=SAND, label="论文", zorder=2)
    b2 = ax.bar(list(xs), released, w, color=GREEN, label="W7900，作者发布的权重", zorder=2)
    b3 = ax.bar([-0 + w], [trained[0]], w, color=CLAY, label="W7900，从头训练", zorder=2)
    for bars, vals in ((b1, paper), (b2, released), (b3, trained[:1])):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1.2, f"{v:g}", ha="center", fontsize=11, color=INK)
    for x, r in zip(xs, random):
        ax.plot([x - 1.5 * w, x + 1.5 * w], [r, r], color=MUTED, lw=1.4, ls=(0, (3, 2)), zorder=3)
    ax.plot([], [], color=MUTED, lw=1.4, ls=(0, (3, 2)), label="随机策略（W7900）")
    ax.set_xticks(list(xs), envs, fontsize=12)
    ax.set_ylim(0, 116)
    ax.set_ylabel("规划成功率（%）", fontsize=13)
    ax.set_title("同一份考卷：50 回合，起点和目标取自数据集，目标在 25 步之外", fontsize=15, pad=12, loc="left")
    ax.legend(frameon=False, fontsize=11, ncol=4, loc="upper left", bbox_to_anchor=(0, 1.0))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=LINE, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "lewm-results.png")
    plt.close(fig)


def reacher_floor() -> None:
    rows = [
        ("MuJoCo 4.0.1", RESULTS / "render_check" / "reacher_v4.0.1_1.0.52_33220.png", "平均差 20.0"),
        ("MuJoCo 3.11.0", RESULTS / "render_check" / "reacher_v3.11.0_1.0.44_33220.png", "平均差 2.6"),
    ]
    cols = ["数据集里存的帧", "环境现画", "两者之差 ×4"]
    tile, scale, left, top, gap = 224, 2, 280, 70, 16
    size = tile * scale
    W = left + 3 * size + 2 * gap + 20
    H = top + 2 * size + gap + 20
    img = Image.new("RGB", (W, H), PAPER_BG)
    draw = ImageDraw.Draw(img)
    f_head = ImageFont.truetype(FONT, 30)
    f_row = ImageFont.truetype(FONT, 30)
    f_note = ImageFont.truetype(FONT, 24)
    for c, name in enumerate(cols):
        x = left + c * (size + gap) + size // 2
        draw.text((x, top // 2), name, font=f_head, fill=INK, anchor="mm")
    for r, (label, path, note) in enumerate(rows):
        panel = Image.open(path).convert("RGB")
        y = top + r * (size + gap)
        draw.text((left - 24, y + size // 2 - 20), label, font=f_row, fill=INK, anchor="rm")
        draw.text((left - 24, y + size // 2 + 22), note, font=f_note, fill=CLAY if r == 0 else GREEN, anchor="rm")
        for c in range(3):
            crop = panel.crop((c * tile, 0, (c + 1) * tile, tile)).resize((size, size), Image.LANCZOS)
            img.paste(crop, (left + c * (size + gap), y))
    img.save(OUT / "lewm-reacher-floor.png")


def training() -> None:
    epochs = list(range(1, 11))
    total = [8.06, 5.05, 2.21, 0.502, 0.483, 0.256, 0.227, 0.175, 0.161, 0.157]
    pred = [1.54, 1.02, 0.379, 0.108, 0.086, 0.044, 0.034, 0.013, 0.0079, 0.0067]
    sigreg = [72.4, 44.8, 20.3, 4.38, 4.42, 2.35, 2.14, 1.80, 1.70, 1.67]
    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=160)
    ax.plot(epochs, sigreg, "o-", color=CLAY, lw=1.8, label="SIGReg 项")
    ax.plot(epochs, total, "o-", color=INK, lw=1.8, label="总损失 = 预测 + 0.09 × SIGReg")
    ax.plot(epochs, pred, "o-", color=GREEN, lw=1.8, label="预测损失")
    ax.set_yscale("log")
    ax.set_xticks(epochs)
    ax.set_xlabel("epoch（每个 5,138 步，batch 128）", fontsize=13)
    ax.set_ylabel("留出数据上的验证损失（对数坐标）", fontsize=13)
    ax.set_title("Two-Room 从头训练：51,380 步，4 小时 41 分", fontsize=15, pad=12, loc="left")
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=LINE, lw=0.8, which="major")
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "lewm-train.png")
    plt.close(fig)


def clips() -> None:
    # Planning videos written by eval.py: agent | dataset trajectory | goal, 50 steps at 15 fps; all three succeed.
    for src, name in (("pusht/env_0", "lewm-pusht"), ("cube/env_2", "lewm-cube"), ("tworoom_trained/env_0", "lewm-tworoom")):
        mp4 = OUT / f"{name}.mp4"
        shutil.copy2(RESULTS / "videos" / f"{src}.mp4", mp4)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "1.5", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                        str(OUT / f"frame-{name}.jpg")], check=True)


if __name__ == "__main__":
    results()
    reacher_floor()
    training()
    clips()
    print(OUT)
