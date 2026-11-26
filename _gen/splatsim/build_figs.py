"""Figures and the clip for the SplatSim note, from the W7900 run in charyang-ai/splatsim results/.

Reads SPLATSIM_RESULTS (default: PhysicalAI/RadeonGarden/splatsim/results next to this repository).
"""

import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "images"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = Path(os.environ.get("SPLATSIM_RESULTS", HERE.parents[2] / "RadeonGarden" / "splatsim" / "results"))
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"


def jpeg(img: Image.Image, name: str, max_w: int = 1600) -> None:
    img = img.convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.Resampling.LANCZOS)
    img.save(OUT / name, quality=86, optimize=True)


if __name__ == "__main__":
    # W7900 render | authors' CUDA render / real photo | |difference|, training view frame_00004.
    shutil.copy2(RESULTS / "check_render" / "view3_comparison.jpg", OUT / "ss-render-check.jpg")
    # Six replayed trajectories, one per row: first, 1/3, 2/3 and last frame.
    jpeg(Image.open(RESULTS / "replay" / "contact_sheet.jpg"), "ss-contact-sheet.jpg")
    # Xvfb at minute 2 of the replay: the cv2.imshow window over the PyBullet GUI; the rest of the 1920x1080 screen is empty.
    jpeg(Image.open(RESULTS / "replay" / "display.png").crop((0, 0, 1026, 770)), "ss-display.jpg")
    mp4 = OUT / "ss-trajectory0.mp4"
    shutil.copy2(RESULTS / "replay" / "trajectory_0.mp4", mp4)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "2.5", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                    str(OUT / "frame-ss-trajectory0.jpg")], check=True)
    print(OUT)
