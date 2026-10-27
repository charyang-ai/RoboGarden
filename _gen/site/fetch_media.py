"""Download post media into _work. Safe to re-run; skips existing files."""

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "_work"
WORK.mkdir(parents=True, exist_ok=True)

FILES = {
    "iws-pusht.mp4": "https://www.yixuanwang.me/interactive_world_sim/media/videos/10min/pusht.mp4",
    "iws-rope.mp4": "https://www.yixuanwang.me/interactive_world_sim/media/videos/10min/rope.mp4",
    "iws-mug.mp4": "https://www.yixuanwang.me/interactive_world_sim/media/videos/10min/mug.mp4",
    "iws-correlation.png": "https://www.yixuanwang.me/interactive_world_sim/media/figures/correlation.png",
    "iws-pusht-init.png": "https://www.yixuanwang.me/interactive_world_sim/media/figures/pusht_init.png",
    "iws-rope-init.png": "https://www.yixuanwang.me/interactive_world_sim/media/figures/bimanual_rope_init.png",
    "iws-mug-init.png": "https://www.yixuanwang.me/interactive_world_sim/media/figures/single_grasp_init.png",
    "pw-card.jpg": "https://point-world.github.io/media/preview-card-1080p.jpg",
    "pw-scarf.mp4": "https://point-world.github.io/media/videos/scarf.mp4",
    "pw-tissue.mp4": "https://point-world.github.io/media/videos/tissuebox.mp4",
    "pw-broom.mp4": "https://point-world.github.io/media/videos/broom.mp4",
    "ws-figure.png": "https://haoyi-duan.github.io/WorldScore/assets/images/overview/full_screen.png",
    "ws-camera.mp4": "https://haoyi-duan.github.io/WorldScore/assets/videos/control/camera_control/4.mp4",
}


def fetch(name: str, url: str) -> None:
    dest = WORK / name
    if dest.exists() and dest.stat().st_size > 0:
        print(f"skip {name} {dest.stat().st_size}")
        return
    print(f"get  {name}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    print(f"done {name} {dest.stat().st_size}")


if __name__ == "__main__":
    for name, url in FILES.items():
        fetch(name, url)
