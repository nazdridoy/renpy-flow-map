# renpy-flow-map

`renpy-flow-map` is a zero-configuration, drop-in debugging utility for Ren'Py visual novels. It hooks directly into the Ren'Py engine during startup and live-streams story execution flow, decision branches, dialogue, and variable mutations straight to your terminal.

---

## Features

- **Real-Time Scene Tracking**: Logs every label transition and scene change as it occurs.
- **Choice Fork Mapping**: Displays active `menu` choice options, condition guards, and records the player's selected choice.
- **Conditional Branch Evaluation**: Traces `if`, `elif`, and `else` blocks with filename, line number, and evaluated truth values.
- **Variable Mutation Diffs**: Monitors the Ren'Py `store` and prints immediate `old -> new` diffs whenever integer, string, boolean, list, dict, or set variables change.
- **Dialogue Stream**: Strips Ren'Py text tags and displays clean speaker names and dialogue text in real time.
- **Zero Configuration**: Simply drop the script into your project `game/` folder. No project modifications required.

---

## Installation & Setup

1. Copy `renpy_flow_map.rpy` into your Ren'Py project's `game/` directory:
   ```bash
   cp renpy_flow_map.rpy /path/to/renpy-project/game/
   ```

2. Launch your game or project from a terminal so console output is visible:
   ```bash
   # Launching via Ren'Py SDK CLI:
   renpy /path/to/renpy-project run

   # Or launching the built game executable directly from terminal:
   ./MyGame.sh
   ```

3. To disable logging temporarily without removing the file, set:
   ```python
   FLOW_MAP_ENABLED = False
   ```
   at the top of `renpy_flow_map.rpy`.

---

## Live Console Output Example

When playing through a scene, your terminal displays a clear structured stream:

```text
[SCENE] -> chapter_1_intro
  [SAY] Narrator: The rain drummed against the windowpane.
  [VAR] affinity: 0 -> 10
  [FLOW] call -> check_weather (game/script.rpy:45)

[SCENE] -> check_weather
  [BRANCH] if raining == True -> True (game/script.rpy:52)
  [SAY] Alice: Looks like we are stuck inside for the day.

  [MENU] Path fork:
    - Choice: 'Offer to make hot tea' (if True)
    - Choice: 'Complain about the cold' (if True)
    - Choice: 'Secret investigation' (if has_key == True)
  [PICK] -> 'Offer to make hot tea'

  [VAR] tea_prepared: False -> True
  [SAY] Alice: Thank you, that would be lovely!
  [FLOW] jump -> kitchen_scene (game/script.rpy:98)
```

---

## Log Output Reference

| Tag | Event | Information Provided |
| :--- | :--- | :--- |
| `[SCENE]` | Label / Scene Transition | Target scene label name |
| `[SAY]` | Dialogue Line | Speaker and dialogue text (tags filtered) |
| `[MENU]` | Choice Fork | All displayed choices and condition guards |
| `[PICK]` | Player Selection | The choice picked by the user or script |
| `[BRANCH]` | Conditional Evaluation | Condition string, evaluated boolean, file and line |
| `[FLOW]` | Jump or Call | Control flow target label, file and line |
| `[VAR]` | Variable Mutation | Variable name and `old_value -> new_value` |

