# WorkBuddy 与其他 Agent 接入

这是本地文件和 CLI 技能，不依赖某个模型品牌。宿主必须能读取完整技能目录、运行 Python/命令行，并访问用户已配置的 yxer。网页聊天中的“阅读说明”不等于拥有执行能力。

## WorkBuddy（Windows）

WorkBuddy 的个人技能入口是 `~/.workbuddy/skills/yixiaoer-media-draft/SKILL.md`。本机已有技能使用目录联接接入共享库；本技能沿用该方式。

```powershell
# skillSource 应指向已经准备好的完整技能目录。
if (!$env:AGENT_VAULT) { throw 'Set AGENT_VAULT to your existing _Agent directory first' }
$skillSource = Join-Path $env:AGENT_VAULT 'skills/yixiaoer-media-draft'
$skillEntry = Join-Path $env:USERPROFILE '.workbuddy/skills/yixiaoer-media-draft'
# 先检查入口不存在；不要覆盖别人的目录或旧链接。
if (Test-Path -LiteralPath $skillEntry) { throw 'Inspect the existing entry first' }
New-Item -ItemType Junction -Path $skillEntry -Target $skillSource
```

`AGENT_VAULT` 未设置时由用户指定 `_Agent` 目录，不把示例路径当作所有人的目录。Obsidian 内是正文；各宿主里的链接是本机入口，不参与跨设备同步。Git 元数据、凭证、发布 payload、回执和测试视频应留在库外。

在 WorkBuddy 新建会话后输入：

> 使用 yixiaoer-media-draft 技能处理这篇文章。五个平台各保存一份蚁小二内部草稿；按已确认的规则制作横竖封面、填写公开可见性，并在完成后把文章标记为已存草稿。

若宿主没有自动发现技能，显式提供该入口的 `SKILL.md` 绝对路径，让它先读取再执行。不要把宿主是否自动刷新缓存当作 CLI 可用性问题。

## Codex、通用 Agent 和其他工具

- Codex：`~/.codex/skills/yixiaoer-media-draft/`。
- 支持通用 skills 目录的 Agent：`~/.agents/skills/yixiaoer-media-draft/`；具体自动发现能力以宿主为准。
- 其他具备本地文件和终端能力的 Agent：链接到其支持的 skills 目录，或在任务中显式给出本技能路径。不要修改不相关工具的全局配置。
- 官方 yixiaoer CLI skill 也需可读。已有安装时复用其目录链接；没有安装时按官方 yxer 安装帮助取得，禁止复制 API Key 到技能中。

## 相同运行环境下验证

在目标 Agent 使用的 Python 中运行以下命令（`<skill>` 是技能实际路径）：

```powershell
python <skill>/scripts/preflight.py
python <skill>/scripts/locate_media.py --article <article.md> --media-root <media-root>
python <skill>/scripts/make_cover.py --help
```

`preflight.py` 只检查 Python、Pillow、ffprobe 和 `yxer doctor`，仅输出允许的状态字段，不读取或显示凭证值。`path_prepend` 必须在随后上传的命令进程显式加到 PATH；脚本不能修改父 shell 的环境。

Windows 可复用现有 ffprobe，也可传 `--ffprobe-dir <bin目录>`；其他系统优先系统 PATH。缺 Pillow 时在目标 Agent 实际使用的 Python 安装 Pillow，避免装进另一个环境。

验收级别要准确：读取入口、目标宿主 Python 执行、真实 CLI 校验与 dry-run，可以证明这些环节可用；没有在 WorkBuddy UI 中实际启动模型任务时，不声称“已验证所有模型自动发现或完整执行”。
