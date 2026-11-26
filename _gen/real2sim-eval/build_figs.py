"""Figures and clips for the Real2Sim-Eval note. Numbers are the W7900 run in charyang-ai/real2sim-eval results/.

Reads R2S_RESULTS (default: RadeonRepro/real2sim-eval/results in this repository) for the scores and the first
run's log, and R2S_HOST (default: _work/r2s_site next to this file) for rope_act_resume.log and the rollout videos
of episodes 13 and 14 copied from the host. The project-page media come from R2S_PAGE (default: _gen/real2sim-post/_work/media).
"""

import json
import os
import re
import shutil
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "images"
OUT.mkdir(parents=True, exist_ok=True)
REPO = HERE.parents[1]
RESULTS = Path(os.environ.get("R2S_RESULTS", REPO / "RadeonRepro" / "real2sim-eval" / "results"))
HOST = Path(os.environ.get("R2S_HOST", HERE / "_work" / "r2s_site"))
PAGE = Path(os.environ.get("R2S_PAGE", REPO / "_gen" / "real2sim-post" / "_work" / "media"))
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
LINE = "#e2d8c6"

OFFSETS = (-5, 0, 5)
ANGLES = (-10, 0, 10)
STEP = re.compile(r"^Episode: (\d+), step: (\d+), time: ([\d.]+)")
MARK = re.compile(r"^=== episode (\d+) attempt")


def outcomes() -> dict[int, bool]:
    per = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))["per_episode"]
    return {int(k.split("_")[1]): v["success"] for k, v in per.items()}


def signed(v: int) -> str:
    return f"+{v}" if v > 0 else f"−{-v}" if v < 0 else "0"


def pose(ep: int) -> tuple[int, int, int]:
    """cfg/gs/rope.yaml: nine (x, y) offsets in cm, each with three rotations; episode = xy_index * 3 + theta_index."""
    return OFFSETS[ep // 9], OFFSETS[(ep // 3) % 3], ANGLES[ep % 3]


def step_times() -> dict[int, list[float]]:
    """Per-step seconds of the last complete (900-step) rollout of every episode, the one that wrote the scored video."""
    runs: list[dict[int, dict[int, float]]] = []
    for path in (RESULTS / "logs" / "rope_act.log", HOST / "rope_act_resume.log"):
        runs.append(defaultdict(dict))
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if MARK.match(raw):
                runs.append(defaultdict(dict))
                continue
            m = STEP.match(raw)
            if m:
                runs[-1][int(m.group(1))][int(m.group(2))] = float(m.group(3))
    best: dict[int, list[float]] = {}
    for run in runs:
        for ep, steps in run.items():
            if len(steps) == 900:
                best[ep] = [steps[s] for s in range(1, 900)]
    return best


def grid_figure(done: dict[int, bool], lang: str) -> None:
    text = {
        "zh": {
            "title": "27 个初值的结局：失败集中在 x 为 −5 cm 和转角 +10°",
            "sub": "成功数：x = −5 cm 为 {0}/9，x = 0 为 {1}/9，x = +5 cm 为 {2}/9。绿：成功；红褐：失败；格子里是回合编号。",
            "panel": "转角 {a}°（{n}/9 成功）",
            "x": "x 偏移（cm）",
            "y": "y 偏移（cm）",
        },
        "en": {
            "title": "Outcomes of the 27 initial states: failures cluster at x = −5 cm and +10° rotation",
            "sub": "Successes: {0}/9 at x = −5 cm, {1}/9 at x = 0, {2}/9 at x = +5 cm. Green: success; clay: failure; cells show episode ids.",
            "panel": "rotation {a}° ({n}/9 succeed)",
            "x": "x offset (cm)",
            "y": "y offset (cm)",
        },
    }[lang]
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 5.4), dpi=160)
    for ax, angle in zip(axes, ANGLES):
        eps = [e for e in done if pose(e)[2] == angle]
        for e in eps:
            x, y, _ = pose(e)
            i, j = OFFSETS.index(x), OFFSETS.index(y)
            ax.add_patch(Rectangle((i + 0.06, j + 0.06), 0.88, 0.88, color=GREEN if done[e] else CLAY))
            ax.text(i + 0.5, j + 0.5, str(e), ha="center", va="center", color="#fffdf8", fontsize=17, fontweight="bold")
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        ax.set_aspect("equal")
        ax.set_xticks([0.5, 1.5, 2.5], [signed(v) for v in OFFSETS], fontsize=11)
        ax.set_yticks([0.5, 1.5, 2.5], [signed(v) for v in OFFSETS], fontsize=11)
        ax.tick_params(length=0)
        for side in ax.spines.values():
            side.set_visible(False)
        ax.set_xlabel(text["x"], fontsize=11)
        if angle == ANGLES[0]:
            ax.set_ylabel(text["y"], fontsize=11)
        ax.set_title(text["panel"].format(a=signed(angle), n=sum(done[e] for e in eps)), fontsize=13, pad=8)
    by_x = [sum(done[e] for e in done if pose(e)[0] == x) for x in OFFSETS]
    fig.suptitle(text["title"], fontsize=15, x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.885, text["sub"].format(*by_x), fontsize=10.5, color=MUTED, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    fig.savefig(OUT / ("r2s-grid.png" if lang == "zh" else "r2s-grid_en.png"), bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def time_figure(done: dict[int, bool], times: dict[int, list[float]], lang: str) -> None:
    text = {
        "zh": {
            "title": "每个控制步的中位耗时：快的几组都失败了",
            "y": "控制步耗时中位数（秒）",
            "x": "回合编号",
            "ok": "成功",
            "bad": "失败",
            "all": "全部回合的中位数 {m:.1f} 秒",
        },
        "en": {
            "title": "Median control-step time per episode: the fast ones all failed",
            "y": "median control-step time (s)",
            "x": "episode",
            "ok": "success",
            "bad": "failure",
            "all": "median over all episodes, {m:.1f} s",
        },
    }[lang]
    eps = sorted(times)
    med = [statistics.median(times[e]) for e in eps]
    overall = statistics.median(statistics.median(times[e]) for e in eps)
    fig, ax = plt.subplots(figsize=(12.4, 5.0), dpi=160)
    ax.bar(eps, med, 0.72, color=[GREEN if done[e] else CLAY for e in eps], zorder=2)
    ax.axhline(overall, color=MUTED, lw=1.3, ls=(0, (3, 2)), zorder=3)
    handles = [
        Patch(color=GREEN, label=text["ok"]),
        Patch(color=CLAY, label=text["bad"]),
        Line2D([], [], color=MUTED, lw=1.3, ls=(0, (3, 2)), label=text["all"].format(m=overall)),
    ]
    ax.set_xticks(eps, [str(e) for e in eps], fontsize=10)
    ax.set_xlim(-0.7, 26.7)
    ax.set_ylim(0, 5.9)
    ax.set_xlabel(text["x"], fontsize=12)
    ax.set_ylabel(text["y"], fontsize=12)
    ax.set_title(text["title"], fontsize=15, pad=12, loc="left")
    ax.legend(handles=handles, frameon=False, fontsize=11, loc="upper left", ncol=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=LINE, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / ("r2s-steptime.png" if lang == "zh" else "r2s-steptime_en.png"))
    plt.close(fig)


def ffmpeg(*args: str) -> None:
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args], check=True)


def clips() -> None:
    # vis_camera_0.mp4 of episodes 13 (success) and 14 (failure): 848x480, 30 fps, 900 control steps.
    for ep in (13, 14):
        mp4 = OUT / f"r2s-ep{ep}.mp4"
        shutil.copy2(HOST / f"ep{ep:04d}.mp4", mp4)
        ffmpeg("-ss", "29", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(OUT / f"frame-r2s-ep{ep}.jpg"))
    shutil.copy2(PAGE / "concat-rope.mp4", OUT / "r2s-sim-vs-real.mp4")
    ffmpeg("-ss", "8", "-i", str(PAGE / "concat-rope.mp4"), "-frames:v", "1", "-q:v", "3", str(OUT / "frame-r2s-sim-vs-real.jpg"))
    for name in ("teaser", "method"):
        img = Image.open(PAGE / f"{name}.png").convert("RGB")
        if img.width > 1600:
            img = img.resize((1600, round(img.height * 1600 / img.width)), Image.Resampling.LANCZOS)
        img.save(OUT / f"r2s-{name}.jpg", quality=88, optimize=True)


def report(done: dict[int, bool], times: dict[int, list[float]]) -> None:
    for e in sorted(times):
        t = times[e]
        print(f"ep {e:2d} {'S' if done[e] else 'F'} pose {pose(e)} median {statistics.median(t):.2f}s "
              f"min {min(t):.2f} max {max(t):.2f} total {sum(t) / 60:.0f} min")
    allt = [x for e in times for x in times[e]]
    print(f"all steps: median {statistics.median(allt):.2f}s, p1 {sorted(allt)[len(allt) // 100]:.2f}s, "
          f"p99 {sorted(allt)[-len(allt) // 100]:.2f}s, min {min(allt):.2f}, max {max(allt):.2f}")
    for key, idx in (("x", 0), ("y", 1), ("theta", 2)):
        print(key, {v: sum(done[e] for e in done if pose(e)[idx] == v) for v in (ANGLES if idx == 2 else OFFSETS)})


if __name__ == "__main__":
    done = outcomes()
    times = step_times()
    report(done, times)
    for lang in ("zh", "en"):
        grid_figure(done, lang)
        time_figure(done, times, lang)
    clips()
    print(OUT)
