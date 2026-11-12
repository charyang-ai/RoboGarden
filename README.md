# RoboGarden

在 AMD ROCm 上移植并优化前沿机器人 / 世界模型的实验笔记。

覆盖 Radeon RDNA3、RDNA4 与 Ryzen RDNA3.5 等平台；目前的工作多在单张 Radeon Pro W7900 上跑通，再把过程写下来。

站点：[https://worldloop.github.io/](https://worldloop.github.io/)（[English](https://worldloop.github.io/en/)）

## 笔记

| 项目 | 说明 |
| --- | --- |
| [MuJoCo 4](https://worldloop.github.io/posts/mujoco4.html) | 弹性杆的小挠度对上悬臂梁公式，塑性铰停在该停的角度 |
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
