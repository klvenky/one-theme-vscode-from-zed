# One (Zed) Themes

Light and dark VS Code themes ported from [Zed's built-in One themes](https://github.com/zed-industries/zed/blob/main/assets/themes/one/one.json).

The goal is parity with Zed rather than another One Dark variant. Every colour comes from Zed's `one.json`: editor and panel surfaces, borders, the full terminal ANSI palette, diagnostic and version-control colours, and the syntax palette.

## Themes

- One Light (Zed)
- One Dark (Zed)

Select one with `Preferences: Color Theme` (`Cmd+K Cmd+T`).

## Install from a VSIX

```sh
npx @vscode/vsce package
code --install-extension one-zed-theme-0.0.1.vsix
```

## Preview without installing

Open this folder in VS Code and press `F5`. That launches an Extension Development Host with both themes available.

## How the mapping works

Zed and VS Code do not describe a window the same way, so a few points are worth knowing.

Zed's syntax highlighting comes from tree-sitter captures, while VS Code uses TextMate scopes and semantic tokens. The themes set `semanticHighlighting` to `true` and define both, so languages with a semantic token provider match Zed most closely.

Some VS Code surfaces have no Zed counterpart. The activity bar follows Zed's tab bar surface, and the sidebar follows its panel surface. A few values, such as widget shadows and button hover states, are derived from Zed colours because Zed does not define them.

Bracket pair colourisation uses a single colour in both themes, since Zed does not tint bracket pairs by depth.

## Updating from upstream

The theme files are generated from Zed's `one.json`, vendored at `scripts/zed-one.json`. When Zed changes its palette, refresh that file and regenerate instead of hand-editing `themes/*.json`.

```sh
curl -sSL -o scripts/zed-one.json \
  https://raw.githubusercontent.com/zed-industries/zed/main/assets/themes/one/one.json
python3 scripts/generate-themes.py scripts/zed-one.json themes/
```
