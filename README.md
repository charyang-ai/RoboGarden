# RoboGarden

在 AMD ROCm 上移植并优化前沿机器人 / 世界模型的实验笔记。

覆盖 Radeon RDNA3、RDNA4 与 Ryzen RDNA3.5 等平台；目前的工作多在单张 Radeon Pro W7900 上跑通，再把过程写下来。

站点：[https://worldloop.github.io/](https://worldloop.github.io/)（[English](https://worldloop.github.io/en/)）

## 笔记

| 项目 | 说明 |
| --- | --- |
| [HY-World 2.0](https://worldloop.github.io/posts/hy-world-2.html) | 不拍电影直接盖房子的 3D 世界模型：重建一张 W7900 4 秒出结果，全景图要 59 GiB，三张卡跑 CFG 并行每步 6.86 秒 |
| [Real2Sim-Eval](https://worldloop.github.io/posts/real2sim-eval.html) | 高斯外观加弹簧质点的绳子替真机给策略打分：官方 27 组评测 18 组成功，失败集中在网格一侧，68 次重跑结局不变 |
| [World Labs Atlas × DM0.5](https://worldloop.github.io/posts/atlas-dm05.html) | 把真实厨房的 3D 高斯重新打光来训练 DM0.5：17 个点的提升在 R9700 与 W7900D 上都复现，同一个种子换台机器五分之一会换结局 |
| [LeWorldModel](https://worldloop.github.io/posts/le-wm.html) | 一帧压成 192 维向量的 JEPA 世界模型：发布权重在四个环境重评，Two-Room 从头训练 |
| [MuJoCo 4](https://worldloop.github.io/posts/mujoco4.html) | 弹性杆的小挠度对上悬臂梁公式，塑性铰停在该停的角度 |
| [Masked Visual Actions](https://worldloop.github.io/posts/masked-visual-actions.html) | 把动作画成视频里露出的像素：同一个 14B 视频模型既当正向模型也当逆向模型，W7900 上补了两处注意力 |
| [SplatSim](https://worldloop.github.io/posts/splatsim.html) | PyBullet 管物理，两百万个高斯管画面：W7900 重画作者的训练视角最多差一个灰度级，420 条轨迹全部重拍 |
| [World2Act](https://worldloop.github.io/posts/world2act.html) | 从视频世界模型的潜空间里读动作：2B 老师在 W7900 上走完 35 步校正流，卷积展开表得先腾地方 |
| [RoboRender](https://worldloop.github.io/posts/roborender.html) | 用视频模型把仿真轨迹画成可学的真实外观 |
| [WorldScore](https://worldloop.github.io/posts/worldscore.html) | 世界生成基准：相机、物体与三维一致性拆开打分 |
| [Interactive World Simulator](https://worldloop.github.io/posts/interactive-world-sim.html) | 像素里按动作往下演，不靠物理引擎当裁判 |
| [PointWorld](https://worldloop.github.io/posts/pointworld.html) | 状态与动作同为点流，预言下一秒每个点怎么走 |
| [Ctrl-World](https://worldloop.github.io/posts/ctrl-world.html) | 策略在想象里滚完操作，先在 GPU 上排好坏 |

对应代码仓库仍放在 [`charyang-ai`](https://github.com/charyang-ai) 下。

## 仓库结构

- 根目录与 `en/`：中英文 Markdown 原文
- `RoboGardenSite/`：站点构建产物（GitHub Pages 发布目录）
- `_gen/site/build_site.py`：从 Markdown 生成静态站

```bash
python _gen/site/build_site.py
```

作者：[Charles Yang](https://github.com/charyang-ai)
