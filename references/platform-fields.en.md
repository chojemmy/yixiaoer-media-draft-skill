# Platform field notes

Limits can change with the CLI and platform UI. Always read `prepare` and `schema fields` for the current run.

| Platform | Title / description | Short title | Dynamic fields | Original and draft |
| --- | --- | --- | --- | --- |
| WeChat Channels | Title commonly up to 80 characters; description up to 1,000 and may contain topics | `short_title` is separate; the schema limit may differ from the UI, so test with a platform draft | `cover` and `horizontalCover` are separate; query locations, collections, activities, products, and dramas | `createType=1` original, `2` non-original; `pubType=0` draft, `1` direct |
| Xiaohongshu video | Title commonly up to 20 characters; description up to 1,000 | Follow the current schema | Visibility and declaration fields depend on account capabilities | Follow the current schema and dry-run first |
| Bilibili video | Title up to 80 characters; description up to 2,000 | Usually no field with the same meaning as Channels `short_title` | `tags` is required (commonly 1–10); `category` is a queried cascading object | `createType=1` self-made/original, `2` repost; `pubType=0` draft, `1` direct |

Generate one clear conclusion for the title, an explanatory description, and only tags grounded in the script. Dynamic objects must preserve the complete CLI result when the contract requires `raw`; never invent IDs or categories.
