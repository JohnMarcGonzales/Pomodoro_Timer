# 🍅 Pomodoro Timer

A modern, themed Pomodoro timer app with adjustable durations, history tracking, and a compact, scalable UI. Built with Python and Tkinter.

## Features

- **Tomato (Pomodoro) Theme:** Adjustable from 25 to 50 minutes.
- **Blueberry (Short Break) Theme:** Adjustable from 5 to 15 minutes.
- **Banana (Long Break) Theme:** Occurs after 4 Pomodoros, adjustable from 40 minutes to 2 hours.
- **Scalable, Centered Window:** The app window is resizable and always opens centered on your screen.
- **Skip, Pause, Reset, and Exit:** Each timer can be skipped, paused/resumed, reset, or you can exit the app at any time with the Exit button.
- **Compact but Complete UI:** All controls and information are visible without clutter.
- **Counters and History:** Tracks how many Pomodoros, short breaks, and long breaks you've completed, and saves history between sessions.
- **Topmost Popups:** After every timer ends, a popup appears above all other windows (even games) to notify you.
- **Simple, Well-Commented Code:** Variable names are simple and every section is explained with comments for easy understanding and modification.

## How to Use

1. **Run the app:**
   ```sh
   python pomodoro.py
   ```
2. **Set durations:** Use the spinboxes to set your preferred Pomodoro, short break, and long break durations within their allowed ranges.
3. **Start the timer:** Click ▶ Start. Use ⏸ Pause, 🔄 Reset, ⏭ Skip, or ❌ Exit as needed.
4. **Track your progress:** See your current session counters and your all-time history at the bottom.
5. **Popups:** When a timer ends, a popup will appear on top of all windows to notify you.
6. **Exit:** Click the ❌ Exit button to close the app and save your history.

## Code Structure

- **Constants:**
  - `THEMES` and `LIMITS` define the look and allowed durations for each timer type.
- **PomodoroApp class:**
  - Handles all timer logic, UI, and history.
  - **State:** `self.state` is 'pomodoro', 'short', or 'long'.
  - **Durations:** `self.durations` holds the current durations for each timer.
  - **Counters:** `self.counters` tracks the current session; `self.history` is loaded/saved from `history.json`.
  - **UI:** Built in `build_ui()`, with all controls and labels clearly named.
  - **Timer Logic:** `start_timer`, `pause_timer`, `reset_timer`, `skip_timer`, `exit_app`, and `handle_cycle_end` manage the timer and state transitions.
  - **Popups:** `show_popup` ensures notifications are always on top.
  - **Window Centering:** `center_window` keeps the app centered on launch.
  - **History:** Automatically saved on close and loaded on start.

## Requirements
- Python 3.x
- Tkinter (usually included with Python)

## Customization
- Change theme colors or emojis in the `THEMES` dictionary.
- Adjust allowed duration ranges in the `LIMITS` dictionary.
- All variable names and logic are kept simple and commented for easy editing.

---

Enjoy your productive sessions! 🍅🫐🍌 
