"""Screenshot the built page at desktop and phone width for review (needs the preview server).

    cd RoboGardenSite && python -m http.server 8766 --bind 127.0.0.1
    python shots.py        -> _work/desktop_<n>.jpg, _work/mobile_sheet.jpg
"""

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

WORK = Path(__file__).resolve().parent / "_work"
URL = "http://127.0.0.1:8766/projects/atlas-robotics/"
EDGE = next(p for p in (Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
                        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")) if p.exists())


def shot(name, width, height):
    out = WORK / f"{name}.png"
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={width},{height}", "--virtual-time-budget=6000",
                    f"--screenshot={out}", URL], check=True, capture_output=True)
    im = Image.open(out).convert("RGB")
    a = np.asarray(im)
    # last row that differs from the bottom-right background pixel = end of content
    diff = np.abs(a.astype(int) - a[-1, -1].astype(int)).sum(axis=2).max(axis=1)
    bottom = int(np.where(diff > 30)[0].max()) + 1
    print(name, im.size, "content ends at", bottom)
    return im.crop((0, 0, im.width, min(im.height, bottom + 40)))


def main():
    WORK.mkdir(exist_ok=True)
    d = shot("page_desktop", 1280, 6400)
    step = 1400
    for i in range(0, d.height, step):
        d.crop((0, i, d.width, min(d.height, i + step))).save(WORK / f"desktop_{i // step}.jpg", quality=85)
    m = shot("page_mobile", 520, 9000)  # headless Edge will not lay out narrower than about 500 px
    n = 4
    hh = -(-m.height // n)
    sheet = Image.new("RGB", ((m.width + 10) * n, hh), "white")
    for i in range(n):
        sheet.paste(m.crop((0, i * hh, m.width, min(m.height, (i + 1) * hh))), (i * (m.width + 10), 0))
    sheet.save(WORK / "mobile_sheet.jpg", quality=88)


if __name__ == "__main__":
    main()
