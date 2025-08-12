import tkinter as tk
from tkinter import messagebox
import winsound
import json
import os
import datetime
import platform
import sys
try:
    import threading
    import itertools
except ImportError:
    pass
try:
    from win10toast import ToastNotifier  # Windows toast notifications
except ImportError:  # optional
    ToastNotifier = None
try:
    import pystray  # system tray icon support
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

# --- Constants for themes and limits ---
LIGHT_THEMES = {
    'pomodoro': {'color': '#ff6347', 'emoji': '🍅', 'label': 'Pomodoro (Tomato)'},
    'short': {'color': '#4682b4', 'emoji': '🫐', 'label': 'Short Break (Blueberry)'},
    'long': {'color': '#e6b800', 'emoji': '🍌', 'label': 'Long Break (Banana)'}
}
DARK_THEMES = {
    'pomodoro': {'color': '#ff826b', 'emoji': '🍅', 'label': 'Pomodoro (Tomato)'},
    'short': {'color': '#6a9edb', 'emoji': '🫐', 'label': 'Short Break (Blueberry)'},
    'long': {'color': '#ffd54f', 'emoji': '🍌', 'label': 'Long Break (Banana)'}
}
LIMITS = {
    'pomodoro': (25, 50),
    'short': (5, 15),
    'long': (40, 120)
}

# Data directory resolution (env override -> AppData -> frozen exe dir -> home fallback)
CUSTOM_DATA_DIR = os.getenv('POMODORO_DATA_DIR')
if CUSTOM_DATA_DIR:
    DATA_DIR = CUSTOM_DATA_DIR
else:
    appdata = os.getenv('APPDATA')
    if appdata:
        DATA_DIR = os.path.join(appdata, 'PomodoroTimer')
    elif getattr(sys, 'frozen', False):  # running from PyInstaller bundle
        DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'data')
    else:
        DATA_DIR = os.path.join(os.path.expanduser('~'), '.pomodoro_timer')
os.makedirs(DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title('🍅 Pomodoro Timer')
        self.root.geometry('520x680')
        self.root.minsize(480, 640)
        self.root.resizable(True, True)
        self.center_window()
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)

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
        self.long_break_interval = 4  # customizable
        self.auto_start = False
        self.muted = False
        self.sound_choice = 'SystemAsterisk'
        self.dark_mode = False
        self.daily_counts = {'date': self.today_str(), 'pomodoro': 0, 'short': 0, 'long': 0}
        self.tray_icon = None
        self.notifier = None
        self.window_hidden = False
        self.tray_thread = None

        # --- History and counters ---
        self.history = self.load_history()
        self.load_settings()
        self.counters = {'pomodoro': 0, 'short': 0, 'long': 0}

        # --- UI ---
        self.build_ui()
        self.setup_notifications()
        self.update_ui()

    # --- UI Construction ---
    def build_ui(self):
        # Root frame
        self.frame = tk.Frame(self.root, bg=self.bg_color())
        self.frame.pack(fill='both', expand=True)
        # Header
        self.title_label = tk.Label(self.frame, text='🍅 Pomodoro Timer', font=('Arial', 22, 'bold'), bg=self.bg_color())
        self.title_label.pack(pady=(18, 6))
        self.emoji_label = tk.Label(self.frame, text=self.current_themes()['pomodoro']['emoji'], font=('Arial', 54), bg=self.bg_color())
        self.emoji_label.pack(pady=(0, 6))
        self.timer_label = tk.Label(self.frame, text=self.format_time(self.time_left), font=('Arial Rounded MT Bold', 54, 'bold'), bg=self.bg_color())
        self.timer_label.pack(pady=(0, 8))
        self.state_label = tk.Label(self.frame, text=self.current_themes()['pomodoro']['label'], font=('Arial', 15, 'bold'), bg=self.bg_color())
        self.state_label.pack(pady=(0, 14))
        # Counters
        self.counter_bar = tk.Frame(self.frame, bg=self.panel_bg(), bd=0, highlightbackground='#444' if self.dark_mode else '#e0e0e0', highlightthickness=1)
        self.counter_bar.pack(pady=(0, 16), fill='x')
        self.counter_label = tk.Label(self.counter_bar, text=self.get_counter_text(), font=('Arial', 13, 'bold'), bg=self.panel_bg(), fg=self.fg_color(), pady=10)
        self.counter_label.pack(fill='x')
        # History cumulative label
        self.history_label = tk.Label(self.frame, text=self.get_history_text(), font=('Arial', 10), bg=self.bg_color(), fg=self.secondary_text_color(), justify='center')
        self.history_label.pack(pady=(0, 10))
        # Control buttons
        btn_frame = tk.Frame(self.frame, bg=self.bg_color())
        btn_frame.pack(pady=6)
        self.start_btn = tk.Button(btn_frame, text='▶ Start', command=self.start_timer, font=('Arial', 13, 'bold'), bg='#ff6347', fg='white', bd=0, padx=18, pady=8)
        self.start_btn.grid(row=0, column=0, padx=10)
        self.pause_btn = tk.Button(btn_frame, text='⏸ Pause', command=self.pause_timer, font=('Arial', 13, 'bold'), bg='#ffa500', fg='white', bd=0, padx=18, pady=8)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.reset_btn = tk.Button(btn_frame, text='🔄 Reset', command=self.reset_timer, font=('Arial', 13, 'bold'), bg='#e0e0e0', fg='#333', bd=0, padx=18, pady=8)
        self.reset_btn.grid(row=0, column=2, padx=10)
        self.skip_btn = tk.Button(btn_frame, text='⏭ Skip', command=self.skip_timer, font=('Arial', 13, 'bold'), bg='#4682b4', fg='white', bd=0, padx=18, pady=8)
        self.skip_btn.grid(row=0, column=3, padx=10)
        self.exit_btn = tk.Button(btn_frame, text='❌ Exit', command=self.exit_app, font=('Arial', 13, 'bold'), bg='#d9534f', fg='white', bd=0, padx=18, pady=8)
        self.exit_btn.grid(row=0, column=4, padx=10)
        # Duration controls
        self.length_frame = tk.Frame(self.frame, bg=self.bg_color())
        self.length_frame.pack(pady=(18, 0))
        self.add_duration_control('Pomodoro', 'pomodoro', 0)
        self.add_duration_control('Short Break', 'short', 1)
        self.add_duration_control('Long Break', 'long', 2)
        # Settings panel
        settings_frame = tk.Frame(self.frame, bg=self.bg_color())
        settings_frame.pack(pady=(10, 0), fill='x')
        tk.Label(settings_frame, text='Long break every', font=('Arial', 11), bg=self.bg_color(), fg=self.secondary_text_color()).grid(row=0, column=0, sticky='e', padx=4, pady=4)
        self.long_break_var = tk.IntVar(value=self.long_break_interval)
        tk.Spinbox(settings_frame, from_=2, to=12, width=4, textvariable=self.long_break_var, command=self.update_long_break_interval, justify='center').grid(row=0, column=1, padx=4)
        tk.Label(settings_frame, text='pomodoros', font=('Arial', 11), bg=self.bg_color(), fg=self.secondary_text_color()).grid(row=0, column=2, sticky='w')
        self.auto_start_var = tk.BooleanVar(value=self.auto_start)
        tk.Checkbutton(settings_frame, text='Auto-start next', variable=self.auto_start_var, command=self.toggle_auto_start, bg=self.bg_color(), fg=self.fg_color(), selectcolor=self.panel_bg()).grid(row=0, column=3, padx=8)
        self.mute_var = tk.BooleanVar(value=self.muted)
        tk.Checkbutton(settings_frame, text='Mute', variable=self.mute_var, command=self.toggle_mute, bg=self.bg_color(), fg=self.fg_color(), selectcolor=self.panel_bg()).grid(row=0, column=4, padx=8)
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        tk.Checkbutton(settings_frame, text='Dark', variable=self.dark_mode_var, command=self.toggle_dark_mode, bg=self.bg_color(), fg=self.fg_color(), selectcolor=self.panel_bg()).grid(row=0, column=5, padx=8)
        tk.Label(settings_frame, text='Sound', font=('Arial', 11), bg=self.bg_color(), fg=self.secondary_text_color()).grid(row=1, column=0, sticky='e', padx=4, pady=4)
        self.sound_var = tk.StringVar(value=self.sound_choice)
        sound_options = ['SystemAsterisk', 'SystemExclamation', 'SystemHand', 'SystemQuestion']
        tk.OptionMenu(settings_frame, self.sound_var, *sound_options, command=lambda _: self.update_sound_choice()).grid(row=1, column=1, columnspan=2, sticky='w', padx=4)
        # Progress
        self.progress_canvas = tk.Canvas(self.frame, width=220, height=220, bg=self.bg_color(), highlightthickness=0)
        self.progress_canvas.pack(pady=14)
        self.progress_arc = None
        # Daily counts
        self.daily_label = tk.Label(self.frame, text=self.get_daily_text(), font=('Arial', 10, 'bold'), bg=self.bg_color(), fg=self.secondary_text_color())
        self.daily_label.pack(pady=(4, 6))
        # Shortcuts
        for seq, func in [('<space>', self.pause_timer), ('<s>', self.start_timer), ('<S>', self.start_timer), ('<r>', self.reset_timer), ('<R>', self.reset_timer), ('<k>', self.skip_timer), ('<K>', self.skip_timer), ('<Escape>', self.exit_app)]:
            self.root.bind(seq, lambda e, f=func: f())
        # Minimize / restore
        self.root.bind('<Unmap>', self.on_minimize)
        self.root.bind('<Map>', self.on_restore)

    def add_duration_control(self, label, key, row):
        minv, maxv = LIMITS[key]
        tk.Label(self.length_frame, text=f'{label} ({minv}-{maxv} min):', font=('Arial', 12), bg=self.bg_color(), fg=self.secondary_text_color()).grid(row=row, column=0, sticky='e', padx=6, pady=4)
        var = tk.IntVar(value=self.durations[key] // 60)
        spin = tk.Spinbox(self.length_frame, from_=minv, to=maxv, textvariable=var, width=6, font=('Arial', 12), command=lambda k=key, v=var: self.set_duration(k, v), justify='center')
        spin.grid(row=row, column=1, padx=6, pady=4)
        setattr(self, f'{key}_var', var)

    # --- Notification / Tray Setup ---
    def setup_notifications(self):
        if platform.system() == 'Windows' and ToastNotifier:
            try:
                self.notifier = ToastNotifier()
            except Exception:
                self.notifier = None

    def show_notification(self, title: str, message: str):
        if self.notifier:
            try:
                self.notifier.show_toast(title, message, duration=5, threaded=True)
            except Exception:
                pass

    def create_tray_icon(self):
        if not (pystray and Image and ImageDraw):
            return
        if self.tray_icon:
            return
        # Create simple circular icon
        img = Image.new('RGB', (64, 64), color=(30, 30, 30) if self.dark_mode else (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 56, 56), fill=(255, 99, 71))
        menu = pystray.Menu(
            pystray.MenuItem('Show', self.restore_from_tray),
            pystray.MenuItem('Start', lambda: self.safe_ui_call(self.start_timer)),
            pystray.MenuItem('Pause/Resume', lambda: self.safe_ui_call(self.pause_timer)),
            pystray.MenuItem('Skip', lambda: self.safe_ui_call(self.skip_timer)),
            pystray.MenuItem('Quit', lambda: self.safe_ui_call(self.exit_app))
        )
        self.tray_icon = pystray.Icon('pomodoro', img, 'Pomodoro Timer', menu)
        def run_icon():
            try:
                self.tray_icon.run()
            except Exception:
                pass
        self.tray_thread = threading.Thread(target=run_icon, daemon=True)
        self.tray_thread.start()

    def restore_from_tray(self, *args):
        self.safe_ui_call(self.show_window)
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None

    def safe_ui_call(self, fn):
        try:
            self.root.after(0, fn)
        except Exception:
            pass

    def show_window(self):
        if self.window_hidden:
            self.root.deiconify()
            self.window_hidden = False

    # --- Timer Logic ---
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.run_timer()

    def run_timer(self):
        if self.is_running and not self.is_paused:
            if self.time_left > 0:
                self.time_left -= 1
                self.update_ui()
                self.timer = self.root.after(1000, self.run_timer)
            else:
                self.update_ui()  # show 00:00
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
        # Skip without counting completion
        if self.timer:
            self.root.after_cancel(self.timer)
        self.is_running = False
        self.is_paused = False
        self.transition_state()  # no counter increment
        self.time_left = self.durations[self.state]
        self.update_ui()

    def handle_cycle_end(self):
        self.play_sound()
        self.counters[self.state] += 1
        self.daily_increment(self.state)
        self.flush_session_counters()  # persist
        self.show_popup(f'{self.current_themes()[self.state]["label"]} Ended!', 'Time for the next step!')
        self.show_notification('Session Complete', f'{self.current_themes()[self.state]["label"]} finished')
        self.transition_state()
        self.time_left = self.durations[self.state]
        self.update_ui()
        if self.auto_start:
            self.start_timer()

    def transition_state(self):
        if self.state == 'pomodoro':
            self.pomodoro_count += 1
            if self.pomodoro_count % self.long_break_interval == 0:
                self.state = 'long'
            else:
                self.state = 'short'
        else:
            self.state = 'pomodoro'

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
        self.check_daily_reset()
        theme = self.current_themes()[self.state]
        # Colors
        self.frame.config(bg=self.bg_color())
        self.timer_label.config(text=self.format_time(self.time_left), bg=self.bg_color(), fg=self.fg_color())
        self.emoji_label.config(text=theme['emoji'], bg=self.bg_color())
        self.state_label.config(text=theme['label'], fg=theme['color'], bg=self.bg_color())
        self.title_label.config(fg=theme['color'], bg=self.bg_color())
        self.counter_bar.config(bg=self.panel_bg(), highlightbackground='#444' if self.dark_mode else '#e0e0e0')
        self.counter_label.config(text=self.get_counter_text(), bg=self.panel_bg(), fg=self.fg_color())
        self.history_label.config(text=self.get_history_text(), bg=self.bg_color(), fg=self.secondary_text_color())
        self.daily_label.config(text=self.get_daily_text(), bg=self.bg_color(), fg=self.secondary_text_color())
        # Buttons theme adaptation minimal (could be expanded)
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
        self.draw_progress()

    # --- Utility Functions ---
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f'{mins:02d}:{secs:02d}'

    def get_counter_text(self):
        return f"🍅 {self.counters['pomodoro']}   🫐 {self.counters['short']}   🍌 {self.counters['long']}"

    def get_history_text(self):
        return f"Cumulative: P {self.history.get('pomodoro', 0)}, S {self.history.get('short', 0)}, L {self.history.get('long', 0)}"

    def get_daily_text(self):
        return f"Today: P {self.daily_counts.get('pomodoro',0)}, S {self.daily_counts.get('short',0)}, L {self.daily_counts.get('long',0)}"

    def show_popup(self, title, message):
        try:
            popup = tk.Toplevel(self.root)
            popup.withdraw()
            popup.attributes('-topmost', True)
            popup.after(0, lambda: popup.focus_force())
            messagebox.showinfo(title, message, parent=popup)
            popup.destroy()
        except tk.TclError:
            pass

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
            try:
                with open(HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    # backward compatibility
                    return {k: int(data.get(k, 0)) for k in ('pomodoro','short','long')}
            except (ValueError, OSError, json.JSONDecodeError):
                return {'pomodoro': 0, 'short': 0, 'long': 0}
        return {'pomodoro': 0, 'short': 0, 'long': 0}

    def flush_session_counters(self):
        # add current session counters to history and reset session counters
        modified = False
        for k in self.counters:
            if self.counters[k]:
                self.history[k] = self.history.get(k, 0) + self.counters[k]
                self.counters[k] = 0
                modified = True
        if modified:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f)

    def daily_increment(self, key):
        self.check_daily_reset()
        self.daily_counts[key] = self.daily_counts.get(key, 0) + 1
        self.save_settings()  # persist daily counts in settings

    def check_daily_reset(self):
        today = self.today_str()
        if self.daily_counts.get('date') != today:
            self.daily_counts = {'date': today, 'pomodoro': 0, 'short': 0, 'long': 0}
            self.save_settings()

    def save_history(self):
        self.flush_session_counters()

    def exit_app(self):
        self.flush_session_counters()
        self.save_settings()
        self.root.destroy()

    # --- Settings persistence ---
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                self.long_break_interval = int(data.get('long_break_interval', self.long_break_interval))
                self.auto_start = bool(data.get('auto_start', self.auto_start))
                self.muted = bool(data.get('muted', self.muted))
                self.sound_choice = data.get('sound_choice', self.sound_choice)
                self.dark_mode = bool(data.get('dark_mode', self.dark_mode))
                self.daily_counts = data.get('daily_counts', self.daily_counts)
            except (ValueError, OSError, json.JSONDecodeError):
                pass

    def save_settings(self):
        data = {
            'long_break_interval': self.long_break_interval,
            'auto_start': self.auto_start,
            'muted': self.muted,
            'sound_choice': self.sound_choice,
            'dark_mode': self.dark_mode,
            'daily_counts': self.daily_counts
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f)
        except OSError:
            pass

    # --- Utility additions ---
    def today_str(self):
        return datetime.date.today().isoformat()

    def update_long_break_interval(self):
        val = self.long_break_var.get()
        if 2 <= val <= 12:
            self.long_break_interval = val
            self.save_settings()

    def toggle_auto_start(self):
        self.auto_start = self.auto_start_var.get()
        self.save_settings()

    def toggle_mute(self):
        self.muted = self.mute_var.get()
        self.save_settings()

    def toggle_dark_mode(self):
        self.dark_mode = self.dark_mode_var.get()
        self.update_ui()
        self.save_settings()

    def update_sound_choice(self):
        self.sound_choice = self.sound_var.get()
        self.save_settings()

    def current_themes(self):
        return DARK_THEMES if self.dark_mode else LIGHT_THEMES

    def bg_color(self):
        return '#1e1e1e' if self.dark_mode else '#f9f9f9'

    def panel_bg(self):
        return '#2b2b2b' if self.dark_mode else '#ffffff'

    def fg_color(self):
        return '#f0f0f0' if self.dark_mode else '#222'

    def secondary_text_color(self):
        return '#aaaaaa' if self.dark_mode else '#888'

    def play_sound(self):
        if self.muted:
            return
        try:
            if platform.system() == 'Windows':
                winsound.PlaySound(self.sound_choice, winsound.SND_ALIAS)
            else:
                print('\a')
        except Exception:
            pass

    # Progress ring drawing
    def draw_progress(self):
        self.progress_canvas.delete('all')
        total = self.durations[self.state]
        remaining = self.time_left
        if total <= 0:
            return
        frac = 1 - (remaining / total)
        start_angle = -90
        extent = frac * 360
        # Background circle
        self.progress_canvas.create_oval(10, 10, 210, 210, outline=self.secondary_text_color(), width=10)
        # Progress arc
        color = self.current_themes()[self.state]['color']
        self.progress_canvas.create_arc(10, 10, 210, 210, start=start_angle, extent=extent, style='arc', outline=color, width=10)

    # Minimize/restore events (placeholder tray behavior)
    def on_minimize(self, event):
        if self.root.state() == 'iconic':
            # Hide completely and create tray icon
            self.window_hidden = True
            self.root.withdraw()
            self.create_tray_icon()

    def on_restore(self, event):
        if not self.window_hidden:
            return
        self.show_window()

if __name__ == '__main__':
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop() 