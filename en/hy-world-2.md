# This Time One Card Is Not Enough: HY-World 2.0 Turns a Photo into a 3D World You Can Walk Into, on W7900s

Most world models this year are making movies. Give them an image and a sentence and they generate a video: the camera pushes in, turns around, and it looks as if you stepped into that world. But a movie ends. Want to look back at the door you just passed? The model has to draw it again, and what it draws may not be the same door. Want a character to stop when it hits a wall? There is no wall in a video, only pixels.

Tencent Hunyuan's HY-World 2.0 asks a different question: instead of shooting a movie you can watch, build a house you can enter. Its output is not video but 3D assets, meshes and 3D Gaussians (3DGS), which drop straight into Blender, Unity, Unreal or Isaac Sim, render in real time on a consumer GPU, and stay as long as you like. The technical report came out in April 2026 (arXiv 2604.14268), and the weights and inference code of its parts were open-sourced one after another.

This note covers how HY-World 2.0 turns a photo into a world, and what happened when it moved onto W7900s: reconstruction needs one card and answers in 4 seconds; panorama generation needs 59 GiB, the first world in this series that does not fit on one 48 GB card.

## Movies and houses

The project's README puts the accounting up front. Video world models (Genie 3, Cosmos, and Hunyuan's own HY-World 1.5) output pixels: the playable duration is limited, typically about a minute; change the viewpoint and details flicker and drift; every interaction costs another round of inference, so the cost keeps piling up; character control is imprecise, and there is no real physical collision. A 3D world model turns this around: the assets are generated once, and rendering after that costs almost nothing; 3D consistency is built in, because there is only one copy of the geometry; physical collision and lighting are left to the engine.

The last row of that comparison table says it plainly: watch a video, and it is gone; build a world, and it stays.

Houses have their own difficulties, of course. A video model only needs every frame to look good; a 3D world has to agree with itself from every angle, and the places that were hidden must contain something. A photo captures one side of the world, and the rest is left to the model to guess, consistently. HY-World 2.0 splits the job into a four-stage pipeline, each stage solving one problem.

## Stage one: draw a panorama first

The first step is HY-Pano 2.0: from a photo or a sentence, generate a 360° panorama.

Drawing the panorama first is a clever order. One equirectangular panorama fixes the whole ring around the camera at once: where the sky is, how high the horizon sits, what is behind you. Every later step expands outward from this image, so you never turn around once and come back to find the room rearranged.

HY-Pano 2.0 comes in two versions. The full one is built on HunyuanImage-3.0, with about 80 billion parameters; the open lightweight one is a LoRA on Qwen-Image-Edit-2509, with about 425 million. This run used the latter. "Lightweight" refers to the LoRA: the Qwen-Image-Edit base underneath is 54 GB in bf16 by itself.

## Stage two: decide where to go

A panorama is the world seen from where you stand. To walk in, you need to know where to go and what you will see when you get there. The second step, WorldNav, plans trajectories: a vision-language model guides the direction, and Recast navigation meshes keep the camera clear of obstacles. It handles a very practical question: where should the camera move to see what the original image hid, without running straight into a wall?

## Stage three: fill in the world along the route

The third step, WorldStereo 2.0 (about 17 billion parameters), generates keyframes along the planned trajectories: as the camera moves forward, what was hidden has to be filled in, and what has already appeared has to stay as it was. It carries a memory mechanism that refers back to existing content when generating new views, so that when you walk far and turn back, you still see the same world.

The report's numbers show where this step improved. On camera control, WorldStereo 2.0 has a rotation error of 0.492, against 0.762 for the previous WorldStereo, 1.690 for SEVA and 0.944 for Gen3C. More important is whether the generated video can be reconstructed into good 3D: from a single image, generate video, then reconstruct. The F1 on Tanks-and-Temples is 41.43, while SEVA, Gen3C and Lyra sit between 31 and 37 and FlashWorld at 22.29; on MipNeRF360 it is 51.27, with FlashWorld second at 42.60. For a 3D world model that is the real exam: looking good is not enough, the frames have to assemble into a self-consistent 3D world.

## Stage four: assemble everything into 3D

The last step assembles the panorama and the generated keyframes into a real 3D world: WorldMirror 2.0 first recovers depth, normals and camera poses from these images, then 3D Gaussians are trained and exported as assets an engine can render in real time.

WorldMirror 2.0 deserves its own section, because it is also HY-World 2.0's second core capability: world reconstruction. Give it a few photos or a casually shot video, and one forward pass predicts depth maps, surface normals, camera parameters, a 3D point cloud and 3DGS attributes at once, with no per-scene optimization. It has about 1.2 billion parameters and supports flexible resolutions from 50 thousand to 500 thousand pixels.

The most interesting part of the report is two sets of numbers. One is priors: if you have priors such as camera intrinsics and extrinsics or depth, you can inject them. On 7-Scenes at medium resolution the accuracy error drops from 0.033 to 0.013, about 60% lower. The other is resolution: the previous WorldMirror 1.0 got worse at high resolution, with the 7-Scenes error rising from 0.043 at medium resolution to 0.079, and DTU's from 1.017 to 2.271. Version 2.0 no longer collapses: at high resolution 7-Scenes is 0.037, close to the 0.033 at medium, and DTU actually drops from 1.005 to 0.845.

"Give it more pixels and the result gets worse" is an old ailment of many feed-forward reconstruction models: training sees a limited range of resolutions, and scaling up at inference falls out of distribution. Version 2.0 has largely cured it, which says more than any leaderboard number about whether it can be used on real photos.

## A community developer had already walked half the way

HY-World 2.0's officially recommended environment is CUDA 12.8, and FlashAttention 3 wants Hopper. The first person to try it on AMD cards was the community developer Vladimir Talyzin. His hy-world-2.0-mac-rocm moved the whole thing onto ROCm and Apple's Metal, with a Radeon 8060S as the reference machine: the integrated GPU of the Ryzen AI Max+ 395 "Strix Halo", under Windows 11, a part AMD does not even list as supported.

His porting notes are a pleasure to read. FlashAttention is a hard import in the code, so without it everything crashes; on ROCm, SDPA silently falls back to the slowest math backend; gsplat is a CUDA extension with no ROCm version, and he built it himself. The best part is the panorama: Qwen's VAE is a video VAE built on 3D causal convolutions, and MIOpen falls off a performance cliff on some Conv3d shapes, with one convolution layer taking minutes. He folded the Conv3d on single-frame images into Conv2d and tiled the decode to get around it. There is also a pitfall only Strix Halo owners will recognize: the 128 GB of memory is split in the BIOS between VRAM and system memory, and the default split puts the 54 GB base into the page file, so every step looks like a hang. In the end, on the 8060S, a 1952×960 panorama at 40 steps takes about 25 minutes, about 38 seconds per step.

This work stands on his shoulders: the same code, moved from one integrated GPU onto several discrete W7900Ds.

## On the W7900, reconstruction needs one card

This run used W7900Ds (gfx1100, 48 GB) with a ROCm 7.2.4 runtime. The first pitfall had nothing to do with the GPU: the port's own install script installs pytorch.org's ROCm 6.4 wheels for gfx1100, and they segfault on a 7.x runtime; switching to the official ROCm 7.2 index fixed it. The second was in the dependencies: the requirements allow diffusers 0.36 or newer, pip installed 0.39, and 0.39 happened to remove the `txt_seq_lens` argument from the Qwen image transformer's forward, so the panorama failed on its first denoising step. Pinning 0.36.0 fixed that. The foundation of a software stack is often hollowed out by little version numbers like these.

Reconstruction went smoothly. The self-check script reports gfx1100, bf16 and AOTriton SDPA all working. WorldMirror 2.0 on the bundled Desk scene, two photos: the model loads in 11.3 seconds, inference takes 4.05 seconds, and 334,365 Gaussians remain after voxel pruning.

Then multiple cards. WorldMirror supports sequence parallelism with `torchrun`, splitting the input views over several cards. On the Park_Stone scene with 32 photos, one card infers in 8.44 seconds, two in 10.26, four in 11.19: the more cards, the slower. The reason is simple: every card holds a full copy of the 1.2-billion-parameter model, so memory barely drops, and the views have to exchange features over PCIe, so the communication bill outweighs what the split saves. For reconstruction, stick with one card.

## The panorama: a world that does not fit on one card

The panorama is a first for this series: it does not fit on one 48 GB card. With the LoRA, one copy of the transformer is 38.8 GiB, and its card peaks at 40.1 GiB at 1952×960; the text encoder and VAE need another 18.7 GiB. About 59 GiB in all. On Strix Halo that is not a problem, because VRAM and RAM are one family there and the 128 GB of unified memory is shared; a discrete card has to choose: either offload the model to CPU memory and shuttle it back and forth, or use more cards.

This run chose more cards, adding a `gpus` parameter to the panogen pipeline. With two cards, the text encoder and VAE go on card 0, and the transformer is cut at block boundaries onto card 1, with accelerate hooks moving activations between the cards. Diffusers has one small quirk here: the split has to happen after the LoRA is loaded, because when diffusers loads a LoRA and finds accelerate hooks, it assumes you have enabled CPU offload and helpfully turns offload back on. With two cards, a step takes 13.15 seconds, and one image takes 526 seconds.

The third card is more interesting. The panorama uses true CFG: every denoising step runs the model twice, once with the prompt and once without, then mixes the two by the guidance strength. The two passes do not depend on each other and could always have run at the same time. So the third card holds a copy of the transformer, a worker thread runs the pass without the prompt on the copy, and the main copy runs the pass with the prompt at the same time. A step drops from 13.15 seconds to 6.86, almost exactly half. The two-card and four-card outputs are byte-identical, with the same SHA-256: the parallelism changed the time, not the result. The fourth card went unused; in this layout it has nothing more to do.

Against the 8060S's 38 seconds per step, three W7900s take 6.86. That is not a knock on the integrated GPU: it ran a 59 GiB model on one chip and one pool of unified memory. The advantage of discrete cards is that they can sit side by side, and two independent computations of the same model map neatly onto two cards.

## Blue dots in the sky

Once multi-GPU worked, a problem showed up that small images had hidden. With the port's default tiled decode, the flat blue sky of the generated panorama carried rows of small, very regular blue dots, as if someone had dabbed ink on a grid across the sky. Turning tiling off made the dots disappear.

Tiled decoding is the port's default on ROCm, and on Strix Halo it has good reason: unified memory is tight, and tiling keeps the decode's peak down. On discrete cards, the VAE already has a card to itself, and the untiled decode peaks at 24.9 GiB, which fits. So in multi-GPU mode, tiling now defaults to off.

This little episode says a lot about porting: a default that is right on the original platform is not necessarily right on different hardware. A default carries the machine it was born on.

## What this run verified

What was verified: WorldMirror 2.0's world reconstruction runs on one W7900, with 4 seconds of inference; HY-Pano 2.0's lightweight panorama model runs on two to three W7900s, three cards at 6.86 seconds per step, with byte-identical results before and after the parallelism. What was not verified is stated just as clearly: gsplat was not built, so the fly-through video after reconstruction was not rendered; WorldStereo 2.0's world expansion and the full four-stage generation pipeline were not run; the 80-billion-parameter HunyuanImage-3.0 panorama backend was not run either.

Then the license. HY-World 2.0 uses Tencent's own community license, whose territory clause excludes the EU, the UK and South Korea, and which forbids using its outputs to improve other AI models. The repository keeps Tencent's license, the Notice file and Vladimir's MIT license, and the two modified files carry change notices at the top. This port is not affiliated with Tencent or with Vladimir.

This series is called "one card, one world", and this time it broke the rule: reconstruction on one card, the panorama on three. That is a finding of its own: the more a world model resembles the real world, the less willing it is to squeeze onto one card.

The code is at <https://github.com/charyang-ai/hy-world-2.0-mac-rocm>.
