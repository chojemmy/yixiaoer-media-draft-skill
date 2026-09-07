---
name: yixiaoer-media-draft
description: 根据 Obsidian 文章和本地视频，制作横竖封面、补齐平台字段并通过 yixiaoer-cli 保存多平台草稿。适用于 WorkBuddy、Codex 和支持本地 SKILL.md 与命令行的 Agent。
---

# 蚁小二媒体草稿

把“视频文件 + 对应脚本”变成用户可以逐项审核的媒体草稿。默认只保存到蚁小二内部草稿箱，用户在审核后自行点击发布；除非用户明确选择平台草稿或正式发布，不调用 `yxer publish`。

## 跨 Agent 入口

先读安装的官方 `yixiaoer/SKILL.md` 及其草稿 workflow；本技能是媒体准备编排层，不替代官方 CLI 的 schema。先运行 `python scripts/preflight.py` 检查当前 Agent 的 Python、Pillow、yxer 和 ffprobe。不同 Agent 的 PATH 可能不同；检查输出的 `path_prepend` 只是一条建议，上传时需显式加入同一命令进程的 PATH。缺少依赖时只补缺失项，不重复上传来试环境。

WorkBuddy 安装与其他 Agent 的接入见 [references/agent-setup.md](references/agent-setup.md)。技能和脚本路径相对于本 SKILL.md 所在目录解析，不依赖用户当前工作目录，也不依赖 Codex 专用工具。只有网页聊天、没有本地文件与命令执行能力的模型不能独立运行此流程。

## 默认目标与平台映射

- **草稿目标默认为蚁小二内部草稿**：执行 `yxer draft save`（先 `--dry-run`），不把“内部草稿”误写成抖音、B 站等平台草稿，也不消耗平台推送次数。只有用户明确说“推送到平台草稿箱”时，才切换到平台草稿流程。
- **公开可见性**：内部草稿不是已发布内容；它保存的是用户稍后点击发布时要采用的设置。对暴露 `visibleType` 的平台，默认写 `visibleType=0`（公开）。B 站当前 schema 没有 `visibleType`，不要自行添加；保留 `pubType=1`，让用户审核后点击即可正式发布。
- **封面方向**：小红书视频使用竖版；抖音使用竖版 `cover`，并在 schema 暴露时同时填写横版 `horizontalCover`；B 站和快手使用横版。每次从 payload 中核对宽高，不能只看文件名。
- **已发布平台**：以用户本次说明为准；文章旧属性不能覆盖用户纠正。用户明确说某个平台已经发布时才按其范围跳过。“五个平台”在本流程中指视频号、小红书、抖音、快手、B站，每账号独立一份草稿和回执。
- **旧版本**：CLI 当前只有保存，没有可靠的内部草稿更新/删除命令。修订时保存一份新版本，并在文章中标记旧版本已被替代，避免把重复版本当成新发布。
- **配额错误**：正式发布或平台草稿返回“今日发布次数已达上限”（通常 code `1001`）时立即停止重试；复用已验证的 payload 执行内部草稿保存，并把失败阶段写入结果。

## 开始前先让用户选项落地

没有 A2UI 时用普通聊天；用户已要求“按之前规则”或给出选择时，沿用可查到的约定并回显，不重复索要授权。仅对缺少且影响结果的选项提问。上传、保存前要能确定以下项目：

1. **封面**：`使用现成封面` / `从视频截图加字` / `重新设计`。自动制作时同时生成平台需要的竖版和横版；用户提供的参考图只作为风格参考，不要把含个人信息的参考图放进公开仓库。
2. **脚本**：`使用 Obsidian 现有脚本` / `从视频转录` / `两者对照并校对`。默认优先已有脚本，只有缺失或用户要求时才转录。
3. **平台和账号**：`按文章 frontmatter` / `选择平台`。展示从 `yxer accounts list --json` 得到的真实账号名称和稳定 ID，让用户确认；不要凭记忆填账号。
4. **字段**：`自动生成标题、短标题、简介、话题/标签` / `用户提供` / `逐项修改`。
5. **声明**：`原创` / `非原创或转载`，另行询问是否需要 AI 生成内容等平台声明。原创映射到各平台真实字段，不要自造 `isOriginal`。
6. **草稿目标**：默认 `蚁小二内部草稿`；只有用户明确要求时才选 `平台草稿箱`，或两者。两者不是同一个状态。
7. **通道**：`云发布` / `本机发布`。云端预检发现账号没有代理时，不要擅自改账号代理；在用户同意后改用已配置的本机客户端。

可直接把选择回显为一行确认，例如：

> 封面=截图加字；脚本=文章与视频对照；平台=视频号；字段=自动后我审核；声明=原创；目标=蚁小二内部草稿；通道=本机。

## 执行顺序

### 1. 定位文章、项目目录和视频

- 从文章名或用户给出的编号提取稳定项目编号（例如 `004`）。Obsidian 文章通常在 vault 的输出目录，素材目录通常在 `D:\自媒体` 或用户配置的媒体根目录；Folder Bridge 只改变可见方式，不改变文件匹配规则。
- 优先运行只读脚本：

  ```powershell
  python scripts/locate_media.py --article "<article.md>" --media-root "<media-root>"
  ```

- 目录名和文章名可能日期不同，先按稳定编号定位；优先文章嵌入的视频文件，再匹配 `final` / `exp_final`。编号 `002` 不匹配 `0020`。候选不唯一时列出候选并让用户选，空结果不能当作成功。
- 用 `ffprobe` 或等价工具一次读取视频时长、分辨率、格式和大小；不要为读元数据重新编码视频。

### 2. 取得并校对脚本

- 读取文章中已有脚本；若需要转录，复用本机模型缓存和已有转录文件。不要每次重新下载模型。
- 只对低置信度片段、专有名词、数字和屏幕文字抽帧验证。先粗采样定位时间，再抽取局部帧；不要默认逐帧 OCR 全片。
- 将校对后的脚本和“画面校对记录”写回文章。语音、字幕、画面文字冲突时保留证据和时间戳，并向用户标出仍不确定的词。

### 3. 生成可读封面

选择“截图加字”时调用 `scripts/make_cover.py`：

```powershell
python scripts/make_cover.py `
  --input "<verified-frame.jpg>" `
  --vertical-output "<project>_封面竖版.jpg" `
  --horizontal-output "<project>_封面横版.jpg" `
  --title "<大标题>" --subtitle "<一句钩子>" --eyebrow "<本期主题>" --brand "<署名>"
```

- 默认竖版为 1080×1440（可按平台改为 1080×1920），横版为 1920×1080；脚本会压缩到平台限制以内。
- 按平台核对方向：小红书=竖版；抖音=`cover`=竖版、`horizontalCover`=横版；B 站=横版；快手=横版。若平台 schema 有不同要求，以本次 `prepare/schema fields` 为准。
- 延续参考风格的关键视觉规则：保留真实人物/场景截图；米白、深蓝、灰绿等低饱和底色；白字和黄字；粗黑描边、强对比、少量文字；移动端缩小后仍能读清。中文标题用确定性的字体叠字，不依赖图像模型正确生成汉字。
- 先在本地查看两张图，再上传。若平台分别有 `cover` 和 `horizontalCover`，分别填写对应资源对象和 key。
- 原截图底部已有字幕时，可用 `--vertical-crop-bottom <像素数>` 在竖版裁剪前排除字幕；检查人物脸部和文字安全边距。信息区使用不透明底色，避免原字幕透出。眉题由 `--eyebrow` 指定，不能残留上期主题。

### 4. 准备内容字段

按所选平台读取 [references/platform-fields.md](references/platform-fields.md)，只使用当前 `yxer prepare`/`schema fields` 暴露的字段。

- 标题围绕视频的一个明确结论；简介包含背景、要点和行动句；话题/标签来自脚本，不堆无关热词。
- 短标题单独生成并计算字符数。CLI schema 的上限不一定等于平台界面限制，先用短而清晰的候选（通常不超过 16 个汉字），在平台草稿结果中记录是否接受；不要把“16 字”写成未经验证的硬规则。
- `原创`、`非原创`、AI 声明和 `pubType` 是不同字段。只有明确选择平台草稿时才使用 `pubType=0`；内部草稿保留平台后续发布所需的业务值（B 站通常为 `pubType=1`）。
- B站 `tags` 是脚本相关的字符串数组；分区 `category` 是必须实时查询的对象数组。CLI 3.2.12 下，先 `choose category` 写父路径再 `set` 成数组，会留下不一致的 query 来源。正确顺序是：用查询中的完整对象数组 `set category`，随后 `choose category --path publishArgs.accountForms[0].contentPublishForm.category[0]` 记录元素来源。详细命令见 [references/yxer-workflow.md](references/yxer-workflow.md)。不手改来源哈希；已污染的本地表单重建后验证，不重复保存远端草稿。
- 抖音和快手要公开时，对应字段必须是 `visibleType=0`；不要因为“草稿”而套用私密值 `1`。小红书等平台的可见范围、声明字段同理。

### 5. 用 yxer 生成草稿

按 [references/yxer-workflow.md](references/yxer-workflow.md) 执行，核心门槛如下：

1. `yxer doctor --json`、`accounts list --json`、目标平台 `prepare` 和 `schema fields`。
2. 选项确认后才上传；按文件内容哈希复用已登记资源，避免重复上传大视频。
3. 用 `publish form set/choose` 维护表单，`verify` 后 `export` payload。
4. 内部草稿：用同一份 payload 执行 `validate`，再执行 `yxer draft save <payload> --dry-run`；两项通过后执行一次 `yxer draft save <payload>`。这条路径不调用平台发布接口。
5. 只有用户明确选择平台草稿箱时，才用同一份 payload 和同一套通道参数执行 `validate → publish --dry-run → publish`，并确保平台字段为 `pubType=0` 或当前 schema 的草稿兼容值。
6. 正式公开发布必须另一次明确授权。任意正式发布返回配额错误时停止重试，转入内部草稿保存并报告原始错误。

云端预检失败通常是账号代理未配置。记录失败原因后，在用户选择本机通道且本机客户端已配置时继续；不要在流程中静默修改账号代理。境外下载（例如模型）遵循本机 Clash 代理设置。

### 6. 回写 Obsidian

保留项目编号、创建日期和原脚本，按授权更新 `status` 和 `platform`。内部草稿成功只写“已存草稿”，实际发布经确认后才写“已发布”；部分成功按平台分别记录。视频、竖封面、横封面各展示一次，通用标题/简介集中存放，表格仅列账号和平台差异，草稿 ID 放折叠存档。仅沿用旧脚本时说明来源，不能声称已重新转录或逐字校对。不要把 API key、客户端标识、密码或私有 payload 放进 vault 或公开仓库。不要修改未授权的 `type: guide` 文档。

## 提速和停止点

- 先读缓存和元数据，再做昂贵操作；首次模型下载和转录是主要耗时，后续运行应复用。
- 抽帧采用“粗采样→低置信度局部复核”，不做全片高密度 OCR。
- 视频只上传一次；封面两张分别上传一次；字段修改后只做一轮 verify、validate 和对应目标的 dry-run。
- 内部草稿保存成功后立即停止并让用户审核。平台发布失败只修具体字段或转内部草稿，不无差别重试正式写操作。
- 重跑前检查本机成功回执及对应 payload 哈希。同一版本已有成功草稿 ID 时跳过保存；超时、回执不明时先核实，不把不确定当作失败自动重试。校验技能时只重放 verify/validate/内部草稿 dry-run，不为测试新建真实草稿。

更多细节：

- 交互选项：[references/interaction-options.md](references/interaction-options.md)
- yxer 顺序和错误恢复：[references/yxer-workflow.md](references/yxer-workflow.md)
- 平台字段：[references/platform-fields.md](references/platform-fields.md)
- 封面规范与提示词：[references/cover-style.md](references/cover-style.md)
