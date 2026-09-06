# 交互选项 / Interaction options

在没有 A2UI 的客户端中，用聊天文本完成结构化选择。已有明确答案就直接执行对应分支；缺少关键选择时一次列出问题，避免上传后才返工。

## 推荐回显模板

```text
项目：<编号和文章>
1. 封面：现成 / 视频截图加字 / 重新设计
2. 脚本：文章 / 视频转录 / 对照校对
3. 平台：按 frontmatter / 选择（显示账号名）
4. 字段：自动 / 用户提供 / 逐项修改
5. 声明：原创 / 非原创；AI 内容声明：是 / 否 / 询问
6. 目标：内部草稿 / 平台草稿箱 / 两者
7. 通道：云 / 本机
请回复编号或直接改写这一行。
```

## English template

```text
Project: <number and article>
1. Cover: existing / screenshot+text / redesign
2. Script: article / transcribe video / compare and verify
3. Platforms: frontmatter / select (show account names)
4. Fields: generate / user supplied / edit individually
5. Declaration: original / repost; AI disclosure: yes / no / ask
6. Destination: internal draft / platform draft box / both
7. Channel: cloud / local
Reply with option numbers or edit this line.
```

账号、平台候选和动态字段必须来自本次 CLI 查询。不要让用户从原始 JSON 中猜 ID。
