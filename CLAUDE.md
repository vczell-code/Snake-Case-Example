# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-file Snake game (`snake_game.py`) built on Python's standard-library `turtle` module. There are no third-party dependencies, no build step, no linter config, and no tests. Keeping it standard-library-only is a stated feature of the project (see `README.md`).

## Commands

```bash
python snake_game.py                 # run the game (opens a Tk window and blocks until it is closed)
python -m py_compile snake_game.py   # syntax check without launching the window
```

Running the game needs a display and does not exit on its own (quit with `Q`/`Esc`), so use `py_compile` for a non-interactive check.

## Architecture

Everything in `snake_game.py` executes at module import time, top to bottom: configuration constants → global game state → screen and turtle setup → handler definitions → key bindings → the main `while True` loop. There is no `main()` and no `if __name__ == "__main__"` guard, so importing the module opens the window and starts the game. Any logic that should be unit-testable has to be separated from that module-level setup first.

**State** lives in module globals (`score`, `high_score`, `delay`, `is_paused`, `is_game_over`, `current_direction`, `next_direction`, `segments`). Functions that mutate them declare `global`. `high_score` is in-memory only and resets on each launch.

**Rendering** uses one `turtle.Turtle` per on-screen thing: `head`, `food`, one turtle per body segment in `segments`, plus hidden "pen" turtles (`border_pen`, `score_pen`, `msg_pen`) that draw text and the arena. `screen.tracer(0)` disables auto-refresh; the loop calls `screen.update()` once per tick. `msg_pen` is shared by the start prompt, pause banner, and game-over banner, so each caller clears it before writing.

**Input buffering**: key handlers never move the snake. They only set `next_direction`, and reject a reversal by comparing against `current_direction` (the direction actually applied last tick). The loop copies `next_direction` into `current_direction` once per tick. This is what prevents a quick double key press from turning the snake back into itself; preserve that split when changing input handling.

**Tick order** in the main loop: apply direction → remember previous head position → move head → wall check → self-collision check → food check (grow, score, speed up, relocate food) → shift body segments forward → `time.sleep(delay)`. Self-collision is tested against segment positions from *before* the shift, and a newly grown segment is parked at `(2000, 2000)` until the shift places it.

**Coordinates**: positions are multiples of `GRID_SIZE` (20) with the origin at the window centre. The playable area is defined by `ARENA_LEFT/RIGHT/BOTTOM/TOP`, which is shifted down 20px to leave room for the scoreboard at y=285. `ARENA_SIZE` is not referenced by any logic; the four bounds are the source of truth. Collisions use `turtle.distance()` thresholds (15 for food, 12 for self) rather than exact coordinate equality.

## Things to know before changing code

- The main loop is wrapped in `except (turtle.Terminator, Exception): pass` so closing the window exits quietly. This also swallows every real bug raised inside the loop: the window just closes with no traceback. Narrow or temporarily remove that handler when debugging.
- `restart_game()` moves old segment turtles off-screen and clears the list, but the turtle objects are never destroyed, so they accumulate across restarts.
- Fonts are hard-coded to `"Segoe UI"` (Windows); other platforms fall back to a Tk default.
