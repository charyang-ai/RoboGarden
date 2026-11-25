"""Prepare the figures for the Atlas x DM0.5 post on the site.

    python _gen/atlas-dm05/build_figs.py

Inputs (local only):
  _gen/zhihu-series/images/atlas-dm05/   the Zhihu article's figures (Chinese labels on four of them)
  ../WorldLabsAtlas/workshop/data/eval/  per-seed outcomes (August / November released runs)
  ../WorldLabsAtlas/_gen/xmachine/_work/results.json   pooled 2x2 cross-machine results
Outputs go to _gen/atlas-dm05/images/: web-sized copies of the shared figures, English versions of the
four Chinese-labelled charts (*_en.png), and the card thumbnail.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "_gen" / "zhihu-series" / "images" / "atlas-dm05"
ATLAS = ROOT.parent / "WorldLabsAtlas"
EVAL = ATLAS / "workshop" / "data" / "eval"
XM = ATLAS / "_gen" / "xmachine" / "_work" / "results.json"
OUT = HERE / "images"
OUT.mkdir(exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def wilson_half(p, n, z=1.96):
    d = 1 + z * z / n
    return z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d


def save(fig, name, **kw):
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote", path)


# --- shared figures, web-sized ----------------------------------------------------------
def shared():
    for name in ("seed_agreement.png", "relight_looks.jpg", "ci_vs_n.png", "drift_seeds.png",
                 "success_rates_final.png", "xmachine.png"):
        (OUT / name).write_bytes((SRC / name).read_bytes())
        print("copied", name)
    # reconstruction: drop the small working-note footer line under the photos
    im = Image.open(SRC / "reconstruction.png").convert("RGB")
    ink = (np.asarray(im).astype(int).sum(axis=2) < 700).any(axis=1)
    y = len(ink) - 1
    while not ink[y]:  # blank margin at the very bottom
        y -= 1
    while ink[y]:  # footer text rows
        y -= 1
    while not ink[y]:  # the blank band between photos and footer
        y -= 1
    im = im.crop((0, 0, im.width, y + 3))
    im.thumbnail((1800, 1800), Image.LANCZOS)
    im.save(OUT / "reconstruction.jpg", quality=88)
    im = Image.open(SRC / "robot_views.jpg").convert("RGB")
    im.thumbnail((1500, 1900), Image.LANCZOS)
    im.save(OUT / "robot_views.jpg", quality=86)
    Image.open(SRC / "w7900_synthetic_check.png").convert("RGB").save(OUT / "w7900_synthetic_check.jpg", quality=88)
    print("wrote reconstruction.jpg, robot_views.jpg, w7900_synthetic_check.jpg")


# --- English versions of the Chinese-labelled charts -----------------------------------
def success_en():
    groups = [
        ("Original lighting (seen in training)", [
            ("Released\nno fine-tune", "#9aa3ad", 53, 200), ("Native render\nLoRA", "#c7b38a", 53, 200),
            ("Single-scene 3DGS\nLoRA", "#d62728", 87, 200), ("Four lightings\nLoRA", "#3b7dd8", 64, 200)]),
        ("Neon lighting (never seen in training)", [
            ("Released\nno fine-tune", "#9aa3ad", 31, 100), ("Single-scene 3DGS\nLoRA", "#d62728", 36, 100),
            ("Four lightings\nLoRA", "#3b7dd8", 31, 100)]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [4, 3]}, sharey=True)
    for ax, (title, bars) in zip(axes, groups):
        for x, (label, color, k, n) in enumerate(bars):
            lo, hi = wilson(k, n)
            ax.bar(x, k / n * 100, color=color, width=0.62)
            ax.errorbar(x, k / n * 100, yerr=[[k / n * 100 - lo * 100], [hi * 100 - k / n * 100]],
                        color="#333", capsize=4, lw=1.2)
            ax.text(x, hi * 100 + 1.5, f"{k / n:.1%}\n{k}/{n}", ha="center", va="bottom", fontsize=10)
        ax.set_xticks(range(len(bars)), [b[0] for b in bars], fontsize=9.5)
        ax.set_title(title, fontsize=12)
        ax.set_ylim(0, 70)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Closed-loop success rate (%)")
    fig.suptitle("BiGym dishwasher task, DM0.5 in the 3DGS kitchen (error bars: Wilson 95% interval)", fontsize=12)
    fig.tight_layout()
    save(fig, "success_rates_final_en.png")


def ci_en():
    ns = np.arange(20, 401)
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    for p, color in ((0.25, "#7f8c99"), (0.43, "#d62728")):
        ax.plot(ns, [wilson_half(p, n) * 100 for n in ns], color=color, lw=2, label=f"true success rate about {p:.0%}")
    for n in (50, 100, 200):
        h = wilson_half(0.43, n) * 100
        ax.plot(n, h, "o", color="#d62728")
        ax.annotate(f"{n} episodes: ±{h:.0f} points", (n, h), xytext=(8, 6), textcoords="offset points", fontsize=10)
    ax.set_xlabel("Evaluation episodes per group")
    ax.set_ylabel("Half-width of the 95% interval (percentage points)")
    ax.set_ylim(0, 22)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=10)
    ax.set_title("How precisely one success rate can be measured:\nat 50 episodes, a gap of ten-odd points is still inside the error", fontsize=12)
    save(fig, "ci_vs_n_en.png")


def drift_en():
    aug = {e["seed"]: e["success"] for e in json.loads((EVAL / "released-original-august.json").read_text())}
    nov = {e["seed"]: e["success"] for e in json.loads((EVAL / "released-original.json").read_text())}
    seeds = sorted(set(aug) & set(nov))[:50]
    both = sum(aug[s] and nov[s] for s in seeds)
    flips = [s for s in seeds if aug[s] != nov[s]]
    fig, ax = plt.subplots(figsize=(12, 2.6))
    for row, (name, res) in enumerate((("August", aug), ("November", nov))):
        for i, s in enumerate(seeds):
            ax.add_patch(Rectangle((i, 1 - row), 0.9, 0.8, color="#2e8b57" if res[s] else "#e8ecf1"))
            if s in flips:
                ax.add_patch(Rectangle((i, 1 - row), 0.9, 0.8, fill=False, ec="#e69500", lw=1.6))
        ax.text(-0.6, 1.4 - row, f"{name}  {sum(res[s] for s in seeds)}/50", ha="right", va="center", fontsize=11)
    ax.set_xlim(-8.5, 50.5), ax.set_ylim(-0.1, 2.0)
    ax.axis("off")
    ax.set_title(f"Same released model, same kitchen, same 50 seeds: {both} succeed both times, "
                 f"{len(flips)} flip (orange outline)", fontsize=12)
    save(fig, "drift_seeds_en.png")
    assert (sum(aug[s] for s in seeds), sum(nov[s] for s in seeds), len(flips), both) == (18, 10, 12, 8)


def xmachine_en():
    res = json.loads(XM.read_text(encoding="utf-8"))
    models = [("released", "Released\nno fine-tune"), ("single", "Single-scene LoRA\ntrained on R9700"),
              ("aw", "Single-scene LoRA\ntrained on W7900D")]
    boxes = [("R9700", "#d62728", "Evaluated on R9700"), ("W7900D", "#3b7dd8", "Evaluated on W7900D")]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [3, 2]})
    for j, (box, color, label) in enumerate(boxes):
        for i, (m, _) in enumerate(models):
            c = res["cells"][f"{m}@{box}"]
            x = i + (j - 0.5) * 0.36
            ax.bar(x, c["rate"] * 100, width=0.34, color=color, label=label if i == 0 else None)
            ax.errorbar(x, c["rate"] * 100, yerr=[[c["rate"] * 100 - c["ci"][0] * 100], [c["ci"][1] * 100 - c["rate"] * 100]],
                        color="#333", capsize=3, lw=1)
            ax.text(x, c["ci"][1] * 100 + 1.2, f"{c['k']}/{c['n']}", ha="center", fontsize=9)
    ax.set_xticks(range(len(models)), [m[1] for m in models])
    ax.set_ylabel("Closed-loop success rate (%)")
    ax.set_ylim(0, 70)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Same seeds, two machines (error bars: Wilson 95% interval)", fontsize=11)
    names = [("released", "Released"), ("single", "LoRA trained on R9700"), ("aw", "LoRA trained on W7900D"),
             ("released R9700 rerun (same box)", "Released, rerun on R9700")]
    for i, (k, _) in enumerate(names):
        v = res["cross_machine"][k]
        tot = max(v["seeds"], 1)
        parts = [(v["both"], "#2e8b57", "Both succeed"), (v["neither"], "#c9d1da", "Both fail"),
                 (v["only_a"] + v["only_b"], "#e69500", "Outcome flips")]
        left = 0
        for cnt, col, lab in parts:
            ax2.barh(i, cnt / tot * 100, left=left, color=col, label=lab if i == 0 else None)
            left += cnt / tot * 100
        ax2.text(101, i, f"flips {(v['only_a'] + v['only_b']) / tot:.0%} ({v['seeds']} seeds)", va="center", fontsize=9)
    ax2.set_yticks(range(len(names)), [n[1] for n in names])
    ax2.invert_yaxis()
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("Share of seeds (%)")
    ax2.legend(fontsize=8.5, loc="lower center", bbox_to_anchor=(0.5, -0.42), ncol=3)
    ax2.set_title("Same model, same seed, another machine (or a rerun): same outcome?", fontsize=11)
    for a in (ax, ax2):
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, "xmachine_en.png")


# --- card thumbnail: the five lightings as five slices ---------------------------------
def thumb():
    im = Image.open(SRC / "relight_looks.jpg").convert("RGB")
    a = np.asarray(im).astype(int)
    nonwhite = (a.sum(axis=2) < 740)
    rows = np.where(nonwhite.mean(axis=1) > 0.55)[0]
    top, bottom = rows.min(), rows.max()
    cols = nonwhite[top : bottom + 1].mean(axis=0) > 0.5
    edges, start = [], None
    for x, on in enumerate(cols):
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start > 40:
                edges.append((start, x))
            start = None
    if start is not None:
        edges.append((start, len(cols)))
    assert len(edges) == 5, edges
    W, H = 800, 500
    sw = W // 5
    canvas = Image.new("RGB", (W, H), "white")
    for i, (x0, x1) in enumerate(edges):
        panel = im.crop((x0, top, x1, bottom + 1))
        scale = H / panel.height
        panel = panel.resize((round(panel.width * scale), H), Image.LANCZOS)
        cx = panel.width // 2
        canvas.paste(panel.crop((cx - sw // 2, 0, cx + sw // 2, H)), (i * sw, 0))
    canvas.save(OUT / "thumb.jpg", quality=88)
    print("wrote", OUT / "thumb.jpg")


if __name__ == "__main__":
    shared()
    success_en()
    ci_en()
    drift_en()
    xmachine_en()
    thumb()
