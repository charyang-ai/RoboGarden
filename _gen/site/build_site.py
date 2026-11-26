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
# Pages whose prose has \( \) or \[ \] math load KaTeX and render it in the browser.
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"

TOKEN = re.compile(
    r"`([^`]+)`"
    r"|\[([^\]]+)\]\(([^)]+)\)"
    r"|<(https?://[^>\s]+)>"
    r"|(https?://[^\s<>）)。，、]+)"
    r"|\*\*([^*]+)\*\*"
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
        "slug": "real2sim-eval",
        "tag": "Real2Sim-Eval",
        "date": "2026-11-26",
        "date_label": "2026.11.26",
        "src": {"zh": ROOT / "real2sim-eval.md", "en": ROOT / "en" / "real2sim-eval.md"},
        "dek": {
            "zh": "仿真想替真机给策略排名次，画面得对齐到那台相机，绳子的弹性得从视频里辨识出来。在一张 W7900 上跑完 27 组绳子评测：18 组成功，失败扎堆在网格的同一侧。",
            "en": "For simulation to rank policies the way the real robot does, the picture has to match that camera and the rope's springiness has to be identified from video. On one W7900 the 27-episode rope evaluation ends 18 for 27, with the failures bunched on one side of the grid.",
        },
        "thumb": "frame-r2s-ep13.jpg",
        "figures": [
            ("r2s-teaser.jpg", {
                "zh": "同一批策略，仿真成功率和真机成功率排在一条对角线上；三个任务是毛绒玩具装箱、绳子穿夹和推 T 形块。图来自项目页。",
                "en": "The same policies' success rates in simulation and on the real robot line up along the diagonal; the three tasks are packing a plush toy, threading a rope through a clip, and pushing a T block. Figure from the project page.",
            }),
            ("r2s-method.jpg", {
                "zh": "整套流程：手机扫描、高斯重建、位置和颜色对齐；从人手摆弄物体的视频里辨识出软体数字孪生；最后包成 Gym 接口。图来自项目页。",
                "en": "The pipeline: a phone scan, Gaussian reconstruction, position and color alignment; a soft-body digital twin identified from a video of hands handling the object; all wrapped in a Gym interface. Figure from the project page.",
            }),
            (
                {"zh": "r2s-grid.png", "en": "r2s-grid_en.png"},
                {
                    "zh": "W7900 上 27 个初值的结局，按 x、y 偏移和转角排开，格子里是回合编号。",
                    "en": "Outcomes of the 27 initial states on the W7900, laid out by x and y offset and by rotation; each cell shows the episode id.",
                },
            ),
            (
                {"zh": "r2s-steptime.png", "en": "r2s-steptime_en.png"},
                {
                    "zh": "每个回合计分那次运行的控制步耗时中位数。失败的回合都在 3.3 秒以下，成功的都在 4 秒以上。",
                    "en": "Median control-step time of each episode's scored run. Every failed episode is under 3.3 s; every successful one takes 4 s or more.",
                },
            ),
        ],
        "videos": [
            ("r2s-sim-vs-real.mp4", "frame-r2s-sim-vs-real.jpg", {
                "zh": "绳子任务，同一个策略、同一个初值，左边是仿真，右边是真机。视频来自项目页。",
                "en": "The rope task with the same policy from the same initial state: simulation on the left, the real robot on the right. Video from the project page.",
            }),
            ("r2s-ep13.mp4", "frame-r2s-ep13.jpg", {
                "zh": "W7900 上的 13 号回合（x、y 偏移都是 0，转角 0°）：绳子穿过夹子的两个开口，成功。相机 0，30 秒，900 个控制步。",
                "en": "Episode 13 on the W7900 (x and y offsets 0, rotation 0°): the rope passes through both openings of the clip, a success. Camera 0, 30 seconds, 900 control steps.",
            }),
            ("r2s-ep14.mp4", "frame-r2s-ep14.jpg", {
                "zh": "14 号回合，位置相同，只多转了 10°：绳子落在夹子旁边，失败。",
                "en": "Episode 14, same position, rotated 10° more: the rope ends up beside the clip, a failure.",
            }),
        ],
    },
    {
        "slug": "atlas-dm05",
        "tag": "World Labs Atlas",
        "date": "2026-11-25",
        "date_label": "2026.11.25",
        "src": {"zh": ROOT / "atlas-dm05.md", "en": ROOT / "en" / "atlas-dm05.md"},
        "dek": {
            "zh": "同一个策略、同一批种子，只把背景换成一间真实厨房的 3D 高斯，一半回合换了结局。在部署场景里渲染训练数据，成功率高 17 个点，换到另一张卡上仍然成立。",
            "en": "Same policy, same seeds, only the background swapped for a 3D Gaussian reconstruction of a real kitchen, and half the episodes change outcome. Rendering training data in the deployment scene lifts success by 17 points, and the gain holds on a second GPU.",
        },
        "thumb": "atlas-thumb.jpg",
        "figures": [
            ("atlas-seed_agreement.png", {
                "zh": "同一份权重、同一批 50 个种子，原生画面和 3DGS 外壳下逐种子的成败（绿：成功，橙框：两边结局不同）。两边都成功的只有 6 个，25 个回合只在其中一边成功，19 个两边都失败。",
                "en": "Same weights, same 50 seeds: per-seed outcome under the native render and under the 3DGS shell (green: success; orange outline: the two sides disagree). Only 6 episodes succeed on both sides, 25 succeed on one side only, and 19 fail on both.",
            }),
            ("atlas-reconstruction.jpg", {
                "zh": "左边是训练时没用过的原始照片，右边是同一机位的 3DGS 渲染：1,458,354 个高斯，PSNR 27.9 dB，SSIM 约 0.94。",
                "en": "Left: a photo held out from training. Right: the 3DGS render from the same viewpoint, 1,458,354 Gaussians, PSNR 27.9 dB, SSIM about 0.94.",
            }),
            ("atlas-relight_looks.jpg", {
                "zh": "Atlas Relight 给同一间厨房打的五种光照：原始、金色黄昏、夜班、台灯用于训练，霓虹留出不训练。",
                "en": "The five lightings Atlas Relight gives the same kitchen: captured, golden hour, night shift and lamp are used for training; neon is held out.",
            }),
            ("atlas-robot_views.jpg", {
                "zh": "复位时机器人三路相机在五种光照下看到的画面（红框是留出的霓虹）。台面以下和机器人都由 MuJoCo 渲染，只有台面以上的背景被重新打光。",
                "en": "What the robot's three cameras see at reset under the five lightings (the red frame is the held-out neon). Everything below the counter and the robot is rendered by MuJoCo; only the background above the counter is relit.",
            }),
            (
                {"zh": "atlas-success_rates_final.png", "en": "atlas-success_rates_final_en.png"},
                {
                    "zh": "在 R9700 上测得的闭环成功率，误差线是 Wilson 95% 区间。",
                    "en": "Closed-loop success rates measured on the R9700. Error bars are Wilson 95% intervals.",
                },
            ),
            (
                {"zh": "atlas-ci_vs_n.png", "en": "atlas-ci_vs_n_en.png"},
                {
                    "zh": "95% 区间半宽随评测回合数的变化。真实成功率在 43% 上下时，50 个回合约正负 13 个点，100 个回合约正负 10 个点，200 个回合约正负 7 个点。",
                    "en": "Half-width of the 95% interval against the number of episodes. With a true success rate near 43%, 50 episodes give about ±13 points, 100 give about ±10, and 200 give about ±7.",
                },
            ),
            (
                {"zh": "atlas-drift_seeds.png", "en": "atlas-drift_seeds_en.png"},
                {
                    "zh": "同一个发布版模型、同一间厨房、同一批 50 个种子：8 月 18/50，11 月 10/50，12 个种子翻转（橙框），其中 10 个由成功变失败。",
                    "en": "The same released model, the same kitchen, the same 50 seeds: 18/50 in August, 10/50 in November. 12 seeds flip (orange outline), 10 of them from success to failure.",
                },
            ),
            (
                {"zh": "atlas-xmachine.png", "en": "atlas-xmachine_en.png"},
                {
                    "zh": "跨机器复现。左：同一批 200 个种子在两台机器上的成功率；右：同一个模型、同一个种子换一台机器后结果翻转的比例，最下面一行是同一台机器重跑一遍作为对照。",
                    "en": "Cross-machine replication. Left: success rates on the same 200 seeds on two machines. Right: the share of seeds whose outcome flips for the same model on another machine; the bottom row is a rerun on the same machine as a control.",
                },
            ),
            ("atlas-w7900_synthetic_check.jpg", {
                "zh": "合成房间的机器人视角检查。上排是 DL3DV 厨房，下排是合成的棋盘格房间。两个腕部相机的画面顶部都能看到合成房间的墙，说明对齐和合成在 W7900D 上是通的。",
                "en": "Robot-view check of a synthetic room. Top: the DL3DV kitchen. Bottom: a synthetic checkerboard room. The synthetic room's wall shows at the top of both wrist-camera views, so alignment and compositing work on the W7900D.",
            }),
        ],
        "videos": [],
    },
    {
        "slug": "le-wm",
        "tag": "LeWorldModel",
        "date": "2026-11-22",
        "date_label": "2026.11.22",
        "src": {"zh": ROOT / "le-wm.md", "en": ROOT / "en" / "le-wm.md"},
        "dek": {
            "zh": "一张画面压成 192 个数，规划在这 192 维里做完。一道正态性检验，管住了 JEPA 的坍塌。",
            "en": "One image becomes 192 numbers, and planning happens inside those 192 dimensions. A normality test keeps the JEPA from collapsing.",
        },
        "thumb": "frame-lewm-cube.jpg",
        "figures": [
            ("lewm-results.png", {
                "zh": "四个环境的规划成功率。浅色是论文的数，深绿是作者发布的权重在 W7900 上重评（Two-Room 和 Reacher 是三个种子、150 回合的平均），红褐色是在 W7900 上从头训练的 Two-Room，虚线是随机策略。",
                "en": "Planning success in the four environments. Sand: the paper. Green: the authors' released checkpoints re-evaluated on the W7900 (Two-Room and Reacher are the mean of three seeds, 150 episodes). Clay: Two-Room trained from scratch on the W7900. Dashed: the random policy.",
            }),
            ("lewm-reacher-floor.png", {
                "zh": "把数据集里同一个状态写回 Reacher 环境再画一张。MuJoCo 4.0.1 只画出一整块深蓝，数据集里是四格棋盘，平均差 20 个灰度级；钉回 3.11.0 后平均差 2.6，剩下的主要是机械臂边上的一圈。",
                "en": "The same dataset state written back into the Reacher environment and rendered again. MuJoCo 4.0.1 draws one flat dark-blue floor where the dataset has a four-square checkerboard, a mean difference of 20 gray levels; pinned back to 3.11.0 the difference is 2.6, mostly a thin outline around the arm.",
            }),
            ("lewm-train.png", {
                "zh": "Two-Room 从头训练 10 个 epoch，每个 epoch 结束时在留出数据上的验证损失（对数坐标）。总损失是预测损失加 0.09 倍的 SIGReg。",
                "en": "Validation loss on held-out data at the end of each of the 10 epochs of training Two-Room from scratch (log scale). The total is the prediction loss plus 0.09 times SIGReg.",
            }),
        ],
        "videos": [
            ("lewm-pusht.mp4", "frame-lewm-pusht.jpg", {
                "zh": "Push-T，作者发布的权重。左：智能体按 LeWM 的规划执行；中：数据集里的原轨迹；右：25 步之后的目标。",
                "en": "Push-T with the released checkpoint. Left: the agent executing LeWM's plan; middle: the original trajectory in the dataset; right: the goal 25 steps later.",
            }),
            ("lewm-tworoom.mp4", "frame-lewm-tworoom.jpg", {
                "zh": "Two-Room，在 W7900 上从头训练的权重。",
                "en": "Two-Room with the checkpoint trained from scratch on the W7900.",
            }),
            ("lewm-cube.mp4", "frame-lewm-cube.jpg", {
                "zh": "OGBench-Cube，作者发布的权重。MuJoCo 由 Mesa 的 radeonsi 驱动在 W7900 上画。",
                "en": "OGBench-Cube with the released checkpoint. MuJoCo renders on the W7900 through Mesa's radeonsi driver.",
            }),
        ],
    },
    {
        "slug": "mujoco4",
        "tag": "MuJoCo 4",
        "date": "2026-11-12",
        "date_label": "2026.11.12",
        "src": {"zh": ROOT / "mujoco4.md", "en": ROOT / "en" / "mujoco4.md"},
        "dek": {
            "zh": "小挠度下，端部反力和欧拉-伯努利公式一致到百万分之二。挠到梁长的 6.8%，先离开的是线性公式。",
            "en": "At small deflection the tip force matches Euler-Bernoulli to about two parts in a million. At 6.8% of the length, the linear formula is what leaves.",
        },
        "thumb": "mujoco4-beam.png",
        "figures": [
            ("mujoco4-beam.png", {
                "zh": "维持形状所需的端部力，除以线性理论的力。绿带是公告里的 0.5%。小挠度在 1.0000，梁长的 6.8% 落到 0.980。15 到 63 段，比值不变。",
                "en": "Tip force required to hold the shape, divided by the linear-theory force. The green band is the announced 0.5%. Small deflection sits at 1.0000; 6.8% of the length falls to 0.980. From 15 to 63 segments the ratio does not move.",
            }),
            ("mujoco4-plastic.png", {
                "zh": "同一只铰先掰到 1 弧度再松开。不设屈服就回到 0。屈服 0.3 弧度时停在 0.698，虚线是应停的 0.700。",
                "en": "The same hinge, bent to 1 radian and released. With no yield it returns to 0. With a 0.3 radian yield it rests at 0.698. The dashed line is the 0.700 it should rest at.",
            }),
        ],
        "videos": [],
    },
    {
        "slug": "masked-visual-actions",
        "tag": "Masked Visual Actions",
        "date": "2026-11-11",
        "date_label": "2026.11.11",
        "src": {"zh": ROOT / "masked-visual-actions.md", "en": ROOT / "en" / "masked-visual-actions.md"},
        "dek": {
            "zh": "把机械臂这一路画出来，其余涂灰，剩下的交给视频模型补完：露出机械臂它演世界，露出杯子它演机器人。在 W7900 上，SDPA 这条退路成了主路，VAE 里悄悄算错的注意力换回了精确内核。",
            "en": "Draw the arm's path, gray out the rest, and let a video model fill in the world: show it the arm and it plays the world, show it the cup and it plays the robot. On a W7900 the SDPA fallback became the main road, and a quietly wrong attention in the VAE went back to the exact kernel.",
        },
        "thumb": "frame-mva-towel.jpg",
        "figures": [
            ("mva-towel.jpg", {
                "zh": "毛巾片段（真机 Franka，定制夹爪），从上到下：遮罩视觉动作、W7900 的生成、作者的生成、真实视频。控制视频里画的是标准 Franka 夹爪，生成的却是参考帧里那对绿色 3D 打印手指；毛巾掀起后，W7900 这一版把露出来的桌面画成了一块木板。",
                "en": "The towel clip (a real Franka with custom fingers), top to bottom: the masked visual action, the W7900 generation, the authors' generation, the real video. The control video draws a standard Franka gripper, yet the generations show the green 3D-printed fingers from the reference frame; once the towel is lifted, the W7900 run paints the uncovered table as a wooden board.",
            }),
            ("mva-behavior.jpg", {
                "zh": "BEHAVIOR 片段（R1 Pro，训练时没见过的双臂机器人），同样四行：遮罩视觉动作、W7900、作者、真实视频。",
                "en": "The BEHAVIOR clip (an R1 Pro, a two-armed robot never seen in training), in the same four rows: masked visual action, W7900, authors, real video.",
            }),
            ("mva-towel-patches.jpg", {
                "zh": "同一个种子下两个补丁的作用。从上到下：上游原样；只打 SDPA 排布补丁，和上一行平均只差 1.3 个灰度级；再把 VAE 里头维度 384 的注意力换成精确内核，毛巾掀起后露出的桌面变成了木板；作者的生成；真实视频。",
                "en": "What the two patches do with the same seed. Top to bottom: upstream as pinned; the SDPA layout patch alone, a mean of 1.3 gray levels from the row above; the head-dim-384 attention in the VAE also routed to the exact kernel, after which the table under the lifted towel becomes a wooden board; the authors' generation; the real video.",
            }),
        ],
        "videos": [
            ("mva-towel.mp4", "frame-mva-towel.jpg", {
                "zh": "W7900 上生成的毛巾片段，两个补丁都打上：832×480，81 帧，15 fps，50 步。",
                "en": "The towel clip generated on the W7900 with both patches: 832×480, 81 frames at 15 fps, 50 steps.",
            }),
            ("mva-behavior.mp4", "frame-mva-behavior.jpg", {
                "zh": "W7900 上生成的 BEHAVIOR 片段（R1 Pro）。",
                "en": "The BEHAVIOR clip (R1 Pro) generated on the W7900.",
            }),
        ],
    },
    {
        "slug": "splatsim",
        "tag": "SplatSim",
        "date": "2026-11-05",
        "date_label": "2026.11.05",
        "src": {"zh": ROOT / "splatsim.md", "en": ROOT / "en" / "splatsim.md"},
        "dek": {
            "zh": "物理留给 PyBullet，画面换成真实场景的两百万个高斯，按关节角搬家。在 W7900 上重画作者的训练视角，和 CUDA 版最多差一个灰度级；420 条轨迹全部重拍。",
            "en": "Physics stays in PyBullet; the picture becomes two million Gaussians of the real scene, moved by joint angle. Redrawn on a W7900, the authors' training views differ from their CUDA renders by at most one gray level, and all 420 trajectories are reshot.",
        },
        "thumb": "frame-ss-trajectory0.jpg",
        "figures": [
            ("ss-render-check.jpg", {
                "zh": "同一份 2,192,636 个高斯的 splat、同一个训练视角。左上是 W7900 画的，右上是作者用 CUDA 画的，左下是真实照片，右下是两张渲染图之差，白点是差一个灰度级的像素。两张渲染图之间的 PSNR 是 96.9 dB。",
                "en": "The same 2,192,636-Gaussian splat from the same training view. Top left: drawn on the W7900. Top right: the authors' CUDA render. Bottom left: the real photo. Bottom right: the difference between the two renders, where white dots are pixels one gray level apart. PSNR between the two renders is 96.9 dB.",
            }),
            ("ss-contact-sheet.jpg", {
                "zh": "W7900 重拍的苹果放盘子数据，抽了六条轨迹，每行一条，从左到右是首帧、三分之一、三分之二和末帧。盘子是那块黑色圆盘，发布的盘子 splat 本来就是这个颜色。",
                "en": "Six of the apple-on-plate trajectories reshot on the W7900, one per row: first frame, one third, two thirds and last frame. The plate is the black disc; the released plate splat really is that color.",
            }),
            ("ss-display.jpg", {
                "zh": "回放进行到第 2 分钟时那台虚拟显示器的截图：前面是 cv2.imshow 的窗口，两百万个高斯在 W7900 上画；后面是 PyBullet 的 GUI，由 llvmpipe 在 CPU 上画。",
                "en": "The virtual display two minutes into the replay: in front, the cv2.imshow window, two million Gaussians drawn on the W7900; behind it, the PyBullet GUI, drawn on the CPU by llvmpipe.",
            }),
        ],
        "videos": [
            ("ss-trajectory0.mp4", "frame-ss-trajectory0.jpg", {
                "zh": "第一条轨迹的回放，800×448，15 fps。",
                "en": "Replay of the first trajectory, 800×448 at 15 fps.",
            }),
        ],
    },
    {
        "slug": "world2act",
        "tag": "World2Act",
        "date": "2026-11-01",
        "date_label": "2026.11.01",
        "src": {"zh": ROOT / "world2act.md", "en": ROOT / "en" / "world2act.md"},
        "dek": {
            "zh": "一个会画下一秒的视频模型，潜空间里已经含着动作。先把它的老师请上一张 W7900：35 步校正流画完一段芒果，前提是给 25.6 GiB 的卷积展开表腾出地方。",
            "en": "A video model that can draw the next second already carries actions in its latents. First its teacher moves onto one W7900: 35 rectified-flow steps paint the mango clip, once a 25.6 GiB convolution table is given room.",
        },
        "thumb": "frame-w2a-robocasa.jpg",
        "figures": [
            ("w2a-motivation.jpg", {
                "zh": "左边是常见的像素空间后训练，从想象出来的画面里反推伪动作或奖励；中间是 World2Act，直接在潜空间里对齐；右边是 RoboCasa 成功率随后训练轨迹数的变化。图来自项目页（论文图 1）。",
                "en": "Left: the usual pixel-space post-training, which recovers pseudo-actions or rewards from imagined frames. Middle: World2Act, which aligns in latent space directly. Right: RoboCasa success rate against the number of post-training trajectories. Figure from the project page (Fig. 1 of the paper).",
            }),
            ("w2a-method.jpg", {
                "zh": "(a) 第一阶段，视频适配器和动作适配器把世界模型潜变量和专家动作块映射到同一个共享空间，动作解码器负责重建；(b) 第二阶段，冻住世界模型、VLA 和第一阶段的模块，只训一个残差策略。图来自项目页（论文图 2）。",
                "en": "(a) Stage one: a video adapter and an action adapter map world-model latents and expert action chunks into one shared space, and an action decoder reconstructs the actions. (b) Stage two: the world model, the VLA and the stage-one modules are frozen and only a residual policy is trained. Figure from the project page (Fig. 2 of the paper).",
            }),
            ("w2a-imagine-vs-real.jpg", {
                "zh": "上排是世界模型想象的关微波炉，下排是 GR00T-N1.6-ft + World2Act 在真机上的执行。作者指出，想象的最后一帧里把手消失了，真机照样把门关上。图来自项目页。",
                "en": "Top: the world model imagining a microwave being closed. Bottom: GR00T-N1.6-ft + World2Act doing the task on the real robot. The authors point out that the handle vanishes in the last imagined frame and the robot still closes the door. Figure from the project page.",
            }),
            (
                {"zh": "frame-w2a-mango.jpg", "en": "frame-w2a-mango_en.jpg"},
                {
                    "zh": "这次在 W7900 上生成的 93 帧里抽出 6 帧。第 0 帧就是条件图；一秒之内，左半边被画成白色橱柜、两只芒果和一只伸进来的夹爪，右半边一直是色块。",
                    "en": "Six of the 93 frames generated on the W7900. Frame 0 is the conditioning image; within a second the left half becomes white cabinets, two mangoes and a gripper reaching in, while the right half stays blocks of color.",
                },
            ),
            (
                {"zh": "w2a-memory.png", "en": "w2a-memory_en.png"},
                {
                    "zh": "改之前，上一层的展开表还占着 24.7 GiB，下一层要的 25.6 GiB 放不下；卷积前清一次缓存，活张量加这一层的表一共 34 GiB 出头。",
                    "en": "Before the fix, the previous layer's unfolded table still holds 24.7 GiB, and the 25.6 GiB the next layer needs does not fit; emptying the cache before the convolution leaves the live tensors plus this layer's table at a little over 34 GiB.",
                },
            ),
        ],
        "videos": [
            ("w2a-robocasa.mp4", "frame-w2a-robocasa.jpg", {
                "zh": "这次生成的视频：一张条件图加一句“pick the mango from the cabinet”，35 步校正流，93 帧，16 fps。",
                "en": "The video generated this time: one conditioning image plus \"pick the mango from the cabinet\", 35 rectified-flow steps, 93 frames at 16 fps.",
            }),
        ],
    },
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
        elif match.group(6) is not None:
            out.append(f"<strong>{inline(match.group(6))}</strong>")
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
        elif all(line.startswith("|") for line in block.splitlines()):
            parts.append(table(block))
        else:
            parts.append(f"<p>{inline(block)}</p>")
    return title, "\n".join(parts)


def table(block: str) -> str:
    """A pipe table: header row, a --- rule (a trailing colon right-aligns the column), then body rows."""
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in block.splitlines()]
    head, rule, body = rows[0], rows[1], rows[2:]
    classes = [' class="num"' if cell.endswith(":") else "" for cell in rule]

    def row(cells: list[str], tag: str) -> str:
        return "<tr>" + "".join(f"<{tag}{classes[i]}>{inline(c)}</{tag}>" for i, c in enumerate(cells)) + "</tr>"

    body_rows = "\n".join(row(r, "td") for r in body)
    return f'<div class="table-wrap"><table>\n<thead>{row(head, "th")}</thead>\n<tbody>\n{body_rows}\n</tbody>\n</table></div>'


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


def page(lang: str, rel: str, title: str, description: str, body: str, root: str, math: bool = False) -> str:
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{LANGS[code]["html_lang"]}" href="{SITE}/{LANGS[code]["prefix"]}{rel}">'
        for code in LANGS
    )
    views_attr = f' data-views-api="{html.escape(VIEWS_API, quote=True)}"' if VIEWS_API else ""
    views_script = f'\n  <script src="{root}views.js" defer></script>' if VIEWS_API else ""
    if math:
        views_script += (
            f'\n  <link rel="stylesheet" href="{KATEX}/katex.min.css">'
            f'\n  <script src="{KATEX}/katex.min.js" defer></script>'
            f'\n  <script src="{KATEX}/contrib/auto-render.min.js" defer'
            f' onload="renderMathInElement(document.querySelector(\'.prose\'))"></script>'
        )
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
    figs = Path(__file__).resolve().parents[1] / "mujoco4" / "images"
    for name in ("mujoco4-beam.png", "mujoco4-plastic.png"):
        src = figs / name
        if not src.exists():
            raise SystemExit(f"missing source media: {src}")
        copy_file(src, WORK / name)
    lewm = Path(__file__).resolve().parents[1] / "le-wm" / "images"
    for name in ("lewm-results.png", "lewm-reacher-floor.png", "lewm-train.png",
                 "lewm-pusht.mp4", "lewm-tworoom.mp4", "lewm-cube.mp4",
                 "frame-lewm-pusht.jpg", "frame-lewm-tworoom.jpg", "frame-lewm-cube.jpg"):
        src = lewm / name
        if not src.exists():
            raise SystemExit(f"missing source media: {src}")
        copy_file(src, WORK / name)
    atlas = Path(__file__).resolve().parents[1] / "atlas-dm05" / "images"
    if not atlas.exists():
        raise SystemExit(f"missing source media: {atlas}")
    for src in sorted(atlas.iterdir()):
        copy_file(src, WORK / f"atlas-{src.name}")
    # These notes write their media under _gen/<slug>/images with the post's prefix already in the names.
    for slug in ("world2act", "splatsim", "masked-visual-actions", "real2sim-eval"):
        images = Path(__file__).resolve().parents[1] / slug / "images"
        if not images.exists():
            raise SystemExit(f"missing source media: {images}")
        for src in sorted(images.iterdir()):
            copy_file(src, WORK / src.name)


def fig_file(name, lang: str) -> str:
    """A figure is one file, or {lang: file} when its labels are in the figure itself."""
    return name[lang] if isinstance(name, dict) else name


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
        for lang in LANGS:
            copy_file(WORK / fig_file(name, lang), folder / fig_file(name, lang))
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
  <img src="{media}/{fig_file(name, lang)}" alt="{html.escape(caption[lang])}">
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
        math = "\\(" in post["prose"] or "\\[" in post["prose"]
        (posts_dir / f"{post['slug']}.html").write_text(
            page(lang, rel, f"{post['title']} · RoboGarden", post["dek"], body, post_root, math),
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
