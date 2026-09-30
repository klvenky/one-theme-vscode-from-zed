# VS Code Theme Extension Handoff

## Goal

Create a VS Code color-theme extension with an original palette inspired by the restraint and clarity of Zed's One themes. Do not reproduce Zed's palette exactly.

Project directory: `~/play-school/one-zed-theme`

## Agreed Choices

- Extension display name: `One Light Theme - Zed Inspired`
- Theme picker labels:
  - `One Light (Zed Inspired)`
  - `One Dark (Zed Inspired)`
- Ship both light and dark variants.
- Use an original Zed-inspired palette.
- Initialize a Git repository.
- No extension ID or publisher was chosen. Do not invent either without asking.

## Current State

The project directory was created and was empty at the last check.

The official Generator Code command was started from the project directory:

```sh
npx --package yo --package generator-code -- yo code . --skipOpen --extensionType colortheme --extensionDisplayName "One Light Theme - Zed Inspired" --gitInit
```

The user approved the temporary installation of:

- `yo@7.0.1`
- `generator-code@1.12.0`

The generator is still running in a terminal and is paused at this prompt:

```text
Do you want to import or convert an existing TextMate color theme?
> No, start fresh
  Yes, import an existing theme but keep it as tmTheme file.
  Yes, import an existing theme and inline it in the Visual Studio Code color theme file.
```

Select `No, start fresh` and continue through one prompt at a time. For the initial generated theme, choose a light base when asked. The dark companion can be added after the scaffold is valid.

The install also printed this warning:

```text
which@7.0.0 requires Node ^22.22.2 || ^24.15.0 || >=26.0.0
current Node is v22.22.0, npm 10.9.4
```

This was an `EBADENGINE` warning, not a failure. If generation fails, update Node to at least `22.22.2` before retrying.

## Work Already Done

- Loaded the `project-setup-info-local` skill.
- Queried the VS Code API reference for color themes, `contributes.themes`, light/dark `uiTheme` values, semantic tokens, local testing, and packaging.
- Created the target directory.
- Started the official scaffold command.
- Confirmed the directory was still empty while the generator awaited its theme-source selection.

## Next Steps

1. Resume the active generator and choose `No, start fresh`.
2. Complete the generator prompts with a light base theme.
3. Immediately validate that `package.json` and the generated theme JSON parse and that the contributed path exists.
4. Inspect the generated manifest and theme file before editing.
5. Update `contributes.themes` to register both picker labels. Use `vs` for the light theme and `vs-dark` for the dark theme.
6. Create original light and dark theme JSON files with editor/workbench colors, terminal ANSI colors, TextMate token colors, semantic highlighting, and semantic token colors.
7. Keep contrast suitable for prolonged coding and make comments readable without giving them the same prominence as executable code.
8. Update the README with installation and local preview instructions.
9. Validate both JSON files, check VS Code diagnostics, and package a VSIX with `@vscode/vsce` if the manifest is ready.
10. Review `git status`; do not commit unless the user asks.

## Suggested Skills

- `project-setup-info-local`: continue the VS Code extension scaffold using the prescribed generator workflow.
- `no-slop`: keep README and marketplace copy concise.

## Process Constraints

- Use the official Generator Code scaffold rather than replacing it with an unrelated template.
- Preserve the user's existing files and unrelated changes.
- Use `apply_patch` for edits to existing text files.
- After the first substantive edit, run the narrowest relevant validation before making further edits.
- Ask before choosing an extension ID, publisher, or marketplace identity.
