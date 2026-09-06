# yxer-cli 工作流 / yxer-cli workflow

这是可恢复的执行顺序。命令中的路径和 ID 都是占位符，必须由本次查询结果替换。

## 1. 环境和 schema

```powershell
yxer doctor --json
yxer accounts list --json
yxer prepare <platform-key> <video|imageText|article> --json
yxer schema fields <platform-key> <type> --json
```

只读取目标平台需要的 workflow 和 schema。账号候选不唯一时让用户确认。

## 2. 资源和表单

选项确认后上传，视频和封面都使用 `--auto-meta`：

```powershell
yxer upload --file "<video>" --auto-meta --json
yxer upload --file "<vertical-cover>" --auto-meta --platform <platform> --usage cover --json
yxer upload --file "<horizontal-cover>" --auto-meta --platform <platform> --usage cover --json
```

将返回的完整资源对象（key、size、width、height、duration、format）放入表单。重复运行前按本地哈希或已保存的资源记录复用，避免重复上传。

页面式表单推荐：

```powershell
yxer publish form start <platform-key> video --output publish-form.json --json
yxer publish form set publish-form.json <declared.path> --value '<json-value>' --source-command '<real source>' --json
yxer publish form verify publish-form.json --json
yxer publish form export publish-form.json --output payload.json --json
```

`set` 只能写 contract 声明过的路径；动态活动、合集、商品、分区等使用 schema 指定的 `query` 和 `choose` 流程。字段修改后重新 verify/export，不要手改 provenance 记录。

## 3. 校验和草稿

必须用同一 payload 和通道参数：

```powershell
yxer validate <platform-key> video payload.json --publish-channel <cloud|local> [--client-id <local-client>] --json
yxer publish video <platform-key> payload.json --publish-channel <cloud|local> [--client-id <local-client>] --dry-run --json
```

平台草稿：先确认 payload 的平台字段 `pubType=0`，再执行正式命令：

```powershell
yxer publish video <platform-key> payload.json --publish-channel <cloud|local> [--client-id <local-client>] --json
```

蚁小二内部草稿是另一条路径：

```powershell
yxer draft save payload.json --json
```

立即记录返回的 task set ID、内部草稿 ID、`stageStatus` 和平台名。不要把内部草稿成功误报成平台草稿成功。

## 4. 通道和代理

默认云端前先看账号代理预检。缺少代理时说明具体账号和原因；不要自动调用代理配置写接口。用户选择本机且客户端已配置时，显式传 `--publish-channel local --client-id ...`，并重新 validate/dry-run。

## 5. 恢复规则

- 账号或平台变更：重新 accounts/prepare/schema。
- 视频或封面变更：重新上传受影响资源。
- 任意字段变更：重新 validate 和 dry-run。
- validate 失败：只修报错字段；不要重复正式 publish。
- 平台草稿成功：停止，等待用户审核；公开发布另行授权。
