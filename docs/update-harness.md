# Update Harness

`kansei update-harness` is a safe template update flow, not a directory sync.

- Dry-run is the default.
- Managed files are updated only when unchanged from the recorded lock checksum.
- User-owned files such as `projects.toml`, `providers.toml`, `knowledge/`, and
  `dashboards/today.md` are not overwritten.
- If a managed file was edited by the user, the new template content is written
  beside it as `<name>.new`.
