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

## How to Upload to GitHub

1. [Create a new repository on GitHub](https://github.com/new)
2. In this project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Pomodoro Timer"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub info.

---
Enjoy your focused work sessions! 🍅🫐 