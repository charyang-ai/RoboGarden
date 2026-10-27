"""Build the public RoboGarden site into docs/ from the essay markdown."""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
WORK = Path(__file__).resolve().parent / "_work"
GARDEN = Path(r"C:\Users\charyang\OneDrive - Advanced Micro Devices Inc\PhysicalAI\RadeonGarden")
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
SITE = "https://charyang-ai.github.io/RoboGarden"

TOKEN = re.compile(
    r"`([^`]+)`"
    r"|\[([^\]]+)\]\(([^)]+)\)"
    r"|<(https?://[^>\s]+)>"
    r"|(https?://[^\s<>）)。，、]+)"
)

POSTS = [
    {
        "slug": "roborender",
        "tag": "RoboRender",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": ROOT / "roborender-video-model.md",
        "dek": "仿真继续负责几何和动作，视频模型负责把这条轨迹画成真实世界里的颜色。",
        "thumb": "rr-frame.png",
        "figures": [
            ("rr-comparison.png", "第 40 帧。从左到右是深度、机械臂掩码、画出来的画面；三行是三个视角。提示词要一只红杯子，几何给的是椭圆，椭圆就变成了一把勺子。"),
        ],
        "videos": [
            ("rr-comparison.mp4", "rr-comparison.png", "同一次 50 步推理的对比视频。每一行一个视角，列是深度、掩码、生成结果。"),
            ("rr-head.mp4", "rr-head.jpg", "头部相机画出的 81 帧。"),
            ("rr-left.mp4", "rr-left.jpg", "左手相机。"),
            ("rr-right.mp4", "rr-right.jpg", "右手相机。"),
        ],
    },
    {
        "slug": "worldscore",
        "tag": "WorldScore",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": ROOT / "worldscore.md",
        "dek": "镜头往前推的时候，吧台还在不在原来的地方。WorldScore 把这件事拆开打分。",
        "thumb": "ws-figure.png",
        "figures": [
            ("ws-figure.png", "WorldScore 要覆盖的那些世界：室内和室外、写实和风格化。图来自 WorldScore 项目页。"),
        ],
        "videos": [
            ("ws-overview.mp4", "frame-ws-overview.jpg", "基准怎么考下一条镜头：从一张起始图出发，模型得按相机指令长出下一个场景。"),
            ("ws-camera.mp4", "frame-ws-camera.jpg", "相机控制的对照。同一句指令，一边听得懂，一边把湖面和山形换了一套。"),
        ],
    },
    {
        "slug": "interactive-world-sim",
        "tag": "Interactive World Simulator",
        "date": "2026-10-27",
        "date_label": "2026.10.27",
        "src": ROOT / "interactive_world_sim.md",
        "dek": "给一帧画面和一串动作，在像素里把下一秒演完，中间不请物理引擎当裁判。",
        "thumb": "frame-iws-pusht.jpg",
        "figures": [
            ("iws-correlation.png", "同一批策略，在世界模型里的分数和在真机上的分数。点靠近对角线，说明排序对得上。图来自项目页。"),
        ],
        "videos": [
            ("iws-pusht.mp4", "frame-iws-pusht.jpg", "推一个 T 形块。左边是模型开环画出来的画面，右边是人在遥操作。"),
            ("iws-rope.mp4", "frame-iws-rope.jpg", "把绳子送向夹子。进了夹子，和从旁边荡过去，是两段不同的视频。"),
            ("iws-mug.mp4", "frame-iws-mug.jpg", "抓一只杯子。滑出指缝，和杯把被顶着转，都是很小的像素变化。"),
        ],
    },
    {
        "slug": "pointworld",
        "tag": "PointWorld",
        "date": "2026-10-26",
        "date_label": "2026.10.26",
        "src": ROOT / "pointworld.md",
        "dek": "状态和动作说同一种语言。给一张 RGB-D，预言每一个点下一秒往哪里走。",
        "thumb": "frame-pw-scarf.jpg",
        "figures": [
            ("pw-card.jpg", "动作也是一团点：夹爪上的点往前走，场景里的点跟着动。图来自 PointWorld 项目页。"),
        ],
        "videos": [
            ("pw-scarf.mp4", "frame-pw-scarf.jpg", "叠围巾。同一个预训练检查点，不做任务微调。"),
            ("pw-tissue.mp4", "frame-pw-tissue.jpg", "推纸巾盒。"),
            ("pw-broom.mp4", "frame-pw-broom.jpg", "拿扫帚扫地。"),
        ],
    },
    {
        "slug": "ctrl-world",
        "tag": "Ctrl-World",
        "date": "2026-10-26",
        "date_label": "2026.10.26",
        "src": ROOT / "BLOG.md",
        "dek": "让策略在想象里把操作滚完。想象只要足够听话，排名就可以先在显卡上排出来。",
        "thumb": "frame-ctrl-banana.jpg",
        "figures": [
            ("ctrl-diagram.jpg", "策略出动作，世界模型长出下一秒的三台相机，记忆把更早的画面留在回路里。"),
        ],
        "videos": [
            ("banana.mp4", "frame-ctrl-banana.jpg", "把香蕉往右挪。上排是记录下来的真值，下排是世界模型在一张 W7900 上想象出来的三台相机。"),
            ("black.mp4", "frame-ctrl-black.jpg", "把椅子上的黑东西放到桌上。"),
            ("towel.mp4", "frame-ctrl-towel.jpg", "把绿毛巾挪到盖子右边。"),
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


def page(title: str, description: str, css: str, body: str, depth: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="author" content="Charles Yang">
  <link rel="icon" href="{depth}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,640&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+SC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css}">
</head>
<body>
{body}
</body>
</html>
"""


def header(depth: str) -> str:
    return f"""<header class="site-header">
  <a class="wordmark" href="{depth}index.html">Robo<span>Garden</span></a>
  <a class="who" href="{depth}index.html">Charles Yang</a>
</header>
"""


def footer(depth: str) -> str:
    return f"""<footer class="site-footer">
  <span>Charles Yang</span>
  <a href="https://github.com/charyang-ai/RoboGarden">GitHub</a>
</footer>
"""


def prepare_local_media() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    pairs = {
        "ctrl-diagram.jpg": GARDEN / "ctrl-world" / "synthetic_traj" / "gallery" / "ctrl_world.jpg",
        "banana-src.mp4": GARDEN / "ctrl-world" / "results" / "videos" / "time_20261025_155637_traj_899_8_5_Move_the_banana_to_the_right.mp4",
        "black-src.mp4": GARDEN / "ctrl-world" / "results" / "videos" / "time_20261025_155936_traj_18599_14_5_Pick_the_black_thing_from_the_.mp4",
        "towel-src.mp4": GARDEN / "ctrl-world" / "results" / "videos" / "time_20261025_160225_traj_199_8_5_Move_the_green_towel_to_the_ri.mp4",
        "ws-overview.mp4": GARDEN / "worldscore" / "assets" / "overview.mp4",
        "rr-comparison.png": GARDEN / "roborender-video-model" / "results" / "frame40_comparison.png",
        "rr-frame.png": GARDEN / "roborender-video-model" / "results" / "frame40_generated_hand_left.png",
        "rr-comparison.mp4": GARDEN / "roborender-video-model" / "results" / "comparison.mp4",
        "rr-head.mp4": GARDEN / "roborender-video-model" / "results" / "generated_head_color.mp4",
        "rr-left.mp4": GARDEN / "roborender-video-model" / "results" / "generated_hand_left.mp4",
        "rr-right.mp4": GARDEN / "roborender-video-model" / "results" / "generated_hand_right.mp4",
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


def build() -> None:
    prepare_local_media()
    media = DOCS / "media"
    media.mkdir(parents=True, exist_ok=True)

    rendered = []
    for post in POSTS:
        slug = post["slug"]
        folder = media / slug
        folder.mkdir(parents=True, exist_ok=True)
        title, prose = markdown_to_html(post["src"])
        thumb_name = "thumb.jpg"
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

        figures = []
        for name, caption in post["figures"]:
            copy_file(WORK / name, folder / name)
            figures.append((name, caption))
        videos = []
        for name, poster_name, caption in post["videos"]:
            src_name = {
                "banana.mp4": "banana-src.mp4",
                "black.mp4": "black-src.mp4",
                "towel.mp4": "towel-src.mp4",
            }.get(name, name)
            copy_file(WORK / src_name, folder / name)
            copy_file(WORK / poster_name, folder / poster_name)
            videos.append((name, poster_name, caption))
        rendered.append({**post, "title": title, "prose": prose, "figures": figures, "videos": videos, "thumb": thumb_name})

    cards = []
    for post in rendered:
        cards.append(
            f"""<a class="card" href="posts/{post['slug']}.html">
  <div class="thumb"><img src="media/{post['slug']}/{post['thumb']}" alt=""></div>
  <div class="card-body">
    <p class="meta">{html.escape(post['tag'])} · {post['date_label']}</p>
    <h2>{html.escape(post['title'])}</h2>
    <p class="dek">{html.escape(post['dek'])}</p>
  </div>
</a>"""
        )
    index_body = f"""{header('')}
<main class="wrap">
  <section class="hero">
    <h1>五次实验，五篇笔记。</h1>
    <p class="lede">每一篇是一次工作：在一张 Radeon Pro W7900 上把世界模型跑通，再把过程写下来。</p>
  </section>
  <section class="grid">
    {''.join(cards)}
  </section>
</main>
{footer('')}
"""
    (DOCS / "index.html").write_text(
        page("RoboGarden", "Charles Yang 的世界模型笔记。", "styles.css", index_body, ""),
        encoding="utf-8",
    )
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    posts_dir = DOCS / "posts"
    posts_dir.mkdir(exist_ok=True)
    for post in rendered:
        figs = "\n".join(
            f"""<figure>
  <img src="../media/{post['slug']}/{name}" alt="{html.escape(caption)}">
  <figcaption>{html.escape(caption)}</figcaption>
</figure>"""
            for name, caption in post["figures"]
        )
        vids = "\n".join(
            f"""<figure>
  <video controls playsinline preload="metadata" poster="../media/{post['slug']}/{poster_name}">
    <source src="../media/{post['slug']}/{name}" type="video/mp4">
  </video>
  <figcaption>{html.escape(caption)}</figcaption>
</figure>"""
            for name, poster_name, caption in post["videos"]
        )
        body = f"""{header('../')}
<article class="post">
  <a class="back" href="../index.html">← 全部笔记</a>
  <p class="kicker">{html.escape(post['tag'])} · {post['date_label']}</p>
  <h1>{html.escape(post['title'])}</h1>
  <p class="byline"><strong>Charles Yang</strong></p>
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
{footer('../')}
"""
        (posts_dir / f"{post['slug']}.html").write_text(
            page(f"{post['title']} · RoboGarden", post["dek"], "../styles.css", body, "../"),
            encoding="utf-8",
        )
        print(post["slug"], "ok")


if __name__ == "__main__":
    build()
