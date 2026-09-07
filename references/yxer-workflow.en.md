# yxer CLI workflow

Read the installed official yixiaoer skill and use current help/schema. Internal drafts and platform publishing are separate paths.

## Environment and sources

Run `python scripts/preflight.py`, `yxer doctor --json`, `yxer accounts list --status 1 --json`, `yxer prepare <platform> video --json`, and `yxer schema fields <platform> video --json`. Add preflight's `path_prepend` to PATH in the upload process; it cannot change the parent environment. Fix missing ffprobe before uploading.

Reuse confirmed choices. A current user correction overrides stale article metadata. Select accounts from the real query, not old example payloads.

## Upload and forms

```powershell
yxer upload --file "<video>" --auto-meta --json
yxer upload --file "<portrait-cover>" --auto-meta --platform shipinhao --usage cover --json
yxer upload --file "<landscape-cover>" --auto-meta --platform shipinhao --usage cover --json
yxer publish form start <platform> video --output form.json --json
yxer publish form set form.json <declared.path> --value-file value.json --source-command "<actual source>" --json
```

The cover platform/usage flags are required for Channels covers. Store complete upload receipts outside the vault and only reuse assets with a real source and matching local hash. Use the returned resource data object, not the outer response envelope. Use UTF-8 value files for complex values. Prepare one account per form.

Portrait primary covers: Channels, Xiaohongshu, Douyin. Landscape: Bilibili and Kuaishou. Channels and Douyin also receive horizontalCover. Originality, AI disclosures, visibility, and draft destination are distinct settings.

## Bilibili category arrays (verified with CLI 3.2.12)

Query `yxer query categories <account-id> --type video --json`. Extract the actual data.dataList array to categories.list.json. Put the confirmed complete object, including raw, inside a one-element array in category-array.json.

```powershell
yxer publish form set form.json 'publishArgs.accountForms[0].contentPublishForm.category' --value-file category-array.json --source-command 'yxer query categories <account-id> --type video --json' --json
yxer publish form choose form.json category --path 'publishArgs.accountForms[0].contentPublishForm.category[0]' --value-file categories.list.json --id <selected-id> --source-command 'yxer query categories <account-id> --type video --json' --json
```

Choosing at the parent path and then replacing the object with an array leaves conflicting query provenance and causes value_hash_mismatch. Set the array first, then choose its element via --path. Rebuild a polluted local form; never edit source hashes. No re-upload or remote draft save is needed for this correction. Bilibili tags are script-related strings, not dynamic query objects.

## Internal drafts (default)

```powershell
yxer publish form verify form.json --json
yxer publish form export form.json --output payload.json --json
yxer validate <platform> video payload.json --json
yxer draft save payload.json --dry-run --json
# Once both checks pass and the current task authorizes saving:
yxer draft save payload.json --json
```

Use one unchanged payload and consistent channel settings. The internal preflight is draft save --dry-run, with request.isDraft=true; do not call publish or publish --dry-run for this path. Channels/Bilibili retain pubType=1 for later manual publishing. Cloud validation may still check account proxies. Use a configured local channel only when already selected by the user; otherwise clarify rather than silently changing configuration.

## Receipts and recovery

Store payload SHA-256 and the account before writing. Success requires ok=true and data.statusCode=0; the draft ID is normally data.data. Preserve the receipt. Skip identical successful revisions; do not blindly retry after timeouts or ambiguous responses. Revalidate changed fields. Record partial success per platform and mark only drafted status in Obsidian.

Compatibility tests use read-only commands, form verification, validation and internal-draft dry-runs only. They do not create fresh drafts.

## Explicit platform drafts or public publishing

Switch to the official platform workflow only when the user explicitly selects it. Use the same payload/channel for validate, publish --dry-run, and authorized publish. Platform draft fields depend on the current schema; never assume every platform uses pubType=0. Stop after quota errors instead of switching channels and retrying.
