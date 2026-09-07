# Interaction options

When the client has no A2UI, collect structured choices in chat. Reuse choices the user already gave and ask for missing critical choices once, before any upload.

```text
Project: <number and article>
1. Cover: existing / screenshot+text / redesign
2. Script: article / transcribe video / compare and verify
3. Platforms: frontmatter / select (show account names)
4. Fields: generate / user supplied / edit individually
5. Declaration: original / repost; AI disclosure: yes / no / ask
6. Destination: internal draft by default; platform draft box / both only when explicitly selected
7. Channel: cloud / local
Reply with option numbers or edit this line.
```

Account candidates and dynamic fields must come from the current CLI query. Never make the user infer IDs from raw JSON.
