# 蚁小二媒体草稿 Skill

把本地视频和 Obsidian 脚本整理成可审核的多平台草稿：定位项目、校对转录、生成横竖封面、补齐标题/短标题/简介/标签，再通过 `yixiaoer-cli` 保存到蚁小二内部草稿或平台草稿箱。流程默认停在草稿，不会替用户公开发布。

![流程总览](assets/workflow-overview.png)

## 适用场景

- Obsidian 文章和 `D:\自媒体` 项目目录按编号对应，例如 `004`。
- 视频文件通常叫 `exp_final`，文章里有脚本或需要从视频转录。
- 需要同时准备视频号、小红书、B 站等平台的发布字段，并让人最后审核。

## 快速开始

将本目录作为 Codex skill 安装后，直接说明视频编号或文章路径，并给出选择：

```text
使用 $yixiaoer-media-draft 处理 004：
封面从视频截图加字；脚本用文章并和视频对照；平台按文章 frontmatter；
标题、短标题、简介和标签自动生成；按原创发布；保存到平台草稿箱和蚁小二内部草稿。
```

Skill 会先定位文章和素材，展示候选账号及选项；确认后才上传。没有 A2UI 时，选项以聊天中的编号或一行回显完成。

## 选项

1. 封面：现成封面、截图加字、重新设计。
2. 脚本：文章脚本、视频转录、两者对照校对。
3. 平台/账号：文章 frontmatter 或手动选择真实账号。
4. 字段：自动生成、用户提供、逐项修改。
5. 声明：原创、非原创/转载，以及是否需要平台的 AI 内容声明。
6. 草稿目标：蚁小二内部草稿、平台草稿箱、两者。
7. 通道：云端或已配置客户端的本机通道。

![封面布局示例](assets/cover-layout.png)

## 可复用脚本

```powershell
python scripts/locate_media.py --article "<article.md>" --media-root "<media-root>"
python scripts/make_cover.py --input "<frame.jpg>" `
  --vertical-output "cover-vertical.jpg" --horizontal-output "cover-horizontal.jpg" `
  --title "技术替代的临界点" --subtitle "一过，替代突然加速"
```

脚本不联网、不读取凭证。`make_cover.py` 用确定性叠字保证中文可读，并默认生成 1080×1440 竖版和 1920×1080 横版；平台有不同尺寸时可传入尺寸参数。

## 运行边界

- 所有 yxer 真实操作都通过 CLI；先 `doctor`、查询账号和 schema，再上传。
- 平台草稿使用 `pubType=0`，原创声明是独立字段；短标题长度要以实际平台结果验证，不能把猜测当规则。
- B 站标签/分区、小红书可见范围等动态字段必须查询真实候选。
- 云发布缺代理时不静默改账号配置；在用户选择后才切换本机通道。
- 不把账号 ID、客户端标识、API key、视频、私人截图或草稿 payload 提交到公开仓库。
- 公开发布需要用户另行明确授权。

详细流程见 [SKILL.md](SKILL.md) 和 [references/](references/)。
英文参考：[workflow](references/yxer-workflow.en.md)、[platform fields](references/platform-fields.en.md)、[cover style](references/cover-style.en.md)、[interaction options](references/interaction-options.en.md)。

## 安装

把仓库目录放入 Codex skills 目录，或在 Codex 中显式调用 `$yixiaoer-media-draft`。需要 `yixiaoer-cli`、Python 3.10+ 和 Pillow（仅使用封面脚本时）。

## English

See [README.en.md](README.en.md) for the complete English description. The Chinese README is the primary landing page.

## License

MIT. See [LICENSE](LICENSE).
