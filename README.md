# claude-workspace

A general-purpose workspace for scripts and small programs built with Claude. Projects here are independent of each other and may use different languages and tools, so each should be self-contained and documented in its own section below.

## Contents

| Project | Description |
| --- | --- |
| [`winkey.py`](#winkeypy) | Makes Right Alt act as the Windows key (Windows, Python stdlib only) |

## winkey.py

Makes **Right Alt** act as the **Windows key**, for a keyboard whose Win key is dead (e.g. Kreo Hive). Windows only, Python standard library only, no admin rights, no reboot.

It installs a per-user low-level keyboard hook that swallows Right Alt and injects Left Win in its place, so taps open Start and combos like Right Alt+E work as Win+E.

### Usage

- Try it: `python winkey.py`. Tap Right Alt to open Start; Right Alt+E, +D and +L work as Win+E, +D and +L.
- Stop it: Ctrl+C in the console. Nothing persists, so Right Alt returns to normal.
- No console window: `pythonw winkey.py`. Stop it by ending `pythonw.exe` in Task Manager.
- Start at login (no admin): press Win+R, run `shell:startup`, and put a shortcut there with target `pythonw.exe C:\path\to\winkey.py`.

### Caveats

- While running, Right Alt no longer works as Alt/AltGr, on every connected keyboard. AltGr layouts (German, Spanish, etc.) lose AltGr characters.
- It does not work while an elevated (administrator) window has focus.
- Some antivirus tools flag keyboard hooks. The script is local and sends nothing anywhere.
