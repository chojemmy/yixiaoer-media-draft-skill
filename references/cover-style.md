# 封面规范与提示词 / Cover style and prompts

## 适合解释图的提示词（中文）

> 米白色纸张与淡淡工程网格背景，低饱和灰蓝、墨蓝和暖黄色配色，手绘水彩与钢笔线稿质感，信息图式分栏和清晰箭头，留白充足，中文标题区域预留空白，简洁、可信、适合知识类科技内容；不要生成难以辨认的小字、logo、二维码或水印。

## English prompt

> A knowledge-focused technology infographic on warm off-white paper with a subtle engineering grid, muted blue-gray, navy and warm yellow palette, hand-drawn watercolor and ink linework, clear columns and arrows, generous whitespace reserved for Chinese typography, calm and trustworthy editorial style; no tiny illegible text, logos, QR codes, or watermarks.

## 视频封面规则

参考图的核心是“真实画面 + 大字”，不是复杂海报：

- 选一帧能看清人物或关键动作的截图，主体不要被文字遮住。
- 竖版默认 1080×1440，适合信息流缩略图；横版默认 1920×1080。按平台 schema 覆盖默认值。
- 主标题一到两行，白色或黄色填充，黑色粗描边和阴影；移动端缩小后仍能读清。
- 一张图只保留一个结论和一个钩子，署名放在安全边距内。
- 视频号常见封面大小上限为 512 KB；运行脚本后检查文件大小并在上传返回值中记录实际尺寸。

`scripts/make_cover.py` 采用 Pillow 确定性叠字。图像模型可用于探索构图，但不要让模型负责最终中文标题。

## 视频封面提示词（需要探索构图时）

中文：

> 竖版短视频信息流封面，使用真实人物近景或关键动作截图作为主体，背景轻微压暗，底部留出深蓝色信息区；只突出一个结论，配两行超大中文标题，白色主字、暖黄色强调字、粗黑描边和阴影，安全边距充足，手机缩略图也清晰，简洁有冲击力；不要小字、复杂装饰、logo、水印或虚构人物。

English:

> Vertical short-video feed thumbnail built from a real close-up or key action frame, slightly darkened background, deep navy information band at the bottom; one clear takeaway, two lines of oversized Chinese typography, white primary type with warm yellow emphasis, thick black outline and shadow, generous safe margins, readable as a small mobile thumbnail; no tiny text, clutter, logos, watermarks, or invented people.
