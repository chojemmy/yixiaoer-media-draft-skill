# yxer-cli workflow

Use this as a recoverable sequence. Replace every placeholder with a value returned by the current CLI run.

## Environment and schema

```powershell
yxer doctor --json
yxer accounts list --json
yxer prepare <platform-key> <video|imageText|article> --json
yxer schema fields <platform-key> <type> --json
```

Read only the workflow and schema needed for the selected platform. Ask the user to choose when account candidates are ambiguous.

## Resources and form

Upload only after the choices are confirmed, using `--auto-meta`. Reuse a resource when its local content hash is already known.

```powershell
yxer upload --file "<video>" --auto-meta --json
yxer upload --file "<vertical-cover>" --auto-meta --platform <platform> --usage cover --json
yxer upload --file "<horizontal-cover>" --auto-meta --platform <platform> --usage cover --json
```

For a page form:

```powershell
yxer publish form start <platform-key> video --output publish-form.json --json
yxer publish form set publish-form.json <declared.path> --value '<json-value>' --source-command '<real source>' --json
yxer publish form verify publish-form.json --json
yxer publish form export publish-form.json --output payload.json --json
```

Only set paths declared by the contract. Use the contract's query/choose flow for dynamic activities, categories, products, and similar fields.

## Validation and drafts

Use the same payload and channel arguments for validation and dry-run:

```powershell
yxer validate <platform-key> video payload.json --publish-channel <cloud|local> [--client-id <local-client>] --json
yxer publish video <platform-key> payload.json --publish-channel <cloud|local> [--client-id <local-client>] --dry-run --json
```

Set the platform field `pubType=0` before saving to a platform draft box. The internal Yixiaoer draft is separate:

```powershell
yxer draft save payload.json --json
```

Record task-set IDs, internal draft IDs, platform names, and stage status immediately. Public publishing requires a separate explicit authorization.

## Channel recovery

If cloud preflight reports a missing account proxy, explain the exact account and do not silently change its configuration. Switch to a configured local client only after the user chooses that channel, then repeat validation and dry-run.

## Speed and proxy

The first transcription/model download is usually the slowest step. Reuse the local model and transcript cache, and use a local file hash to reuse uploaded resources. For Hugging Face or other overseas downloads, set the machine's approved Clash proxy for the current process before starting the download, for example:

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
```

The proxy above is only an example of a local setting; never put credentials or proxy secrets in a payload, vault note, or public repository.
