#!/usr/bin/env python3
# pyright: basic
"""Generate VS Code color themes from Zed's One theme family.

Reads Zed's upstream `one.json` and emits one VS Code color-theme file per
variant, reusing Zed's exact hex values wherever VS Code exposes an
equivalent surface.
"""

import json
import os
import sys

# --- colour helpers ---------------------------------------------------------


def parse(c):
    c = c.lstrip("#")
    if len(c) == 6:
        c += "ff"
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4, 6))


def fmt(t):
    r, g, b, a = (max(0, min(255, int(round(v)))) for v in t)
    return "#%02x%02x%02x" % (r, g, b) if a == 255 else "#%02x%02x%02x%02x" % (r, g, b, a)


def alpha(c, a):
    """Return colour `c` with alpha replaced by float `a` (0..1)."""
    r, g, b, _ = parse(c)
    return fmt((r, g, b, a * 255))


def over(fg, bg):
    """Alpha-composite `fg` onto opaque `bg`."""
    fr, fg_, fb, fa = parse(fg)
    br, bg_, bb, _ = parse(bg)
    a = fa / 255
    return fmt((fr * a + br * (1 - a), fg_ * a + bg_ * (1 - a), fb * a + bb * (1 - a), 255))


def mix(c1, c2, t):
    """Blend opaque `c1` toward `c2` by `t` (0..1)."""
    a = parse(c1)
    b = parse(c2)
    return fmt(tuple(a[i] + (b[i] - a[i]) * t for i in range(4)))


# --- theme construction -----------------------------------------------------

TRANSPARENT = "#00000000"


def build(theme):
    s = dict(theme["style"])
    syn = {k: v["color"] for k, v in s.pop("syntax").items()}
    players = s["players"]
    dark = theme["appearance"] == "dark"

    def z(key):
        return s[key]

    editor_bg = z("editor.background")
    surface = z("surface.background")
    elevated = z("elevated_surface.background")
    text = z("text")
    muted = z("text.muted")
    accent = z("text.accent")
    border = z("border")
    border_var = z("border.variant")
    border_focus = z("border.focused")
    cursor = players[0]["cursor"]
    selection = players[0]["selection"]

    # Foreground for filled accent surfaces (buttons, badges).
    on_accent = editor_bg if dark else "#fafafaff"
    accent_hover = mix(accent, "#ffffffff" if dark else "#000000ff", 0.12)

    colors = {
        # base
        "focusBorder": border_focus,
        "foreground": text,
        "disabledForeground": z("text.disabled"),
        "descriptionForeground": muted,
        "errorForeground": z("error"),
        "icon.foreground": z("icon"),
        "selection.background": selection,
        "widget.border": border,
        "widget.shadow": "#00000066" if dark else "#0000001a",
        "sash.hoverBorder": border_focus,
        "window.activeBorder": border,
        "window.inactiveBorder": border_var,

        # text / markdown preview
        "textLink.foreground": accent,
        "textLink.activeForeground": z("link_text.hover"),
        "textBlockQuote.background": surface,
        "textBlockQuote.border": border_var,
        "textCodeBlock.background": elevated,
        "textPreformat.foreground": syn["string"],
        "textPreformat.background": elevated,
        "textSeparator.foreground": border,

        # buttons
        "button.background": accent,
        "button.foreground": on_accent,
        "button.hoverBackground": accent_hover,
        "button.secondaryBackground": z("element.background"),
        "button.secondaryForeground": text,
        "button.secondaryHoverBackground": z("element.hover"),
        "checkbox.background": z("element.background"),
        "checkbox.foreground": text,
        "checkbox.border": border,

        # inputs
        "dropdown.background": elevated,
        "dropdown.listBackground": elevated,
        "dropdown.foreground": text,
        "dropdown.border": border,
        "input.background": z("element.background"),
        "input.foreground": text,
        "input.border": border,
        "input.placeholderForeground": z("text.placeholder"),
        "inputOption.activeBackground": alpha(accent, 0.2),
        "inputOption.activeBorder": border_focus,
        "inputOption.activeForeground": text,
        "inputValidation.errorBackground": over(z("error.background"), elevated),
        "inputValidation.errorBorder": z("error.border"),
        "inputValidation.errorForeground": text,
        "inputValidation.warningBackground": over(z("warning.background"), elevated),
        "inputValidation.warningBorder": z("warning.border"),
        "inputValidation.warningForeground": text,
        "inputValidation.infoBackground": over(z("info.background"), elevated),
        "inputValidation.infoBorder": z("info.border"),
        "inputValidation.infoForeground": text,

        # scrollbars
        "scrollbar.shadow": TRANSPARENT,
        "scrollbarSlider.background": z("scrollbar.thumb.background"),
        "scrollbarSlider.hoverBackground": z("scrollbar.thumb.hover_background"),
        "scrollbarSlider.activeBackground": z("scrollbar.thumb.hover_background"),

        # badges / progress
        "badge.background": accent,
        "badge.foreground": on_accent,
        "activityBarBadge.background": accent,
        "activityBarBadge.foreground": on_accent,
        "progressBar.background": accent,

        # lists & trees
        "list.activeSelectionBackground": z("element.selected"),
        "list.activeSelectionForeground": text,
        "list.activeSelectionIconForeground": z("icon"),
        "list.inactiveSelectionBackground": z("element.selected"),
        "list.inactiveSelectionForeground": text,
        "list.hoverBackground": z("element.hover"),
        "list.hoverForeground": text,
        "list.focusBackground": z("element.selected"),
        "list.focusForeground": text,
        "list.focusOutline": TRANSPARENT,
        "list.highlightForeground": accent,
        "list.focusHighlightForeground": accent,
        "list.errorForeground": z("error"),
        "list.warningForeground": z("warning"),
        "list.dropBackground": z("drop_target.background"),
        "listFilterWidget.background": elevated,
        "listFilterWidget.outline": border_focus,
        "listFilterWidget.noMatchesOutline": z("error"),
        "tree.indentGuidesStroke": border_var,
        "tree.inactiveIndentGuidesStroke": border_var,

        # activity bar (no Zed equivalent; follows the tab/panel surface)
        "activityBar.background": surface,
        "activityBar.foreground": z("icon"),
        "activityBar.inactiveForeground": z("icon.muted"),
        "activityBar.border": border_var,
        "activityBar.activeBorder": accent,
        "activityBar.activeBackground": TRANSPARENT,
        "activityBarTop.foreground": z("icon"),
        "activityBarTop.inactiveForeground": z("icon.muted"),
        "activityBarTop.activeBorder": accent,

        # side bar
        "sideBar.background": z("panel.background"),
        "sideBar.foreground": muted,
        "sideBar.border": border_var,
        "sideBarTitle.foreground": muted,
        "sideBarSectionHeader.background": z("panel.background"),
        "sideBarSectionHeader.foreground": muted,
        "sideBarSectionHeader.border": border_var,

        # editor groups & tabs
        "editorGroup.border": border_var,
        "editorGroup.dropBackground": z("drop_target.background"),
        "editorGroupHeader.tabsBackground": z("tab_bar.background"),
        "editorGroupHeader.tabsBorder": border_var,
        "editorGroupHeader.noTabsBackground": z("tab_bar.background"),
        "editorPane.background": editor_bg,
        "tab.activeBackground": z("tab.active_background"),
        "tab.activeForeground": text,
        "tab.inactiveBackground": z("tab.inactive_background"),
        "tab.inactiveForeground": muted,
        "tab.hoverBackground": z("element.hover"),
        "tab.border": border_var,
        "tab.activeBorder": z("tab.active_background"),
        "tab.activeBorderTop": TRANSPARENT,
        "tab.unfocusedActiveBackground": z("tab.active_background"),
        "tab.unfocusedActiveForeground": muted,
        "tab.unfocusedInactiveBackground": z("tab.inactive_background"),
        "tab.unfocusedInactiveForeground": z("text.disabled"),
        "tab.lastPinnedBorder": border_var,

        # breadcrumbs (Zed's editor toolbar)
        "breadcrumb.background": z("toolbar.background"),
        "breadcrumb.foreground": muted,
        "breadcrumb.focusForeground": text,
        "breadcrumb.activeSelectionForeground": text,
        "breadcrumbPicker.background": elevated,

        # editor
        "editor.background": editor_bg,
        "editor.foreground": z("editor.foreground"),
        "editorLineNumber.foreground": z("editor.line_number"),
        "editorLineNumber.activeForeground": z("editor.active_line_number"),
        "editorCursor.foreground": cursor,
        "editor.selectionBackground": selection,
        "editor.inactiveSelectionBackground": alpha(selection, 0.15),
        "editor.selectionHighlightBackground": z("editor.document_highlight.read_background"),
        "editor.wordHighlightBackground": z("editor.document_highlight.read_background"),
        "editor.wordHighlightStrongBackground": z("editor.document_highlight.write_background"),
        "editor.findMatchBackground": z("search.active_match_background"),
        "editor.findMatchHighlightBackground": z("search.match_background"),
        "editor.findRangeHighlightBackground": alpha(selection, 0.15),
        "editor.hoverHighlightBackground": z("editor.highlighted_line.background"),
        "editor.lineHighlightBackground": z("editor.active_line.background"),
        "editor.rangeHighlightBackground": z("editor.highlighted_line.background"),
        "editorWhitespace.foreground": z("editor.invisible"),
        "editorIndentGuide.background1": z("editor.wrap_guide"),
        "editorIndentGuide.activeBackground1": z("editor.active_wrap_guide"),
        "editorRuler.foreground": z("editor.wrap_guide"),
        "editorBracketMatch.background": z("editor.document_highlight.read_background"),
        "editorBracketMatch.border": border_focus,
        "editorCodeLens.foreground": z("hint"),
        "editorInlayHint.foreground": z("hint"),
        "editorInlayHint.background": TRANSPARENT,
        "editorGhostText.foreground": z("predictive"),
        "editorLink.activeForeground": z("link_text.hover"),
        "editorLightBulb.foreground": z("warning"),
        "editorLightBulbAutoFix.foreground": z("info"),
        "editorUnnecessaryCode.opacity": "#0000007f" if dark else "#00000059",
        "editorStickyScroll.background": editor_bg,
        "editorStickyScrollHover.background": z("element.hover"),

        # gutter & diagnostics
        "editorGutter.background": z("editor.gutter.background"),
        "editorGutter.addedBackground": z("version_control.added"),
        "editorGutter.modifiedBackground": z("version_control.modified"),
        "editorGutter.deletedBackground": z("version_control.deleted"),
        "editorGutter.foldingControlForeground": z("icon.muted"),
        "editorError.foreground": z("error"),
        "editorWarning.foreground": z("warning"),
        "editorInfo.foreground": z("info"),
        "editorHint.foreground": z("hint"),

        # overview ruler
        "editorOverviewRuler.border": TRANSPARENT,
        "editorOverviewRuler.errorForeground": z("error"),
        "editorOverviewRuler.warningForeground": z("warning"),
        "editorOverviewRuler.infoForeground": z("info"),
        "editorOverviewRuler.addedForeground": z("version_control.added"),
        "editorOverviewRuler.modifiedForeground": z("version_control.modified"),
        "editorOverviewRuler.deletedForeground": z("version_control.deleted"),
        "editorOverviewRuler.findMatchForeground": z("search.match_background"),
        "editorOverviewRuler.selectionHighlightForeground": selection,
        "editorOverviewRuler.wordHighlightForeground": z("editor.document_highlight.read_background"),
        "editorOverviewRuler.wordHighlightStrongForeground": z("editor.document_highlight.write_background"),
        "editorOverviewRuler.bracketMatchForeground": border_focus,

        # minimap
        "minimap.background": editor_bg,
        "minimap.findMatchHighlight": z("search.match_background"),
        "minimap.selectionHighlight": selection,
        "minimap.errorHighlight": z("error"),
        "minimap.warningHighlight": z("warning"),
        "minimapSlider.background": z("scrollbar.thumb.background"),
        "minimapSlider.hoverBackground": z("scrollbar.thumb.hover_background"),
        "minimapSlider.activeBackground": z("scrollbar.thumb.hover_background"),
        "minimapGutter.addedBackground": z("version_control.added"),
        "minimapGutter.modifiedBackground": z("version_control.modified"),
        "minimapGutter.deletedBackground": z("version_control.deleted"),

        # brackets: Zed does not rainbow-colour pairs
        "editorBracketHighlight.foreground1": syn["punctuation.bracket"],
        "editorBracketHighlight.foreground2": syn["punctuation.bracket"],
        "editorBracketHighlight.foreground3": syn["punctuation.bracket"],
        "editorBracketHighlight.foreground4": syn["punctuation.bracket"],
        "editorBracketHighlight.foreground5": syn["punctuation.bracket"],
        "editorBracketHighlight.foreground6": syn["punctuation.bracket"],
        "editorBracketHighlight.unexpectedBracket.foreground": z("error"),

        # diffs & merges
        "diffEditor.insertedTextBackground": z("version_control.word_added"),
        "diffEditor.removedTextBackground": z("version_control.word_deleted"),
        "diffEditor.insertedLineBackground": z("created.background"),
        "diffEditor.removedLineBackground": z("deleted.background"),
        "diffEditor.border": border_var,
        "diffEditorGutter.insertedLineBackground": z("created.background"),
        "diffEditorGutter.removedLineBackground": z("deleted.background"),
        "merge.currentHeaderBackground": alpha(z("created"), 0.35),
        "merge.currentContentBackground": alpha(z("created"), 0.15),
        "merge.incomingHeaderBackground": alpha(z("info"), 0.35),
        "merge.incomingContentBackground": alpha(z("info"), 0.15),
        "merge.border": border_var,

        # widgets
        "editorWidget.background": elevated,
        "editorWidget.foreground": text,
        "editorWidget.border": border,
        "editorHoverWidget.background": elevated,
        "editorHoverWidget.foreground": text,
        "editorHoverWidget.border": border,
        "editorHoverWidget.statusBarBackground": surface,
        "editorSuggestWidget.background": elevated,
        "editorSuggestWidget.foreground": text,
        "editorSuggestWidget.border": border,
        "editorSuggestWidget.selectedBackground": z("element.selected"),
        "editorSuggestWidget.selectedForeground": text,
        "editorSuggestWidget.highlightForeground": accent,
        "editorSuggestWidget.focusHighlightForeground": accent,
        "editorMarkerNavigation.background": elevated,
        "editorMarkerNavigationError.background": z("error"),
        "editorMarkerNavigationWarning.background": z("warning"),
        "editorMarkerNavigationInfo.background": z("info"),
        "peekView.border": border_focus,
        "peekViewEditor.background": editor_bg,
        "peekViewEditor.matchHighlightBackground": z("search.match_background"),
        "peekViewResult.background": surface,
        "peekViewResult.lineForeground": muted,
        "peekViewResult.fileForeground": text,
        "peekViewResult.selectionBackground": z("element.selected"),
        "peekViewResult.selectionForeground": text,
        "peekViewResult.matchHighlightBackground": z("search.match_background"),
        "peekViewTitle.background": surface,
        "peekViewTitleLabel.foreground": text,
        "peekViewTitleDescription.foreground": muted,

        # quick input / command palette
        "quickInput.background": elevated,
        "quickInput.foreground": text,
        "quickInputTitle.background": elevated,
        "quickInputList.focusBackground": z("element.selected"),
        "quickInputList.focusForeground": text,
        "quickInputList.focusIconForeground": z("icon"),
        "pickerGroup.border": border_var,
        "pickerGroup.foreground": muted,
        "keybindingLabel.background": z("element.background"),
        "keybindingLabel.foreground": text,
        "keybindingLabel.border": border,
        "keybindingLabel.bottomBorder": border,

        # panel & terminal
        "panel.background": z("terminal.background"),
        "panel.border": border_var,
        "panelTitle.activeForeground": text,
        "panelTitle.inactiveForeground": muted,
        "panelTitle.activeBorder": accent,
        "panelSection.border": border_var,
        "panelSectionHeader.background": z("panel.background"),
        "panelSectionHeader.foreground": muted,
        "terminal.background": z("terminal.background"),
        "terminal.foreground": z("terminal.foreground"),
        "terminal.border": border_var,
        "terminal.selectionBackground": selection,
        "terminalCursor.foreground": cursor,
        "terminalCursor.background": z("terminal.background"),

        # status bar
        "statusBar.background": z("status_bar.background"),
        "statusBar.foreground": muted,
        "statusBar.border": border_var,
        "statusBar.noFolderBackground": z("status_bar.background"),
        "statusBar.noFolderForeground": muted,
        "statusBar.debuggingBackground": z("status_bar.background"),
        "statusBar.debuggingForeground": z("modified"),
        "statusBar.debuggingBorder": z("modified"),
        "statusBarItem.hoverBackground": z("ghost_element.hover"),
        "statusBarItem.activeBackground": z("ghost_element.active"),
        "statusBarItem.prominentBackground": z("element.selected"),
        "statusBarItem.prominentForeground": text,
        "statusBarItem.prominentHoverBackground": z("element.hover"),
        "statusBarItem.remoteBackground": z("status_bar.background"),
        "statusBarItem.remoteForeground": accent,
        "statusBarItem.errorBackground": z("status_bar.background"),
        "statusBarItem.errorForeground": z("error"),
        "statusBarItem.warningBackground": z("status_bar.background"),
        "statusBarItem.warningForeground": z("warning"),

        # title bar & menus
        "titleBar.activeBackground": z("title_bar.background"),
        "titleBar.activeForeground": text,
        "titleBar.inactiveBackground": z("title_bar.inactive_background"),
        "titleBar.inactiveForeground": muted,
        "titleBar.border": border_var,
        "menubar.selectionBackground": z("ghost_element.hover"),
        "menubar.selectionForeground": text,
        "menu.background": elevated,
        "menu.foreground": text,
        "menu.border": border,
        "menu.selectionBackground": z("element.selected"),
        "menu.selectionForeground": text,
        "menu.separatorBackground": border_var,

        # notifications
        "notificationCenter.border": border,
        "notificationCenterHeader.background": surface,
        "notificationCenterHeader.foreground": muted,
        "notifications.background": elevated,
        "notifications.foreground": text,
        "notifications.border": border_var,
        "notificationToast.border": border,
        "notificationLink.foreground": accent,
        "notificationsErrorIcon.foreground": z("error"),
        "notificationsWarningIcon.foreground": z("warning"),
        "notificationsInfoIcon.foreground": z("info"),
        "banner.background": surface,
        "banner.foreground": text,
        "banner.iconForeground": accent,

        # extensions & welcome
        "extensionButton.prominentBackground": accent,
        "extensionButton.prominentForeground": on_accent,
        "extensionButton.prominentHoverBackground": accent_hover,
        "extensionBadge.remoteBackground": accent,
        "extensionBadge.remoteForeground": on_accent,
        "welcomePage.background": editor_bg,
        "welcomePage.tileBackground": elevated,
        "welcomePage.tileHoverBackground": z("element.hover"),
        "welcomePage.progress.background": z("element.background"),
        "welcomePage.progress.foreground": accent,
        "walkThrough.embeddedEditorBackground": elevated,

        # source control
        "gitDecoration.addedResourceForeground": z("created"),
        "gitDecoration.untrackedResourceForeground": z("created"),
        "gitDecoration.modifiedResourceForeground": z("modified"),
        "gitDecoration.stageModifiedResourceForeground": z("modified"),
        "gitDecoration.deletedResourceForeground": z("deleted"),
        "gitDecoration.stageDeletedResourceForeground": z("deleted"),
        "gitDecoration.renamedResourceForeground": z("renamed"),
        "gitDecoration.conflictingResourceForeground": z("conflict"),
        "gitDecoration.ignoredResourceForeground": z("ignored"),
        "gitDecoration.submoduleResourceForeground": z("hint"),

        # debug
        "debugToolBar.background": elevated,
        "debugToolBar.border": border,
        "editor.stackFrameHighlightBackground": z("modified.background"),
        "editor.focusedStackFrameHighlightBackground": z("created.background"),
        "debugIcon.breakpointForeground": z("deleted"),
        "debugIcon.breakpointDisabledForeground": z("ignored"),
        "debugConsole.infoForeground": z("info"),
        "debugConsole.warningForeground": z("warning"),
        "debugConsole.errorForeground": z("error"),
        "debugConsole.sourceForeground": muted,
        "debugConsoleInputIcon.foreground": accent,
        "debugView.stateLabelBackground": z("element.background"),
        "debugView.stateLabelForeground": text,
        "debugView.valueChangedHighlight": alpha(accent, 0.4),

        # testing
        "testing.iconFailed": z("error"),
        "testing.iconErrored": z("error"),
        "testing.iconPassed": z("created"),
        "testing.iconQueued": z("modified"),
        "testing.iconSkipped": z("ignored"),
        "testing.iconUnset": z("ignored"),

        # notebooks
        "notebook.editorBackground": editor_bg,
        "notebook.cellEditorBackground": editor_bg,
        "notebook.cellBorderColor": border_var,
        "notebook.focusedCellBorder": border_focus,
        "notebook.selectedCellBackground": z("element.selected"),
        "notebook.cellHoverBackground": z("element.hover"),

        # settings editor
        "settings.headerForeground": text,
        "settings.modifiedItemIndicator": z("modified"),
        "settings.dropdownBackground": z("element.background"),
        "settings.dropdownBorder": border,
        "settings.textInputBackground": z("element.background"),
        "settings.textInputBorder": border,
        "settings.numberInputBackground": z("element.background"),
        "settings.numberInputBorder": border,
        "settings.checkboxBackground": z("element.background"),
        "settings.checkboxBorder": border,
        "settings.focusedRowBackground": z("element.hover"),

        # charts
        "charts.foreground": text,
        "charts.lines": border,
        "charts.red": syn["property"],
        "charts.blue": syn["function"],
        "charts.yellow": syn["constant"],
        "charts.orange": syn["number"],
        "charts.green": syn["string"],
        "charts.purple": syn["keyword"],
    }

    # Terminal ANSI palette, copied straight from Zed.
    for name in ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"):
        colors["terminal.ansi" + name.capitalize()] = z("terminal.ansi." + name)
        colors["terminal.ansiBright" + name.capitalize()] = z("terminal.ansi.bright_" + name)

    # Outline / suggestion icons follow the syntax palette.
    symbol_map = {
        "class": "type", "interface": "type", "struct": "type", "typeParameter": "type",
        "enumerator": "enum", "enumeratorMember": "variant",
        "function": "function", "method": "function", "constructor": "constructor",
        "variable": "variable", "constant": "constant",
        "property": "property", "field": "property",
        "string": "string", "number": "number", "boolean": "boolean",
        "keyword": "keyword", "operator": "operator",
        "module": "namespace", "namespace": "namespace",
        "event": "attribute", "snippet": "keyword",
    }
    for vs_name, zed_name in symbol_map.items():
        colors["symbolIcon.%sForeground" % vs_name] = syn[zed_name]
    for vs_name in ("array", "object", "null", "reference", "text", "unit", "color", "file", "folder", "key"):
        colors["symbolIcon.%sForeground" % vs_name] = text

    return colors, syn


# --- TextMate scope mapping -------------------------------------------------

def token_colors(syn):
    def rule(name, scopes, color_key, style=None, weight=None):
        settings = {"foreground": syn[color_key]}
        font = []
        if style:
            font.append(style)
        if weight:
            font.append(weight)
        if font:
            settings["fontStyle"] = " ".join(font)
        return {"name": name, "scope": scopes, "settings": settings}

    return [
        rule("Comment", ["comment", "punctuation.definition.comment"], "comment"),
        rule("Documentation comment", [
            "comment.block.documentation",
            "comment.line.documentation",
            "string.quoted.docstring",
        ], "comment.doc"),

        rule("Variable", [
            "variable",
            "variable.other",
            "meta.definition.variable.name",
            "support.variable",
        ], "variable"),
        rule("Parameter", [
            "variable.parameter",
            "meta.function.parameters variable",
        ], "variable.parameter"),
        rule("Special variable", [
            "variable.language",
            "variable.other.this",
        ], "variable.special"),

        rule("Property", [
            "variable.other.property",
            "variable.other.object.property",
            "meta.object-literal.key",
            "support.type.property-name",
        ], "property"),

        rule("Punctuation", ["punctuation"], "punctuation"),
        rule("Brackets", [
            "punctuation.section",
            "punctuation.definition.block",
            "punctuation.definition.bracket",
            "punctuation.definition.parameters",
            "punctuation.definition.array",
            "meta.brace",
        ], "punctuation.bracket"),
        rule("Delimiters", [
            "punctuation.separator",
            "punctuation.terminator",
            "punctuation.accessor",
        ], "punctuation.delimiter"),
        rule("Template punctuation", [
            "punctuation.definition.template-expression",
            "punctuation.section.embedded",
            "keyword.other.substitution",
        ], "punctuation.special"),

        rule("Keyword", [
            "keyword",
            "keyword.control",
            "storage",
            "storage.type",
            "storage.modifier",
            "keyword.operator.new",
            "keyword.operator.expression",
            "keyword.operator.logical.python",
        ], "keyword"),
        rule("Operator", [
            "keyword.operator",
            "storage.type.function.arrow",
        ], "operator"),
        rule("Preprocessor", [
            "meta.preprocessor",
            "keyword.control.directive",
            "entity.name.function.preprocessor",
            "punctuation.definition.preprocessor",
        ], "preproc"),

        rule("Function", [
            "entity.name.function",
            "support.function",
            "variable.function",
            "meta.function-call.generic",
        ], "function"),
        rule("Constructor", [
            "entity.name.function.constructor",
            "support.class.constructor",
        ], "constructor"),

        rule("Type", [
            "entity.name.type",
            "entity.name.class",
            "support.type",
            "support.class",
            "entity.other.inherited-class",
        ], "type"),
        rule("Enum", ["entity.name.type.enum"], "enum"),
        rule("Enum member", [
            "variable.other.enummember",
            "constant.other.enum",
        ], "variant"),
        rule("Namespace", [
            "entity.name.namespace",
            "entity.name.scope-resolution",
            "support.module",
        ], "namespace"),

        rule("String", [
            "string",
            "string.quoted",
            "punctuation.definition.string",
        ], "string"),
        rule("Escape sequence", ["constant.character.escape"], "string.escape"),
        rule("Regular expression", [
            "string.regexp",
            "punctuation.definition.group",
        ], "string.regex"),
        rule("Special string", [
            "string.other",
            "string.unquoted",
        ], "string.special"),
        rule("Symbol", [
            "constant.other.symbol",
            "constant.other.key",
        ], "string.special.symbol"),

        rule("Number", ["constant.numeric"], "number"),
        rule("Boolean", [
            "constant.language.boolean",
            "constant.language.null",
            "constant.language.undefined",
            "constant.language.nil",
        ], "boolean"),
        rule("Constant", [
            "constant",
            "constant.other",
            "constant.language",
            "variable.other.constant",
            "entity.name.constant",
            "support.constant",
        ], "constant"),

        rule("Tag", ["entity.name.tag"], "tag"),
        rule("Attribute", [
            "entity.other.attribute-name",
            "meta.attribute",
            "meta.decorator",
            "punctuation.decorator",
        ], "attribute"),
        rule("Label", [
            "entity.name.label",
            "constant.other.label",
        ], "label"),
        rule("Embedded", ["meta.embedded"], "embedded"),

        rule("CSS selector", [
            "entity.other.attribute-name.class.css",
            "entity.other.attribute-name.id.css",
            "entity.name.tag.css",
            "entity.name.tag.reference.scss",
        ], "selector"),
        rule("CSS pseudo selector", [
            "entity.other.attribute-name.pseudo-class",
            "entity.other.attribute-name.pseudo-element",
        ], "selector.pseudo"),

        rule("Markup heading", [
            "markup.heading",
            "entity.name.section",
        ], "title", weight="bold"),
        rule("Markup emphasis", ["markup.italic"], "emphasis", style="italic"),
        rule("Markup strong", ["markup.bold"], "emphasis.strong", weight="bold"),
        rule("Markup link text", [
            "string.other.link.title",
            "string.other.link.description",
        ], "link_text", style="italic"),
        rule("Markup link URI", [
            "markup.underline.link",
            "string.other.link",
        ], "link_uri"),
        rule("Markup raw", [
            "markup.inline.raw",
            "markup.raw",
            "markup.fenced_code",
        ], "text.literal"),
        rule("Markup list marker", [
            "punctuation.definition.list.begin.markdown",
            "beginning.punctuation.definition.list.markdown",
        ], "punctuation.list_marker"),
        rule("Markup punctuation", [
            "punctuation.definition.heading.markdown",
            "punctuation.definition.bold.markdown",
            "punctuation.definition.italic.markdown",
            "punctuation.definition.quote.begin.markdown",
        ], "punctuation.markup"),
        rule("Diff inserted", [
            "markup.inserted",
            "meta.diff.header.to-file",
        ], "diff.plus"),
        rule("Diff deleted", [
            "markup.deleted",
            "meta.diff.header.from-file",
        ], "diff.minus"),

        {
            "name": "Invalid",
            "scope": ["invalid", "invalid.illegal"],
            "settings": {"foreground": syn["punctuation.special"]},
        },
    ]


def semantic_token_colors(syn):
    mapping = {
        "variable": "variable",
        "parameter": "variable.parameter",
        "property": "property",
        "function": "function",
        "method": "function",
        "macro": "preproc",
        "class": "type",
        "interface": "type",
        "struct": "type",
        "type": "type",
        "typeParameter": "type",
        "enum": "enum",
        "enumMember": "variant",
        "namespace": "namespace",
        "keyword": "keyword",
        "modifier": "keyword",
        "string": "string",
        "number": "number",
        "regexp": "string.regex",
        "operator": "operator",
        "comment": "comment",
        "decorator": "attribute",
        "event": "attribute",
        "label": "label",
        "selfKeyword": "variable.special",
        "*.defaultLibrary": "variable.special",
    }
    return {k: syn[v] for k, v in mapping.items()}


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    data = json.load(open(src))
    targets = {
        "One Dark": ("one-dark-zed-color-theme.json", "One Dark (Zed)"),
        "One Light": ("one-light-zed-color-theme.json", "One Light (Zed)"),
    }

    for theme in data["themes"]:
        filename, label = targets[theme["name"]]
        colors, syn = build(theme)
        doc = {
            "$schema": "vscode://schemas/color-theme",
            "name": label,
            "type": theme["appearance"],
            "semanticHighlighting": True,
            "colors": colors,
            "semanticTokenColors": semantic_token_colors(syn),
            "tokenColors": token_colors(syn),
        }
        path = os.path.join(out_dir, filename)
        with open(path, "w") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")
        print("wrote %s (%d colors, %d token rules)" % (path, len(colors), len(doc["tokenColors"])))


if __name__ == "__main__":
    main()
