# Pomodoro Timer 🍅🫐

A simple, themed Pomodoro timer with customizable intervals, built in Python with a Red Tomato (work) and Blueberry (break) theme.

## Features
- Pomodoro (work) timer: 25–50 minutes (user adjustable)
- Short break: 5 minutes (blueberry theme)
- Long break: 40 minutes after 4 pomodoros
- Automatic cycle management
- Simple, colorful GUI

## How to Run

1. **Install Python 3** (if not already installed)
2. Open a terminal in this project folder.
3. Run:
   ```bash
   python pomodoro.py
   ```

## How to Build a Windows Executable

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller --onefile --windowed pomodoro.py
   ```
3. The `.exe` will be in the `dist/` folder.

---
Enjoy your focused work sessions! 🍅🫐 
