# yxer CLI 工作流

所有命令以本次安装的 yxer 帮助和 schema 为准。内部草稿与平台发布是两条不同的路径。

## 1. 环境与真实数据

```powershell
python scripts/preflight.py
yxer doctor --json
yxer accounts list --status 1 --json
yxer prepare <platform> video --json
yxer schema fields <platform> video --json
```

`preflight.py` 的 `path_prepend` 应在随后上传命令的同一进程加入 PATH，不修改全局环境。缺 ffprobe 时先定位已有程序或安装，再上传；不要退回不带元数据的重复上传。

账号按本次查询选择；一个平台唯一有效账号可自动选中并说明。用户已指定的平台与历史约定可以沿用，不能因为旧 frontmatter 写“已发布”就覆盖用户的新说明。

## 2. 上传与表单

```powershell
yxer upload --file "<video>" --auto-meta --json
yxer upload --file "<vertical-cover>" --auto-meta --platform 视频号 --usage cover --json
yxer upload --file "<horizontal-cover>" --auto-meta --platform 视频号 --usage cover --json
yxer publish form start <platform> video --output form.json --json
```

视频号封面需使用上述平台和用途参数。每次上传立即把完整返回存到库外工作目录。只复用有真实上传来源且本地文件哈希相同的资源；不从历史示例抄 key。

使用 `publish form set` 填 contract 声明路径，复杂值通过 `--value-file` 传 JSON，中文文件以 UTF-8 保存。资源来自 upload 的 `data` 对象，不能传外层 `{ok,data,...}`。每份表单只对应一个确认的账号。

```powershell
yxer publish form set form.json <declared.path> --value-file value.json --source-command "<actual source>" --json
```

平台约定：视频号/小红书/抖音竖主封面，B站/快手横主封面，视频号/抖音另填 horizontalCover。公开可见性取 schema 的公开枚举。原创、AI声明、内部草稿和平台草稿是不同设置。

## 3. B站分类数组（CLI 3.2.12 实测）

先查询当前账号：

```powershell
yxer query categories <account-id> --type video --json
```

从真实响应的 `data.dataList` 提取候选数组为 `categories.list.json`。用户已确认或按既定约定选中的完整对象组成单元素数组，存为 `category-array.json`；保留 raw，不编造 ID。

```powershell
yxer publish form set form.json 'publishArgs.accountForms[0].contentPublishForm.category' --value-file category-array.json --source-command 'yxer query categories <account-id> --type video --json' --json
yxer publish form choose form.json category --path 'publishArgs.accountForms[0].contentPublishForm.category[0]' --value-file categories.list.json --id <selected-id> --source-command 'yxer query categories <account-id> --type video --json' --json
```

关键是 `choose --path ...category[0]` 记录数组元素来源。先在父路径 choose 单个对象，再 set 父路径数组，会同时留下 object 和 array 的冲突来源，导致 `value_hash_mismatch`。旧会话已冲突时重建本地表单并按上面顺序填写，不手改 session、valueHash 或 rawHash。这个修复不需要重新上传，也不需要新增远端草稿。

B站 tags 是脚本相关字符串数组，不是需查询 ID 的动态对象。

## 4. 内部草稿（默认）

```powershell
yxer publish form verify form.json --json
yxer publish form export form.json --output payload.json --json
yxer validate <platform> video payload.json --json
yxer draft save payload.json --dry-run --json
# 两项通过且当前任务已授权保存后，执行一次：
yxer draft save payload.json --json
```

验证和保存使用同一 payload；通道写在 payload 中。显式 local 时在 validate 保持同一通道，并使用已配置客户端。内部草稿不需要调用 `publish --dry-run` 或 `publish`；其预检是 `draft save --dry-run`，返回 `request.isDraft=true`。视频号/B站保留后续发布用的 pubType=1。

`validate` 在 cloud 下仍可能触发账号代理预检。用户已确认本机通道（含明确沿用的历史选择）时用 local；否则说明缺代理并询问通道，不能擅自改账号代理或自动切换。

## 5. 回执与中断恢复

- 写入前把 payload SHA-256 和账号关联保存在库外。
- `draft save` 成功要求 `ok=true`、`data.statusCode=0`，草稿 ID 通常在 `data.data`。记录原始回执，遇到版本差异先读输出。
- 同一账号、同一 payload 哈希已有成功回执时跳过保存。超时或输出不明时保留现场并核实，不自动重发。
- 修改任意字段后重新 verify/export/validate/dry-run。出现部分成功时只处理未完成账号。
- 文档状态写“已存草稿”，五平台各留 ID；不要写已发布或声称平台后台已存在。
- 验证技能兼容性只做只读检查、表单验证和内部草稿 dry-run，不为测试新增真实草稿。

## 6. 显式平台草稿或公开发布

仅当用户明确选择该目标，才切换到官方对应发布 workflow。使用同一 payload、同一通道执行 validate、publish --dry-run 和已授权的 publish。平台草稿字段以当前 schema 为准，不能把所有平台强行设 pubType=0。配额错误立即停止，不换通道重复消耗推送。
