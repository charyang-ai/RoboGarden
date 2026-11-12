"""Figures for the MuJoCo 4 note. Numbers are the W7900-host measurements."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)

font_manager.fontManager.addfont(r"C:\Windows\Fonts\msyh.ttc")
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
LINE = "#e2d8c6"


def beam() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=160)
    # Official claim: within 0.5% of Euler-Bernoulli.
    ax.axhspan(0.995, 1.005, color="#1c4f3e", alpha=0.10, zorder=0)
    ax.axhline(1.0, color=GREEN, lw=1.2, zorder=1)
    xs = [0.068, 6.8]
    ys = [1.0000, 0.9796]
    ax.scatter(xs, ys, s=90, color=[GREEN, CLAY], zorder=3)
    ax.annotate(
        "0.068% 梁长\n比值 1.0000",
        xy=(0.068, 1.0000),
        xytext=(0.7, 1.016),
        fontsize=12,
        color=GREEN,
        arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.8),
    )
    ax.annotate(
        "6.8% 梁长\n比值 0.980",
        xy=(6.8, 0.9796),
        xytext=(4.15, 0.968),
        fontsize=12,
        color=CLAY,
        arrowprops=dict(arrowstyle="-", color=CLAY, lw=0.8),
    )
    ax.text(3.15, 1.0065, "0.5% 的带子", color=GREEN, fontsize=11)
    ax.set_xlim(-0.25, 7.6)
    ax.set_ylim(0.955, 1.025)
    ax.set_xlabel("端部挠度 / 梁长（%）", fontsize=13)
    ax.set_ylabel("维持形状所需的力 / 线性理论", fontsize=13)
    ax.set_title("同一根圆杆，网格从 15 段加到 63 段，比值不变", fontsize=15, pad=12, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=11)
    ax.yaxis.grid(True, color=LINE, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "mujoco4-beam.png")
    plt.close(fig)


def plastic() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=160)
    labels = ["弹性铰\n不设屈服", "塑性铰\n屈服 0.3 弧度"]
    vals = [0.0, 0.6975]
    colors = [GREEN, CLAY]
    bars = ax.bar(labels, vals, width=0.55, color=colors, zorder=2)
    ax.axhline(0.7, color=INK, lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.text(1.38, 0.708, "松开后应停在 0.700", color=INK, fontsize=12, ha="right")
    ax.scatter([0, 1], [1.0, 1.0], s=70, facecolors="none", edgecolors=MUTED, lw=1.4, zorder=3)
    ax.text(-0.22, 1.03, "松开前都在 1.0 弧度", color=MUTED, fontsize=12)
    for bar, val in zip(bars, vals):
        label = "0" if val == 0 else "0.698"
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.04, label, ha="center", fontsize=14, color=INK)
    ax.set_ylim(0, 1.22)
    ax.set_ylabel("松开并停稳后的角度（弧度）", fontsize=13)
    ax.set_title("同一只铰，先掰到 1 弧度，再把力矩拿走", fontsize=15, pad=12, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=12)
    ax.yaxis.grid(True, color=LINE, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "mujoco4-plastic.png")
    plt.close(fig)


if __name__ == "__main__":
    beam()
    plastic()
    print(OUT)
