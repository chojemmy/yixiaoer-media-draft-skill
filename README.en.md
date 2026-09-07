# Yixiaoer Media Draft Skill

Prepare local videos and Obsidian scripts for review: locate media, create vertical and horizontal covers, fill platform fields, and save **Yixiaoer internal drafts**. The user reviews and publishes manually.

## v0.2.0: WorkBuddy support

Works with WorkBuddy, Codex, and other agents that can read local files and run commands. The skill uses standard SKILL.md, Python, and yxer CLI; it does not require Codex-specific tools. Browser-only chat models cannot execute this workflow independently.

Validated on Windows using WorkBuddy's bundled Python: dependency checks, a real final.mp4 lookup, Chinese cover generation, and validation/internal-draft dry-runs for existing payloads across five platforms. Compatibility tests create no new drafts and publish nothing. WorkBuddy UI auto-discovery and every third-party model's end-to-end behavior have not been tested; start a new task or provide the absolute SKILL.md path when needed.

This version fixes final-file discovery, hardcoded cover text, subtitle bleed-through, Windows UTF-8 output, and Bilibili category-array provenance conflicts.

![Workflow](assets/workflow-overview.png)

## Installation

Requires yxer CLI and its official skill, Python 3.10+, Pillow, and ffprobe. Configure yxer locally, then run `python scripts/preflight.py` in the target agent's Python environment. Credentials stay in the CLI's local configuration, never in skill files.

| Host | Skill location |
| --- | --- |
| WorkBuddy | `~/.workbuddy/skills/yixiaoer-media-draft/` |
| Codex | `~/.codex/skills/yixiaoer-media-draft/` |
| Agents supporting a shared skills directory | `~/.agents/skills/yixiaoer-media-draft/` |
| Other local agents | Their supported directory, or explicitly read the absolute SKILL.md path |

For an Obsidian-based source of truth, keep the complete skill in `_Agent/skills/yixiaoer-media-draft/` and link host entries to it (Windows Junction or the equivalent on other systems). Recreate links per device. Keep Git metadata, credentials, videos, payloads, and receipts outside the vault. See [agent setup](references/agent-setup.md).

## Example request

```text
Use yixiaoer-media-draft for this article. Reuse its script, create screenshot-and-text
covers, and prepare one internal draft per account for WeChat Channels, Xiaohongshu,
Douyin, Kuaishou, and Bilibili. Generate the copy; original content, public visibility.
Save only to Yixiaoer internal drafts and mark the article as drafted. I will publish.
```

Codex also accepts `$yixiaoer-media-draft`. Reuse established preferences rather than asking again. The user's current correction takes precedence over stale article metadata.

## Workflow

- Prefer embedded video names, then final/exp_final candidates within the exact project number. Never guess among multiple candidates.
- Reuse existing scripts. Transcribe only when needed; never claim transcription or verification that did not happen.
- Query real accounts and current schemas. Upload one video and two independently verified covers.
- Portrait primary covers: Channels, Xiaohongshu, Douyin. Landscape: Bilibili and Kuaishou. Channels and Douyin also receive a landscape cover.
- Use `visibleType=0` for public visibility where exposed; query Bilibili categories and preserve the complete object array. Tags are script-related strings.
- Per account: `verify → export → validate → draft save --dry-run → draft save`. Save the receipt immediately and skip an already successful identical revision on reruns.
- Record drafted status, shared copy/covers once, platform differences in a table, and draft IDs in a collapsible archive. Mark published only after actual publication is confirmed.

Internal drafts are separate from platform drafts. Keep `pubType=1` where appropriate for later user publishing; `draft save` adds `isDraft=true`. Platform drafts require explicit selection and platform-specific fields. Never use repeated live pushes as a test.

![Cover layout](assets/cover-layout.png)

## Scripts and tests

```powershell
python scripts/preflight.py
python scripts/locate_media.py --article "<article.md>" --media-root "<media-root>"
python scripts/make_cover.py --input "<frame.jpg>" `
  --vertical-output "vertical.jpg" --horizontal-output "horizontal.jpg" `
  --title "<title>" --subtitle "<hook>" --eyebrow "<topic>"
python -m unittest discover -s tests -v
```

The locator and cover renderer are offline. Preflight uses read-only `yxer doctor` and outputs allowlisted status fields. Add its `path_prepend` to PATH in the later upload process; the helper cannot change its parent shell. Use `--vertical-crop-bottom` only after inspecting the source subtitle region. Review both covers before upload.

Detailed [workflow](references/yxer-workflow.en.md) and [platform notes](references/platform-fields.en.md). The Chinese [README.md](README.md) is the main page. MIT: [LICENSE](LICENSE).
