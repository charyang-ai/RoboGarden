"""Figures and clips for the Masked Visual Actions note, from the W7900 runs in charyang-ai/masked-visual-actions results/.

Reads MVA_RESULTS (default: PhysicalAI/RadeonGarden/masked-visual-actions/results next to this repository).
The final runs have both DiffSynth patches; towel_pinned_sdpa_final.jpg also shows the runs before them.
"""

import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "images"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = Path(os.environ.get("MVA_RESULTS", HERE.parents[2] / "RadeonGarden" / "masked-visual-actions" / "results"))
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\charyang\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

if __name__ == "__main__":
    # Rows: masked visual action, W7900, authors, real video; five frames across the clip.
    shutil.copy2(RESULTS / "full_towel_50step_final" / "compare_towel.jpg", OUT / "mva-towel.jpg")
    shutil.copy2(RESULTS / "full_behavior_50step_final" / "compare_behavior.jpg", OUT / "mva-behavior.jpg")
    # Rows: as pinned, SDPA patch only, both patches, authors, real video.
    shutil.copy2(RESULTS / "towel_pinned_sdpa_final.jpg", OUT / "mva-towel-patches.jpg")
    for name, at in (("towel", "2.6"), ("behavior", "2.6")):
        mp4 = OUT / f"mva-{name}.mp4"
        shutil.copy2(RESULTS / f"full_{name}_50step_final" / f"{name}.mp4", mp4)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", at, "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                        str(OUT / f"frame-mva-{name}.jpg")], check=True)
    print(OUT)
