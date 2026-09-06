# Yixiaoer Media Draft Skill

Turn a local video and its Obsidian script into reviewable, multi-platform drafts: locate the project, verify the transcript, create readable vertical and horizontal covers, fill title/short title/description/tags, and save through `yixiaoer-cli`. The workflow stops at a draft and never publishes publicly by default.

![Workflow overview](assets/workflow-overview.png)

## Workflow

Before any upload or write, ask the user to choose (or reuse choices already stated):

1. Cover: existing / screenshot plus text / redesign.
2. Script: Obsidian script / video transcription / compare and verify.
3. Platforms and accounts: article frontmatter / explicit selection from `yxer accounts list`.
4. Fields: generate automatically / user supplied / edit one by one.
5. Declaration: original / repost, plus any platform disclosure.
6. Destination: Yixiaoer internal draft, platform draft box, or both.
7. Channel: cloud or a configured local client.

The skill locates an article and a matching `exp_final` video by stable project number, reuses cached transcription and uploaded resources, checks only ambiguous frames, creates both cover ratios, and runs `verify → validate → dry-run` before a write. Platform drafts use `pubType=0`; public publishing requires a separate explicit authorization.

![Cover layout](assets/cover-layout.png)

## Scripts

```powershell
python scripts/locate_media.py --article "<article.md>" --media-root "<media-root>"
python scripts/make_cover.py --input "<frame.jpg>" `
  --vertical-output "cover-vertical.jpg" --horizontal-output "cover-horizontal.jpg" `
  --title "<large title>" --subtitle "<hook>"
```

The scripts are offline and credential-free. Cover generation uses deterministic text rendering so Chinese remains legible on small thumbnails.

## Safety and privacy

Use real account, schema, category, and tag values returned by the CLI. Never guess dynamic fields. Do not commit account identifiers, client IDs, API keys, videos, private screenshots, or payloads. If cloud preflight reports a missing proxy, explain it and switch to a configured local client only after the user chooses that channel.

The Chinese [README.md](README.md) is the primary landing page. See [SKILL.md](SKILL.md) and [references/](references/) for operational details.

## License

MIT. See [LICENSE](LICENSE).
