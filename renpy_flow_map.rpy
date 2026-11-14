# Copyright (c) 2026 nazDridoy
# SPDX-License-Identifier: MIT
#
# renpy-flow-map
# ===========================================================================
# Real-time terminal tracing and flow mapping for Ren'Py visual novels.
# Logs scene transitions, choice menus, conditional branches, dialogue,
# and variable mutations directly to the console.
# ===========================================================================

init -999 python:
    """
    renpy-flow-map
    ================================
    Real-time terminal tracing and flow mapping for Ren'Py visual novels.
    """
    import copy
    import builtins

    FLOW_MAP_ENABLED = True
    CLI_LOG_ENABLED = FLOW_MAP_ENABLED

    if FLOW_MAP_ENABLED:
        # Lock in true Python built-in types so game variables named "set", "list", etc. never break isinstance()
        _SAFE_TYPES = (
            builtins.int,
            builtins.float,
            builtins.str,
            builtins.bool,
            builtins.list,
            builtins.dict,
            builtins.set,
        )

        _last_node = None
        _tracked_vars = {}
        _ignore_vars = {
            "FLOW_MAP_ENABLED", "CLI_LOG_ENABLED", "mouse_visible", "suppress_overlay",
            "main_menu", "_last_node", "_tracked_vars", "_ignore_vars", "_SAFE_TYPES"
        }

        def _check_vars():
            global _tracked_vars
            for k, v in list(store.__dict__.items()):
                if k.startswith("_") or k in _ignore_vars:
                    continue
                try:
                    if isinstance(v, _SAFE_TYPES):
                        if k not in _tracked_vars:
                            _tracked_vars[k] = copy.copy(v)
                        elif _tracked_vars[k] != v:
                            old_v = _tracked_vars[k]
                            _tracked_vars[k] = copy.copy(v)
                            print(f"  [VAR] {k}: {old_v!r} -> {v!r}", flush=True)
                except Exception:
                    # Safely ignore custom objects with broken __eq__ or __copy__ methods
                    continue

        # 1. SCENE / LABEL CHANGES
        def _cli_label_log(name, abnormal):
            if not name.startswith("_"):
                _check_vars()
                print(f"\n[SCENE] -> {name}", flush=True)

        config.label_callback = _cli_label_log

        # 2. MENU FORKS & PLAYER PICKS
        _orig_menu = renpy.exports.menu

        def _cli_menu_wrapper(items, *args, **kwargs):
            print("  [MENU] Path fork:", flush=True)
            for caption, condition, block in items:
                if block is not None:
                    clean_cap = renpy.filter_text_tags(caption, allow=[])
                    print(f"    - Choice: {clean_cap!r} (if {condition})", flush=True)
            chosen = _orig_menu(items, *args, **kwargs)
            print(f"  [PICK] -> {chosen!r}", flush=True)
            _check_vars()
            return chosen

        renpy.exports.menu = _cli_menu_wrapper

        # 3. SINGLE-FIRE DIALOGUE, BRANCHES & JUMPS
        def _cli_statement_logger(name):
            global _last_node
            _check_vars()

            ctx = renpy.game.context()
            if not ctx or not ctx.current:
                return

            if ctx.current == _last_node:
                return
            _last_node = ctx.current

            node = renpy.game.script.lookup(ctx.current)
            filename = getattr(node, "filename", "") or ""
            lineno = getattr(node, "linenumber", 0)

            if "renpy/common" in filename or "renpy_flow_map.rpy" in filename or "universal_CLI_LOG.rpy" in filename:
                return

            # A. Dialogue lines
            if isinstance(node, renpy.ast.Say):
                who = f"{node.who}: " if node.who else ""
                try:
                    what = renpy.substitute(node.what)
                except Exception:
                    what = node.what
                what = renpy.filter_text_tags(what, allow=[])
                print(f"  [SAY] {who}{what}", flush=True)

            # B. Conditional branches (if / elif / else)
            elif isinstance(node, renpy.ast.If):
                for cond, block in node.entries:
                    try:
                        result = bool(renpy.python.py_eval(cond))
                    except Exception:
                        result = "?"
                    print(f"  [BRANCH] if {cond} -> {result} ({filename}:{lineno})", flush=True)
                    if result is True:
                        break

            # C. Jumps & Calls
            elif isinstance(node, (renpy.ast.Jump, renpy.ast.Call)):
                target = getattr(node, "target", None) or getattr(node, "label", "")
                print(f"  [FLOW] {name} -> {target} ({filename}:{lineno})", flush=True)

        config.statement_callbacks.append(_cli_statement_logger)

