"""Build the "World Labs Atlas for Robotics" project page.

    python build_page.py
      -> RoboGardenSite/projects/atlas-robotics/index.html     (page; project.css sits beside it)
      -> RoboGardenSite/media/atlas-robotics/*                  (two videos, posters, three figures)

The page has no source-code links by request (2026-11-26): no repository, no reproduce button.

Every number comes from PhysicalAI/WorldLabsAtlas:
  kitchen-3dgs/README.md                      reconstruction (Gaussians, steps, held-out PSNR / SSIM)
  _gen/xmachine/README.md                     2 x 2 cross-machine table, 200 seeds per cell, paired p-values
  zhihu/atlas-02-*.md, section 4              fine-tuning comparison on the R9700 box, held-out neon look
  zhihu/atlas-02-*.md, section 3              share of pixels the background takes in each camera
"""

import html
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROBOGARDEN = HERE.parents[1]
ATLAS = ROBOGARDEN.parent / "WorldLabsAtlas"
SITE = ROBOGARDEN / "RoboGardenSite"
SLUG = "atlas-robotics"
PAGE_DIR = SITE / "projects" / SLUG
MEDIA = SITE / "media" / SLUG
M = f"../../media/{SLUG}"
PUBLIC = "https://worldloop.github.io"
PAGE_URL = f"{PUBLIC}/projects/{SLUG}/"
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

LINKEDIN = "https://www.linkedin.com/in/charles-yang-2162b269/"
ATLAS_BLOG = "https://www.worldlabs.ai/blog/atlas"
DM05 = "https://huggingface.co/Dexmal/DM05"
DL3DV = "https://huggingface.co/datasets/DL3DV/DL3DV-ALL-2K"
WRITEUP = "../../en/posts/atlas-dm05.html"  # the RoboGarden note with the full method and statistics

TITLE = "World Labs Atlas for Robotics: One Scene, Endless Worlds To Train A VLA"  # same as page 4 of the flyer

# Closed-loop success on the R9700 box, original lighting, same 200 seeds for every row (successes, episodes).
FINETUNE = [
    ("Released DM0.5", "no fine-tuning", 53, 200, "base"),
    ("LoRA on simulator frames", "same 30 demos, default MuJoCo look", 53, 200, "base"),
    ("LoRA on the 3DGS kitchen", "same 30 demos, rendered in the target scene", 87, 200, "win"),
    ("LoRA on four relit looks", "captured, golden hour, night shift, lamp", 64, 200, "mid"),
]
# 2 x 2 cross-machine check: (model, eval on R9700, eval on W7900D), 200 seeds per cell.
XMACHINE = [
    ("Released DM0.5", (53, 200), (54, 200)),
    ("3DGS-kitchen LoRA, trained on R9700", (87, 200), (88, 200)),
    ("3DGS-kitchen LoRA, trained on W7900D", (77, 200), (82, 200)),
]


def esc(s):
    return html.escape(s, quote=True)


def pct(k, n, digits=1):
    return f"{100 * k / n:.{digits}f}%"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# ------------------------------------------------------------------ media --

def encode(src, dst):
    """1280-wide H.264 for the web; keeps the audio track if the source has one."""
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(src), "-vf", "scale=1280:-2", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", str(dst)], check=True)


def jpg(src, dst, width, box=None, quality=86):
    im = Image.open(src).convert("RGB")
    if box:
        im = im.crop(box)
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, quality=quality, optimize=True)


def prepare_media():
    MEDIA.mkdir(parents=True, exist_ok=True)
    encode(ATLAS / "robot-video" / "env_edit_robot_task.mp4", MEDIA / "robot_task.mp4")
    jpg(ATLAS / "robot-video" / "env_edit_robot_task_poster.jpg", MEDIA / "robot_task.jpg", 1280)
    encode(ATLAS / "relight-demo" / "kitchen_relight_demo.mp4", MEDIA / "relight.mp4")
    jpg(ATLAS / "relight-demo" / "kitchen_relight_demo_poster.jpg", MEDIA / "relight.jpg", 1280)
    # Held-out photo (left half) beside the 3DGS render (right half).
    jpg(ATLAS / "kitchen-3dgs" / "heldout-vs-reference.png", MEDIA / "heldout_vs_render.jpg", 1920)
    jpg(ATLAS / "kitchen-3dgs" / "validation-render.png", MEDIA / "kitchen_render.jpg", 1280)
    jpg(ATLAS / "zhihu" / "images" / "part2" / "visual_domains.png", MEDIA / "visual_domains.jpg", 1400)


# ----------------------------------------------------------------- charts --

def bars_html():
    """Horizontal bars in plain HTML/CSS so the labels stay readable on a phone (the page is reached by QR)."""
    full = 0.6  # the track runs 0-60%
    rows = []
    for name, sub, k, n, kind in FINETUNE:
        lo, hi = wilson(k, n)
        rows.append(
            f'<div class="bar-row {kind}">'
            f'<div class="bar-label"><b>{esc(name)}</b><span>{esc(sub)}</span></div>'
            f'<div class="bar-track" role="img" aria-label="{esc(name)}: {k} of {n} episodes, {pct(k, n)}">'
            f'<i class="bar" style="width:{k / n / full * 100:.2f}%"></i>'
            f'<i class="ci" style="left:{lo / full * 100:.2f}%;width:{(hi - lo) / full * 100:.2f}%"></i></div>'
            f'<div class="bar-value">{pct(k, n)}<small>{k}/{n}</small></div></div>')
    axis = "".join(f"<span>{v}%</span>" for v in (0, 20, 40, 60))
    return f'<div class="bars">{"".join(rows)}<div class="bar-row axis"><div></div><div class="bar-axis">{axis}</div><div></div></div></div>'


def xmachine_rows():
    rows = []
    for name, a, b in XMACHINE:
        cls = "" if name.startswith("Released") else ' class="hi"'
        rows.append(f"<tr><th>{esc(name)}</th><td{cls}>{a[0]}/{a[1]} <b>{pct(*a)}</b></td>"
                    f"<td{cls}>{b[0]}/{b[1]} <b>{pct(*b)}</b></td></tr>")
    return "".join(rows)


# ------------------------------------------------------------------- html --

def build_html():
    # Wording rule (user, 2026-11-26): the scene is a real capture, not generated by Marble/Atlas. Atlas only
    # edits it, and each edit is new training data. Say "scene", "edit", "variation"; never "new world".
    description = ("A real kitchen captured as 3D Gaussians, edited with World Labs Atlas, and re-rendered as new "
                   "training data to fine-tune and test a vision-language-action robot policy on AMD Radeon PRO GPUs.")
    released_w, lora_w = XMACHINE[0][2], XMACHINE[2][2]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(TITLE)} · RoboGarden</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="Charles Yang">
  <link rel="canonical" href="{PAGE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(TITLE)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{PAGE_URL}">
  <meta property="og:image" content="{PUBLIC}/media/{SLUG}/kitchen_render.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,640&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+SC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">
  <link rel="stylesheet" href="project.css">
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="../../en/index.html">Robo<span>Garden</span></a>
  <nav class="site-nav">
    <a class="who" href="../../en/index.html">Charles Yang</a>
  </nav>
</header>

<main class="proj">
  <section class="proj-hero">
    <p class="kicker">Project · AMD @ NeurIPS 2026</p>
    <h1>{esc(TITLE)}</h1>
    <p class="lede">A real kitchen is captured in photos and rebuilt as 1.46 million 3D Gaussians. World Labs Atlas then edits that scene, so one capture becomes many variations. Robot demonstrations are re-rendered in each variation as new training data for a vision-language-action (VLA) policy, and the policy is tested in closed loop. Reconstruction, rendering, training and testing run on AMD Radeon™ PRO GPUs with ROCm™.</p>
    <div class="btn-row">
      <a class="btn primary" href="#results">See the results</a>
      <a class="btn" href="{WRITEUP}">Read the write-up</a>
      <a class="btn" href="#contact">Contact</a>
    </div>
    <div class="stats">
      <div class="stat"><b>1.46M</b><span>3D Gaussians: a real commercial kitchen, reconstructed on one Radeon™ PRO W7900D</span></div>
      <div class="stat"><b>5</b><span>looks of one kitchen: the capture plus four from World Labs Relight, one of them held out</span></div>
      <div class="stat"><b>{pct(*released_w, 0)} → {pct(*lora_w, 0)}</b><span>closed-loop task success on Radeon™ PRO W7900D after fine-tuning in the 3DGS kitchen</span></div>
      <div class="stat"><b>1,200</b><span>closed-loop episodes in the two-machine check, 200 seeds per cell</span></div>
    </div>
    <figure class="hero-shot">
      <video controls muted playsinline preload="metadata" poster="{M}/robot_task.jpg">
        <source src="{M}/robot_task.mp4" type="video/mp4">
      </video>
      <figcaption>The demo in 56 seconds: pick a look for the 3DGS kitchen, then watch the same policy unload cutlery from the dishwasher into the drawer in the captured lighting and in a neon look it never saw in training.</figcaption>
    </figure>
  </section>

  <section class="sec" id="how">
    <p class="eyebrow">How it works</p>
    <h2>From photos of a room to a tested robot policy</h2>
    <p class="sec-lede">The captured scene supplies what the robot sees, Atlas edits it, and the physics simulator decides how things move. Keeping appearance and physics apart is what lets the scene be edited without touching the robot setup.</p>
    <div class="steps four">
      <div class="step"><span class="n">01 · RECONSTRUCT</span><h3>Photos to 3D Gaussians</h3><p>A commercial kitchen from the DL3DV-10K dataset is reconstructed with 3D Gaussian Splatting on one Radeon™ PRO W7900D: 15,000 steps, 1,458,354 Gaussians, 27.9 dB PSNR on a held-out photo.</p></div>
      <div class="step"><span class="n">02 · EDIT</span><h3>Change the look</h3><p>World Labs Relight, part of the Atlas-based Marble tools, re-lights the captured Gaussians. The scene is edited, not generated: geometry stays untouched, so alignment and calibration carry over to every look.</p></div>
      <div class="step"><span class="n">03 · RE-RENDER</span><h3>Replay the demonstrations</h3><p>Thirty expert demonstrations are replayed in MuJoCo. The robot, counter and dishwasher are simulated; the Gaussians are drawn behind them as the room. Only the three camera streams change.</p></div>
      <div class="step"><span class="n">04 · TRAIN AND TEST</span><h3>Fine-tune, then close the loop</h3><p>Dexmal's DM0.5 VLA gets a LoRA fine-tune of 1,000 steps on three GPUs. Each model then runs the task on 200 fixed seeds, with the policy acting on rendered images at 20 Hz.</p></div>
    </div>
    <figure class="fig">
      <img src="{M}/heldout_vs_render.jpg" alt="Left: a photo of the kitchen that was withheld from training. Right: the 3D Gaussian render of the same view." loading="lazy">
      <figcaption>Left: a photo withheld from reconstruction. Right: the 3DGS render of the same view, trained on a Radeon™ PRO W7900D (PSNR 27.9 dB, SSIM 0.937).</figcaption>
    </figure>
  </section>

  <section class="sec">
    <p class="eyebrow">Edit the scene</p>
    <h2>One capture, five looks</h2>
    <p class="sec-lede">The captured kitchen plus golden hour, night shift and lamp are used for training. Neon is kept out of training and used only to test the policy.</p>
    <div class="duo">
      <figure>
        <video controls muted playsinline preload="metadata" poster="{M}/relight.jpg">
          <source src="{M}/relight.mp4" type="video/mp4">
        </video>
        <figcaption>The relit looks, flown through as 3D Gaussians (35 s).</figcaption>
      </figure>
      <figure>
        <img src="{M}/visual_domains.jpg" alt="The robot's head camera at the same step: default simulator materials on the left, the 3D Gaussian kitchen on the right." loading="lazy">
        <figcaption>What the robot sees. Same seed and step: default simulator materials on the left, the 3DGS kitchen on the right. The physics model is identical in both.</figcaption>
      </figure>
    </div>
    <p class="note">Lighting edits on this page are real World Labs Relight outputs. The texture edit pictured on the NeurIPS flyer is a concept image of where the demo is heading, and is labelled as such there.</p>
  </section>

  <section class="sec" id="results">
    <p class="eyebrow">Results</p>
    <h2>Training in the deployment scene is what moves the number</h2>
    <p class="sec-lede">Task: BiGym <code>DishwasherUnloadCutleryLong</code>, a two-arm robot unloading cutlery from a dishwasher rack into a drawer. Every row uses the same 200 seeds, the same recipe and the captured lighting.</p>
    <div class="panel">
      {bars_html()}
      <p class="fine">Closed-loop success in the 3DGS kitchen, 200 episodes per model, measured on Radeon™ AI PRO R9700. Whiskers are Wilson 95% intervals. The 3DGS-kitchen LoRA beats the simulator-frame LoRA by 17 points (paired p = 0.0001) and the four-look LoRA by 11.5 points (p = 0.003).</p>
    </div>
    <div class="learn">
      <div class="step"><span class="n">01</span><h3>Match the scene first</h3><p>Fine-tuning on the default simulator look gives no gain at all: {FINETUNE[1][2]}/{FINETUNE[1][3]}, the same as the released model. The same demonstrations rendered in the target scene give {pct(FINETUNE[2][2], FINETUNE[2][3])}.</p></div>
      <div class="step"><span class="n">02</span><h3>More lighting did not add more</h3><p>Training on four looks scores {pct(FINETUNE[3][2], FINETUNE[3][3], 0)}. In the held-out neon look it scores 31/100, level with the released model; the single-scene model scores 36/100. The room fills about 1% of the head camera, so relighting changes little of what the policy sees.</p></div>
      <div class="step"><span class="n">03</span><h3>It holds on a second GPU family</h3><p>The recipe was repeated from scratch on Radeon™ PRO W7900D and all three models were scored on both machines. Both fine-tunes beat the released model on both.</p></div>
    </div>
    <table class="spec xm">
      <tr><th></th><th>Evaluated on Radeon™ AI PRO R9700</th><th>Evaluated on Radeon™ PRO W7900D</th></tr>
      {xmachine_rows()}
    </table>
    <p class="fine">200 seeds per cell, 1,200 episodes in total. Paired McNemar tests against the released model on the same machine: p = 0.0002 and 0.012 on R9700, p = 0.0004 and 0.005 on W7900D. The two fine-tunes do not differ from each other (p = 0.20 and 0.50). Totals agree across machines to within 2.5 points, although 18–26% of individual seeds change outcome when the machine changes.</p>
  </section>

  <section class="sec">
    <p class="eyebrow">Built with</p>
    <h2>Models and data</h2>
    <div class="partners">
      <a class="partner atlas" href="{ATLAS_BLOG}">
        <span class="role">World model</span><h3>World Labs Atlas</h3>
        <p>World Labs' world model. Here it does one job: it edits a scene that was captured for real. Its Relight tool produced the four edited looks of the kitchen; the kitchen itself is not generated.</p>
        <span class="go">worldlabs.ai/blog/atlas →</span>
      </a>
      <a class="partner dexmal" href="{DM05}">
        <span class="role">VLA policy</span><h3>Dexmal DM0.5</h3>
        <p>A vision-language-action model. It takes three camera images, the robot state and one instruction, and predicts chunks of 16 actions. The released checkpoint is the starting point.</p>
        <span class="go">huggingface.co/Dexmal/DM05 →</span>
      </a>
      <a class="partner dl3dv" href="{DL3DV}">
        <span class="role">Scene data</span><h3>DL3DV-10K</h3>
        <p>The dataset of real-world scenes the kitchen comes from. It is licensed CC BY-NC 4.0, for non-commercial research use.</p>
        <span class="go">huggingface.co/datasets/DL3DV →</span>
      </a>
    </div>
  </section>

  <section class="sec">
    <p class="eyebrow">Stack</p>
    <h2>Runs on Radeon</h2>
    <table class="spec">
      <tr><th>GPUs</th><td>AMD Radeon™ PRO W7900D (48 GB): reconstruction on one card, fine-tuning on three, one evaluation process per card. Repeated on AMD Radeon™ AI PRO R9700 (32 GB).</td></tr>
      <tr><th>Software</th><td>ROCm™, PyTorch, OpenSplat for reconstruction, gsplat 1.4.0 built from source for rendering, MuJoCo for physics</td></tr>
      <tr><th>Policy</th><td>Dexmal DM0.5, LoRA rank 32, 1,000 steps, effective batch 48</td></tr>
      <tr><th>Task</th><td>BiGym <code>DishwasherUnloadCutleryLong</code>, 30 expert demonstrations, three cameras at 20 Hz</td></tr>
      <tr><th>Scene</th><td>DL3DV-10K commercial kitchen, 1,458,354 Gaussians. The Gaussians are appearance only; they take no part in collisions.</td></tr>
    </table>
  </section>

  <section class="contact" id="contact">
    <h2>Questions, collaboration, or a demo</h2>
    <p>Charles Yang, AMD.</p>
    <div class="btn-row">
      <a class="btn primary" href="{LINKEDIN}">LinkedIn</a>
      <a class="btn" href="{WRITEUP}">Full write-up</a>
      <a class="btn" href="../../en/index.html">RoboGarden notes</a>
    </div>
  </section>
</main>
<footer class="site-footer">
  <span>Charles Yang</span>
  <a href="../../en/index.html">RoboGarden</a>
</footer>
</body>
</html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    if "--no-media" not in sys.argv:
        prepare_media()
    (PAGE_DIR / "index.html").write_text(build_html(), encoding="utf-8", newline="\n")
    for f in sorted(MEDIA.iterdir()):
        print(f"  {f.name:24s} {f.stat().st_size / 1e6:6.2f} MB")
    print("wrote", PAGE_DIR / "index.html")


if __name__ == "__main__":
    main()
