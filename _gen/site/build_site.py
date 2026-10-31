"""Build the public RoboGarden site into RoboGardenSite/ from the essay markdown, in Chinese and English."""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "RoboGardenSite"
WORK = Path(__file__).resolve().parent / "_work"
REPRO = ROOT / "RadeonRepro"
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
SITE = "https://worldloop.github.io"
REPO = "https://github.com/worldloop/worldloop.github.io"
# Base URL of the analytics Worker in analytics/; empty leaves the view counter out of the pages.
VIEWS_API = "https://robogarden-views.worldloop.workers.dev"

TOKEN = re.compile(
    r"`([^`]+)`"
    r"|\[([^\]]+)\]\(([^)]+)\)"
    r"|<(https?://[^>\s]+)>"
    r"|(https?://[^\s<>）)。，、]+)"
)

LANGS = {
    "zh": {
        "html_lang": "zh-CN",
        "prefix": "",
        "hero": "在 AMD ROCm 上移植并优化前沿机器人模型",
        "lede": "覆盖 Radeon RDNA3、RDNA4 与 Ryzen RDNA3.5 平台。",
        "description": "Charles Yang 在 AMD ROCm 上移植并优化前沿机器人模型的笔记。",
        "back": "← 全部笔记",
        "switch_to": "en",
        "switch_text": "EN",
        "switch_title": "English",
    },
    "en": {
        "html_lang": "en",
        "prefix": "en/",
        "hero": "Porting and Optimizing Frontier Robotics Models on AMD ROCm",
        "lede": "Across Radeon RDNA3, RDNA4, and Ryzen RDNA3.5 platforms.",
        "description": "Charles Yang's notes on porting and optimizing frontier robotics models on AMD ROCm.",
        "back": "← All notes",
        "switch_to": "zh",
        "switch_text": "中文",
        "switch_title": "中文",
    },
}

POSTS = [
    {
        "slug": "roborender",
        "tag": "RoboRender",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": {"zh": ROOT / "roborender-video-model.md", "en": ROOT / "en" / "roborender-video-model.md"},
        "dek": {
            "zh": "仿真继续负责几何和动作，视频模型负责把这条轨迹画成真实世界里的颜色。",
            "en": "Simulation keeps the geometry and actions; a video model paints the trajectory in real-world colors.",
        },
        "thumb": "rr-frame.png",
        "figures": [
            ("rr-comparison.png", {
                "zh": "第 40 帧。从左到右是深度、机械臂掩码、画出来的画面；三行是三个视角。提示词要一只红杯子，几何给的是椭圆，椭圆就变成了一把勺子。",
                "en": "Frame 40. Left to right: depth, arm mask, painted frame; the three rows are three views. The prompt asks for a red cup, the geometry gives an ellipse, and the ellipse becomes a spoon.",
            }),
        ],
        "videos": [
            ("rr-comparison.mp4", "rr-comparison.png", {
                "zh": "同一次 50 步推理的对比视频。每一行一个视角，列是深度、掩码、生成结果。",
                "en": "Comparison video from the same 50-step run. One row per view; columns are depth, mask, and generated output.",
            }),
            ("rr-head.mp4", "rr-head.jpg", {"zh": "头部相机画出的 81 帧。", "en": "81 frames painted for the head camera."}),
            ("rr-left.mp4", "rr-left.jpg", {"zh": "左手相机。", "en": "Left wrist camera."}),
            ("rr-right.mp4", "rr-right.jpg", {"zh": "右手相机。", "en": "Right wrist camera."}),
        ],
    },
    {
        "slug": "worldscore",
        "tag": "WorldScore",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": {"zh": ROOT / "worldscore.md", "en": ROOT / "en" / "worldscore.md"},
        "dek": {
            "zh": "镜头往前推的时候，吧台还在不在原来的地方。WorldScore 把这件事拆开打分。",
            "en": "When the camera pushes in, is the bar still where it was? WorldScore breaks that question apart and scores each piece.",
        },
        "thumb": "ws-figure.png",
        "figures": [
            ("ws-figure.png", {
                "zh": "WorldScore 要覆盖的那些世界：室内和室外、写实和风格化。图来自 WorldScore 项目页。",
                "en": "The worlds WorldScore covers: indoor and outdoor, realistic and stylized. Figure from the WorldScore project page.",
            }),
        ],
        "videos": [
            ("ws-overview.mp4", "frame-ws-overview.jpg", {
                "zh": "基准怎么考下一条镜头：从一张起始图出发，模型得按相机指令长出下一个场景。",
                "en": "How the benchmark tests the next shot: starting from one image, the model has to grow the next scene following a camera instruction.",
            }),
            ("ws-camera.mp4", "frame-ws-camera.jpg", {
                "zh": "相机控制的对照。同一句指令，一边听得懂，一边把湖面和山形换了一套。",
                "en": "Camera control side by side. Same instruction: one side follows it, the other swaps out the lake and the mountains.",
            }),
        ],
    },
    {
        "slug": "interactive-world-sim",
        "tag": "Interactive World Simulator",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": {"zh": ROOT / "interactive_world_sim.md", "en": ROOT / "en" / "interactive_world_sim.md"},
        "dek": {
            "zh": "给一帧画面和一串动作，在像素里把下一秒演完，中间不请物理引擎当裁判。",
            "en": "Given one frame and a sequence of actions, play out the next second in pixels, with no physics engine as referee.",
        },
        "thumb": "frame-iws-pusht.jpg",
        "figures": [
            ("iws-correlation.png", {
                "zh": "同一批策略，在世界模型里的分数和在真机上的分数。点靠近对角线，说明排序对得上。图来自项目页。",
                "en": "The same policies scored in the world model and on the real robot. Points near the diagonal mean the rankings agree. Figure from the project page.",
            }),
        ],
        "videos": [
            ("iws-pusht.mp4", "frame-iws-pusht.jpg", {
                "zh": "推一个 T 形块。左边是模型开环画出来的画面，右边是人在遥操作。",
                "en": "Pushing a T-shaped block. Left: the model's open-loop rollout; right: a human teleoperating.",
            }),
            ("iws-rope.mp4", "frame-iws-rope.jpg", {
                "zh": "把绳子送向夹子。进了夹子，和从旁边荡过去，是两段不同的视频。",
                "en": "Feeding a rope toward a clip. Entering the clip and swinging past it are two different videos.",
            }),
            ("iws-mug.mp4", "frame-iws-mug.jpg", {
                "zh": "抓一只杯子。滑出指缝，和杯把被顶着转，都是很小的像素变化。",
                "en": "Grabbing a mug. Slipping through the fingers and the handle being pushed into a turn are both tiny pixel changes.",
            }),
        ],
    },
    {
        "slug": "pointworld",
        "tag": "PointWorld",
        "date": "2026-10-26",
        "date_label": "2026.10.26",
        "src": {"zh": ROOT / "pointworld.md", "en": ROOT / "en" / "pointworld.md"},
        "dek": {
            "zh": "状态和动作说同一种语言。给一张 RGB-D，预言每一个点下一秒往哪里走。",
            "en": "State and action speak the same language. From one RGB-D image, predict where every point goes in the next second.",
        },
        "thumb": "frame-pw-scarf.jpg",
        "figures": [
            ("pw-card.jpg", {
                "zh": "动作也是一团点：夹爪上的点往前走，场景里的点跟着动。图来自 PointWorld 项目页。",
                "en": "Actions are points too: points on the gripper move forward, and points in the scene follow. Figure from the PointWorld project page.",
            }),
        ],
        "videos": [
            ("pw-scarf.mp4", "frame-pw-scarf.jpg", {
                "zh": "叠围巾。同一个预训练检查点，不做任务微调。",
                "en": "Folding a scarf. The same pretrained checkpoint, with no task fine-tuning.",
            }),
            ("pw-tissue.mp4", "frame-pw-tissue.jpg", {"zh": "推纸巾盒。", "en": "Pushing a tissue box."}),
            ("pw-broom.mp4", "frame-pw-broom.jpg", {"zh": "拿扫帚扫地。", "en": "Sweeping with a broom."}),
        ],
    },
    {
        "slug": "ctrl-world",
        "tag": "Ctrl-World",
        "date": "2026-10-26",
        "date_label": "2026.10.26",
        "src": {"zh": ROOT / "BLOG.md", "en": ROOT / "en" / "BLOG.md"},
        "dek": {
            "zh": "让策略在想象里把操作滚完。想象只要足够听话，排名就可以先在显卡上排出来。",
            "en": "Let the policy roll out the manipulation in imagination. If the imagination is obedient enough, the ranking can be settled on a GPU first.",
        },
        "thumb": "frame-ctrl-banana.jpg",
        "figures": [
            ("ctrl-diagram.jpg", {
                "zh": "策略出动作，世界模型长出下一秒的三台相机，记忆把更早的画面留在回路里。",
                "en": "The policy outputs actions, the world model grows the next second for three cameras, and memory keeps earlier frames in the loop.",
            }),
        ],
        "videos": [
            ("banana.mp4", "frame-ctrl-banana.jpg", {
                "zh": "把香蕉往右挪。上排是记录下来的真值，下排是世界模型在一张 W7900 上想象出来的三台相机。",
                "en": "Move the banana to the right. Top row: recorded ground truth; bottom row: the three cameras imagined by the world model on one W7900.",
            }),
            ("black.mp4", "frame-ctrl-black.jpg", {
                "zh": "把椅子上的黑东西放到桌上。",
                "en": "Put the black thing on the chair onto the table.",
            }),
            ("towel.mp4", "frame-ctrl-towel.jpg", {
                "zh": "把绿毛巾挪到盖子右边。",
                "en": "Move the green towel to the right of the lid.",
            }),
        ],
    },
]


def inline(text: str) -> str:
    out: list[str] = []
    pos = 0
    for match in TOKEN.finditer(text):
        out.append(html.escape(text[pos : match.start()]))
        if match.group(1) is not None:
            out.append(f"<code>{html.escape(match.group(1))}</code>")
        elif match.group(2) is not None:
            href = html.escape(match.group(3), quote=True)
            out.append(f'<a href="{href}">{html.escape(match.group(2))}</a>')
        else:
            href = html.escape(match.group(4) or match.group(5), quote=True)
            out.append(f'<a href="{href}">{href}</a>')
        pos = match.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def markdown_to_html(path: Path) -> tuple[str, str]:
    title = ""
    blocks: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            blocks.append("\n".join(buf).strip())
            buf.clear()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("作者："):
            continue
        if not line:
            flush()
            continue
        buf.append(line)
    flush()

    parts: list[str] = []
    for block in blocks:
        if block.startswith("## "):
            parts.append(f"<h2>{inline(block[3:].strip())}</h2>")
        else:
            parts.append(f"<p>{inline(block)}</p>")
    return title, "\n".join(parts)


def poster(src: Path, dest: Path, ss: str = "2") -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    subprocess.run(
        [FFMPEG, "-y", "-ss", ss, "-i", str(src), "-frames:v", "1", "-q:v", "3", str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == src.stat().st_size:
        return
    shutil.copy2(src, dest)


def page(lang: str, rel: str, title: str, description: str, body: str, root: str) -> str:
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{LANGS[code]["html_lang"]}" href="{SITE}/{LANGS[code]["prefix"]}{rel}">'
        for code in LANGS
    )
    views_attr = f' data-views-api="{html.escape(VIEWS_API, quote=True)}"' if VIEWS_API else ""
    views_script = f'\n  <script src="{root}views.js" defer></script>' if VIEWS_API else ""
    return f"""<!DOCTYPE html>
<html lang="{LANGS[lang]['html_lang']}"{views_attr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="author" content="Charles Yang">
{alternates}
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,640&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+SC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}styles.css">{views_script}
</head>
<body>
{body}
</body>
</html>
"""


def header(lang: str, rel: str, root: str) -> str:
    strings = LANGS[lang]
    other = LANGS[strings["switch_to"]]
    home = f"{root}{strings['prefix']}index.html"
    switch = f"{root}{other['prefix']}{rel}"
    return f"""<header class="site-header">
  <a class="wordmark" href="{home}">Robo<span>Garden</span></a>
  <nav class="site-nav">
    <a class="lang-switch" href="{switch}" hreflang="{other['html_lang']}" lang="{other['html_lang']}" title="{strings['switch_title']}">{strings['switch_text']}</a>
    <a class="who" href="{home}">Charles Yang</a>
  </nav>
</header>
"""


def footer() -> str:
    return f"""<footer class="site-footer">
  <span>Charles Yang</span>
  <a href="{REPO}">GitHub</a>
</footer>
"""


def prepare_local_media() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    pairs = {
        "ctrl-diagram.jpg": REPRO / "ctrl-world" / "synthetic_traj" / "gallery" / "ctrl_world.jpg",
        "banana-src.mp4": REPRO / "ctrl-world" / "results" / "videos" / "time_20261025_155637_traj_899_8_5_Move_the_banana_to_the_right.mp4",
        "black-src.mp4": REPRO / "ctrl-world" / "results" / "videos" / "time_20261025_155936_traj_18599_14_5_Pick_the_black_thing_from_the_.mp4",
        "towel-src.mp4": REPRO / "ctrl-world" / "results" / "videos" / "time_20261025_160225_traj_199_8_5_Move_the_green_towel_to_the_ri.mp4",
        "ws-overview.mp4": REPRO / "worldscore" / "assets" / "overview.mp4",
        "rr-comparison.png": REPRO / "roborender-video-model" / "results" / "frame40_comparison.png",
        "rr-frame.png": REPRO / "roborender-video-model" / "results" / "frame40_generated_hand_left.png",
        "rr-comparison.mp4": REPRO / "roborender-video-model" / "results" / "comparison.mp4",
        "rr-head.mp4": REPRO / "roborender-video-model" / "results" / "generated_head_color.mp4",
        "rr-left.mp4": REPRO / "roborender-video-model" / "results" / "generated_hand_left.mp4",
        "rr-right.mp4": REPRO / "roborender-video-model" / "results" / "generated_hand_right.mp4",
    }
    for name, src in pairs.items():
        if not src.exists():
            raise SystemExit(f"missing source media: {src}")
        copy_file(src, WORK / name)
    poster(WORK / "banana-src.mp4", WORK / "frame-ctrl-banana.jpg", "1.5")
    poster(WORK / "black-src.mp4", WORK / "frame-ctrl-black.jpg", "1.5")
    poster(WORK / "towel-src.mp4", WORK / "frame-ctrl-towel.jpg", "1.5")
    poster(WORK / "ws-overview.mp4", WORK / "frame-ws-overview.jpg", "6")
    poster(WORK / "rr-head.mp4", WORK / "rr-head.jpg", "1")
    poster(WORK / "rr-left.mp4", WORK / "rr-left.jpg", "1")
    poster(WORK / "rr-right.mp4", WORK / "rr-right.jpg", "1")


def copy_post_media(post: dict) -> None:
    folder = DOCS / "media" / post["slug"]
    folder.mkdir(parents=True, exist_ok=True)
    src_thumb = WORK / post["thumb"]
    if src_thumb.suffix.lower() != ".jpg":
        subprocess.run(
            [FFMPEG, "-y", "-i", str(src_thumb), "-q:v", "3", str(folder / "thumb.jpg")],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        copy_file(src_thumb, folder / "thumb.jpg")
    for name, _ in post["figures"]:
        copy_file(WORK / name, folder / name)
    for name, poster_name, _ in post["videos"]:
        src_name = {
            "banana.mp4": "banana-src.mp4",
            "black.mp4": "black-src.mp4",
            "towel.mp4": "towel-src.mp4",
        }.get(name, name)
        copy_file(WORK / src_name, folder / name)
        copy_file(WORK / poster_name, folder / poster_name)


def build_lang(lang: str) -> None:
    strings = LANGS[lang]
    out = DOCS / strings["prefix"] if strings["prefix"] else DOCS
    index_root = "../" if strings["prefix"] else ""
    post_root = index_root + "../"

    rendered = []
    for post in POSTS:
        title, prose = markdown_to_html(post["src"][lang])
        rendered.append({**post, "title": title, "prose": prose, "dek": post["dek"][lang]})

    cards = []
    for post in rendered:
        cards.append(
            f"""<a class="card" href="posts/{post['slug']}.html">
  <div class="thumb"><img src="{index_root}media/{post['slug']}/thumb.jpg" alt=""></div>
  <div class="card-body">
    <p class="meta">{html.escape(post['tag'])} · {post['date_label']}<span class="views" data-views="{post['slug']}" hidden></span></p>
    <h2>{html.escape(post['title'])}</h2>
    <p class="dek">{html.escape(post['dek'])}</p>
  </div>
</a>"""
        )
    index_body = f"""{header(lang, 'index.html', index_root)}
<main class="wrap">
  <section class="hero">
    <h1>{html.escape(strings['hero'])}</h1>
    <p class="lede">{html.escape(strings['lede'])}</p>
  </section>
  <section class="grid">
    {''.join(cards)}
  </section>
</main>
{footer()}
"""
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        page(lang, "index.html", "RoboGarden", strings["description"], index_body, index_root),
        encoding="utf-8",
    )

    posts_dir = out / "posts"
    posts_dir.mkdir(exist_ok=True)
    for post in rendered:
        media = f"{post_root}media/{post['slug']}"
        figs = "\n".join(
            f"""<figure>
  <img src="{media}/{name}" alt="{html.escape(caption[lang])}">
  <figcaption>{html.escape(caption[lang])}</figcaption>
</figure>"""
            for name, caption in post["figures"]
        )
        vids = "\n".join(
            f"""<figure>
  <video controls playsinline preload="metadata" poster="{media}/{poster_name}">
    <source src="{media}/{name}" type="video/mp4">
  </video>
  <figcaption>{html.escape(caption[lang])}</figcaption>
</figure>"""
            for name, poster_name, caption in post["videos"]
        )
        rel = f"posts/{post['slug']}.html"
        body = f"""{header(lang, rel, post_root)}
<article class="post" data-slug="{post['slug']}">
  <a class="back" href="../index.html">{strings['back']}</a>
  <p class="kicker">{html.escape(post['tag'])} · {post['date_label']}</p>
  <h1>{html.escape(post['title'])}</h1>
  <p class="byline"><strong>Charles Yang</strong><span class="views" data-views="{post['slug']}" hidden></span></p>
  <div class="figures">
    {figs}
  </div>
  <div class="videos">
    {vids}
  </div>
  <div class="prose">
    {post['prose']}
  </div>
</article>
{footer()}
"""
        (posts_dir / f"{post['slug']}.html").write_text(
            page(lang, rel, f"{post['title']} · RoboGarden", post["dek"], body, post_root),
            encoding="utf-8",
        )
        print(lang, post["slug"], "ok")


def build() -> None:
    prepare_local_media()
    for post in POSTS:
        copy_post_media(post)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copy2(Path(__file__).resolve().parent / "views.js", DOCS / "views.js")
    for lang in LANGS:
        build_lang(lang)


if __name__ == "__main__":
    build()
