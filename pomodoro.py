import tkinter as tk
from tkinter import messagebox
import winsound
import json
import os

# --- Constants for themes and limits ---
THEMES = {
    'pomodoro': {'color': '#ff6347', 'emoji': '🍅', 'label': 'Pomodoro (Tomato)'},
    'short': {'color': '#4682b4', 'emoji': '🫐', 'label': 'Short Break (Blueberry)'},
    'long': {'color': '#e6b800', 'emoji': '🍌', 'label': 'Long Break (Banana)'}
}
LIMITS = {
    'pomodoro': (25, 50),
    'short': (5, 15),
    'long': (40, 120)
}
HISTORY_FILE = 'history.json'

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title('🍅 Pomodoro Timer')
        self.root.geometry('480x600')
        self.root.minsize(420, 540)
        self.root.resizable(True, True)
        self.center_window()
        self.root.protocol('WM_DELETE_WINDOW', self.save_history)

        # --- Timer state ---
        self.state = 'pomodoro'  # 'pomodoro', 'short', 'long'
        self.is_running = False
        self.is_paused = False
        self.timer = None
        self.pomodoro_count = 0
        self.time_left = 25 * 60
        self.durations = {
            'pomodoro': 25 * 60,
            'short': 5 * 60,
            'long': 40 * 60
        }
        # --- History and counters ---
        self.history = self.load_history()
        self.counters = {'pomodoro': 0, 'short': 0, 'long': 0}

        # --- UI ---
        self.build_ui()
        self.update_ui()

    # --- UI Construction ---
    def build_ui(self):
        self.frame = tk.Frame(self.root, bg='#f9f9f9')
        self.frame.pack(fill='both', expand=True)

        # Title and emoji
        self.title_label = tk.Label(self.frame, text='🍅 Pomodoro Timer', font=('Arial', 22, 'bold'), bg='#f9f9f9')
        self.title_label.pack(pady=(18, 6))
        self.emoji_label = tk.Label(self.frame, text=THEMES['pomodoro']['emoji'], font=('Arial', 54), bg='#f9f9f9')
        self.emoji_label.pack(pady=(0, 6))
        self.timer_label = tk.Label(self.frame, text=self.format_time(self.time_left), font=('Arial Rounded MT Bold', 54, 'bold'), bg='#f9f9f9')
        self.timer_label.pack(pady=(0, 8))
        self.state_label = tk.Label(self.frame, text=THEMES['pomodoro']['label'], font=('Arial', 15, 'bold'), bg='#f9f9f9')
        self.state_label.pack(pady=(0, 14))

        # Counters
        self.counter_bar = tk.Frame(self.frame, bg='#fff', bd=0, highlightbackground='#e0e0e0', highlightthickness=1)
        self.counter_bar.pack(pady=(0, 16), fill='x')
        self.counter_label = tk.Label(self.counter_bar, text=self.get_counter_text(), font=('Arial', 13, 'bold'), bg='#fff', pady=10)
        self.counter_label.pack(fill='x')

        # History
        self.history_label = tk.Label(self.frame, text=self.get_history_text(), font=('Arial', 10), bg='#f9f9f9', fg='#888', justify='center')
        self.history_label.pack(pady=(0, 10))

        # Controls
        btn_frame = tk.Frame(self.frame, bg='#f9f9f9')
        btn_frame.pack(pady=6)
        self.start_btn = tk.Button(btn_frame, text='▶ Start', command=self.start_timer, font=('Arial', 13, 'bold'), bg='#ff6347', fg='white', bd=0, padx=18, pady=8, activebackground='#ff826b', relief='flat', cursor='hand2')
        self.start_btn.grid(row=0, column=0, padx=10)
        self.pause_btn = tk.Button(btn_frame, text='⏸ Pause', command=self.pause_timer, font=('Arial', 13, 'bold'), bg='#ffa500', fg='white', bd=0, padx=18, pady=8, activebackground='#ffc04d', relief='flat', cursor='hand2')
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.reset_btn = tk.Button(btn_frame, text='🔄 Reset', command=self.reset_timer, font=('Arial', 13, 'bold'), bg='#e0e0e0', fg='#333', bd=0, padx=18, pady=8, activebackground='#cccccc', relief='flat', cursor='hand2')
        self.reset_btn.grid(row=0, column=2, padx=10)
        self.skip_btn = tk.Button(btn_frame, text='⏭ Skip', command=self.skip_timer, font=('Arial', 13, 'bold'), bg='#4682b4', fg='white', bd=0, padx=18, pady=8, activebackground='#6a9edb', relief='flat', cursor='hand2')
        self.skip_btn.grid(row=0, column=3, padx=10)
        # Exit button
        self.exit_btn = tk.Button(btn_frame, text='❌ Exit', command=self.exit_app, font=('Arial', 13, 'bold'), bg='#d9534f', fg='white', bd=0, padx=18, pady=8, activebackground='#e57373', relief='flat', cursor='hand2')
        self.exit_btn.grid(row=0, column=4, padx=10)

        # Duration controls
        self.length_frame = tk.Frame(self.frame, bg='#f9f9f9')
        self.length_frame.pack(pady=(18, 0))
        self.add_duration_control('Pomodoro', 'pomodoro', 0)
        self.add_duration_control('Short Break', 'short', 1)
        self.add_duration_control('Long Break', 'long', 2)

    def add_duration_control(self, label, key, row):
        minv, maxv = LIMITS[key]
        tk.Label(self.length_frame, text=f'{label} ({minv}-{maxv} min):', font=('Arial', 12), bg='#f9f9f9', fg='#888').grid(row=row, column=0, sticky='e', padx=6, pady=4)
        var = tk.IntVar(value=self.durations[key] // 60)
        spin = tk.Spinbox(self.length_frame, from_=minv, to=maxv, textvariable=var, width=6, font=('Arial', 12), command=lambda k=key, v=var: self.set_duration(k, v), justify='center')
        spin.grid(row=row, column=1, padx=6, pady=4)
        setattr(self, f'{key}_var', var)

    # --- Timer Logic ---
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.run_timer()

    def run_timer(self):
        if self.is_running and not self.is_paused:
            if self.time_left > 0:
                self.update_ui()
                self.time_left -= 1
                self.timer = self.root.after(1000, self.run_timer)
            else:
                self.is_running = False
                self.handle_cycle_end()

    def pause_timer(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            if not self.is_paused:
                self.run_timer()
            self.update_ui()

    def reset_timer(self):
        if self.timer:
            self.root.after_cancel(self.timer)
        self.is_running = False
        self.is_paused = False
        self.time_left = self.durations[self.state]
        self.update_ui()

    def skip_timer(self):
        if self.timer:
            self.root.after_cancel(self.timer)
        self.is_running = False
        self.is_paused = False
        self.handle_cycle_end()

    def handle_cycle_end(self):
        winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
        self.counters[self.state] += 1
        self.save_history()
        self.show_popup(f'{THEMES[self.state]["label"]} Ended!', f'Time for the next step!')
        if self.state == 'pomodoro':
            self.pomodoro_count += 1
            if self.pomodoro_count % 4 == 0:
                self.state = 'long'
            else:
                self.state = 'short'
        else:
            self.state = 'pomodoro'
        self.time_left = self.durations[self.state]
        self.update_ui()

    # --- Duration and UI Updates ---
    def set_duration(self, key, var):
        val = var.get()
        minv, maxv = LIMITS[key]
        if minv <= val <= maxv:
            self.durations[key] = val * 60
            if self.state == key:
                self.time_left = self.durations[key]
                self.update_ui()

    def update_ui(self):
        theme = THEMES[self.state]
        self.emoji_label.config(text=theme['emoji'])
        self.timer_label.config(text=self.format_time(self.time_left))
        self.state_label.config(text=theme['label'], fg=theme['color'])
        self.title_label.config(fg=theme['color'])
        self.counter_label.config(text=self.get_counter_text())
        self.history_label.config(text=self.get_history_text())
        # Button states
        if self.is_running and not self.is_paused:
            self.start_btn.config(state='disabled')
            self.pause_btn.config(text='⏸ Pause', state='normal')
        elif self.is_running and self.is_paused:
            self.start_btn.config(state='disabled')
            self.pause_btn.config(text='▶ Resume', state='normal')
        else:
            self.start_btn.config(state='normal')
            self.pause_btn.config(text='⏸ Pause', state='disabled')

    # --- Utility Functions ---
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f'{mins:02d}:{secs:02d}'

    def get_counter_text(self):
        return f"🍅 {self.counters['pomodoro']}   🫐 {self.counters['short']}   🍌 {self.counters['long']}"

    def get_history_text(self):
        return f"History: Pomodoros: {self.history.get('pomodoro', 0)}, Short: {self.history.get('short', 0)}, Long: {self.history.get('long', 0)}"

    def show_popup(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.withdraw()
        popup.attributes('-topmost', True)
        popup.after(0, lambda: popup.focus_force())
        messagebox.showinfo(title, message, parent=popup)
        popup.destroy()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.root.geometry(f'+{x}+{y}')

    # --- History Persistence ---
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return {'pomodoro': 0, 'short': 0, 'long': 0}

    def save_history(self):
        for k in self.counters:
            self.history[k] = self.history.get(k, 0) + self.counters[k]
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f)

    def exit_app(self):
        self.save_history()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop() 