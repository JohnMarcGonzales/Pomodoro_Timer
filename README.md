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

Optional (enable notifications & tray icon):

- win10toast (Windows toast notifications)
- pystray + pillow (system tray icon support)

## Build Windows EXE

You can bundle the app into a single Windows executable using PyInstaller.

1. Install dependencies:
  ```powershell
  pip install pyinstaller win10toast pystray pillow
  ```
2. Build (basic):
  ```powershell
  pyinstaller --onefile --windowed --name PomodoroTimer pomodoro.py
  ```
3. (Optional) Include an icon (place tomato.ico in project root):
  ```powershell
  pyinstaller --onefile --windowed --icon tomato.ico --name PomodoroTimer pomodoro.py
  ```
4. Resulting EXE will be in `dist/PomodoroTimer.exe`.

### Data Persistence Location

History and settings are stored in (priority order):

1. Path set via env var `POMODORO_DATA_DIR` (if defined)
2. `%APPDATA%\PomodoroTimer` (default on Windows)
3. `<exe folder>\data` (when frozen and no APPDATA)
4. User home `~/.pomodoro_timer` (fallback)

This keeps your stats across upgrades. To create a portable copy, set `POMODORO_DATA_DIR` to a relative folder before launching the EXE.

Example (PowerShell):
```powershell
$env:POMODORO_DATA_DIR = "$PWD\portable_data"; .\PomodoroTimer.exe
```

### Using a Script

You can create a PowerShell script (build_exe.ps1):
```powershell
param([switch]$Clean,[string]$Name='PomodoroTimer')
if($Clean){ Remove-Item -Recurse -Force dist,build -ErrorAction SilentlyContinue }
if(-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)){ pip install pyinstaller }
$icon=''; if(Test-Path 'tomato.ico'){ $icon='--icon tomato.ico' }
pyinstaller --onefile --windowed $icon --name $Name pomodoro.py
```

Optional (enable notifications & tray icon):

- win10toast (Windows toast notifications)
- pystray + pillow (system tray icon support)

## Build Windows EXE

You can bundle the app into a single Windows executable using PyInstaller.

1. Install dependencies:
  ```powershell
  pip install pyinstaller win10toast pystray pillow
  ```
2. Build (basic):
  ```powershell
  pyinstaller --onefile --windowed --name PomodoroTimer pomodoro.py
  ```
3. (Optional) Include an icon (place tomato.ico in project root):
  ```powershell
  pyinstaller --onefile --windowed --icon tomato.ico --name PomodoroTimer pomodoro.py
  ```
4. Resulting EXE will be in `dist/PomodoroTimer.exe`.

### Data Persistence Location

History and settings are stored in (priority order):

1. Path set via env var `POMODORO_DATA_DIR` (if defined)
2. `%APPDATA%\PomodoroTimer` (default on Windows)
3. `<exe folder>\data` (when frozen and no APPDATA)
4. User home `~/.pomodoro_timer` (fallback)

This keeps your stats across upgrades. To create a portable copy, set `POMODORO_DATA_DIR` to a relative folder before launching the EXE.

Example (PowerShell):
```powershell
$env:POMODORO_DATA_DIR = "$PWD\portable_data"; .\PomodoroTimer.exe
```

### Using the Provided Script

You can also run `powershell -File build_exe.ps1` which auto-adds the icon if present.

Optional (enable notifications & tray icon):

- win10toast (Windows toast notifications)
- pystray + pillow (system tray icon support)

## Build Windows EXE

You can bundle the app into a single Windows executable using PyInstaller.

1. Install dependencies:
  ```powershell
  pip install pyinstaller win10toast pystray pillow
  ```
2. Build (basic):
  ```powershell
  pyinstaller --onefile --windowed --name PomodoroTimer pomodoro.py
  ```
3. (Optional) Include an icon (place tomato.ico in project root):
  ```powershell
  pyinstaller --onefile --windowed --icon tomato.ico --name PomodoroTimer pomodoro.py
  ```
4. Resulting EXE will be in `dist/PomodoroTimer.exe`.

### Data Persistence Location

History and settings are stored in (priority order):

1. Path set via env var `POMODORO_DATA_DIR` (if defined)
2. `%APPDATA%\PomodoroTimer` (default on Windows)
3. `<exe folder>\data` (when frozen and no APPDATA)
4. User home `~/.pomodoro_timer` (fallback)

This keeps your stats across upgrades. To create a portable copy, set `POMODORO_DATA_DIR` to a relative folder before launching the EXE.

Example (PowerShell):
```powershell
$env:POMODORO_DATA_DIR = "$PWD\portable_data"; .\PomodoroTimer.exe
```

### Using the Provided Script

You can also run `powershell -File build_exe.ps1` which auto-adds the icon if present.

## Customization
- Change theme colors or emojis in the `THEMES` dictionary.
- Adjust allowed duration ranges in the `LIMITS` dictionary.
- All variable names and logic are kept simple and commented for easy editing.

---

Enjoy your productive sessions! 🍅🫐🍌 
