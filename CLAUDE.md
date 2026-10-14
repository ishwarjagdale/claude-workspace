# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a general-purpose workspace. It may hold many unrelated scripts and programs in different languages, so there is no shared build, lint, or test setup. Keep each project self-contained and add a section for it to `README.md`.

### winkey.py

`winkey.py` is a single-file, stdlib-only, Windows-only script (see `README.md`). It installs a `WH_KEYBOARD_LL` hook via `ctypes` that swallows Right Alt (`VK_RMENU`) and injects Left Win with `SendInput`. Injected events (`LLKHF_INJECTED`) are ignored to avoid feedback loops.

There is no build, lint, or test setup. The script can only be run on Windows (`python winkey.py`); it exits immediately on other platforms.
