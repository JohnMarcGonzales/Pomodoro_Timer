import tkinter as tk
from tkinter import messagebox
import winsound

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("🍅 Pomodoro Timer")
        self.pomodoro_count = 0
        self.is_running = False
        self.timer = None
        self.pomodoro_length = 25 * 60  # default 25 mins
        self.short_break = 5 * 60
        self.long_break = 40 * 60
        self.current_time = self.pomodoro_length
        self.state = 'Pomodoro'  # or 'Short Break' or 'Long Break'
        # Counters
        self.pomodoro_done = 0
        self.short_break_done = 0
        self.long_break_done = 0

        # UI
        self.window_width = 340
        self.window_height = 390
        self.center_window(self.window_width, self.window_height)
        self.root.resizable(False, False)
        self.frame = tk.Frame(self.root, bg='#f9f9f9')
        self.frame.pack(fill='both', expand=True)

        self.title_label = tk.Label(self.frame, text="🍅 Pomodoro Timer", font=("Arial", 17, "bold"), bg='#f9f9f9', fg='#ff6347')
        self.title_label.pack(pady=(14, 2))

        self.emoji_label = tk.Label(self.frame, text="🍅", font=("Arial", 38), bg='#f9f9f9')
        self.emoji_label.pack(pady=(0, 0))

        self.timer_label = tk.Label(self.frame, text="⏰ " + self.format_time(self.current_time), font=("Arial Rounded MT Bold", 44, "bold"), bg='#f9f9f9', fg='#222')
        self.timer_label.pack(pady=(0, 2))

        self.state_label = tk.Label(self.frame, text="Pomodoro (Red Tomato)", font=("Arial", 13, "bold"), bg='#f9f9f9', fg='#ff6347')
        self.state_label.pack(pady=(0, 8))

        # Counter bar with rounded look
        self.counter_bar = tk.Frame(self.frame, bg='#fff', bd=0, highlightbackground='#e0e0e0', highlightthickness=1)
        self.counter_bar.pack(pady=(0, 10), padx=18, fill='x')
        self.counter_label = tk.Label(self.counter_bar, text=self.get_counter_text(), font=("Arial", 11, "bold"), bg='#fff', fg='#444', pady=6)
        self.counter_label.pack(fill='x')

        # Separator
        self.separator = tk.Frame(self.frame, height=2, bg='#ececec')
        self.separator.pack(fill='x', padx=18, pady=(0, 10))

        # Button row
        btn_frame = tk.Frame(self.frame, bg='#f9f9f9')
        btn_frame.pack(pady=2)
        self.start_button = tk.Button(btn_frame, text="▶ Start", command=self.start_timer, font=("Arial", 11, "bold"), bg='#ff6347', fg='white', bd=0, padx=14, pady=6, activebackground='#ff826b', relief='flat', cursor='hand2')
        self.start_button.grid(row=0, column=0, padx=7)
        self.pause_button = tk.Button(btn_frame, text="⏸ Pause", command=self.pause_timer, font=("Arial", 11, "bold"), bg='#ffa500', fg='white', bd=0, padx=14, pady=6, activebackground='#ffc04d', relief='flat', cursor='hand2')
        self.pause_button.grid(row=0, column=1, padx=7)
        self.reset_button = tk.Button(btn_frame, text="🔄 Reset", command=self.reset_timer, font=("Arial", 11, "bold"), bg='#e0e0e0', fg='#333', bd=0, padx=14, pady=6, activebackground='#cccccc', relief='flat', cursor='hand2')
        self.reset_button.grid(row=0, column=2, padx=7)
        self.skip_button = tk.Button(btn_frame, text="⏭ Skip", command=self.skip_timer, font=("Arial", 11, "bold"), bg='#4682b4', fg='white', bd=0, padx=14, pady=6, activebackground='#6a9edb', relief='flat', cursor='hand2')
        self.skip_button.grid(row=0, column=3, padx=7)

        # Pomodoro length
        self.length_label = tk.Label(self.frame, text="Pomodoro Length (25-50 min):", font=("Arial", 10), bg='#f9f9f9', fg='#888')
        self.length_label.pack(pady=(12, 0))
        self.length_var = tk.IntVar(value=25)
        self.length_spin = tk.Spinbox(self.frame, from_=25, to=50, textvariable=self.length_var, width=5, font=("Arial", 10), command=self.update_length, justify='center')
        self.length_spin.pack(pady=(0, 10))

        # Short break length
        self.short_label = tk.Label(self.frame, text="Short Break (3-15 min):", font=("Arial", 10), bg='#f9f9f9', fg='#888')
        self.short_label.pack(pady=(0, 0))
        self.short_var = tk.IntVar(value=5)
        self.short_spin = tk.Spinbox(self.frame, from_=3, to=15, textvariable=self.short_var, width=5, font=("Arial", 10), command=self.update_short_length, justify='center')
        self.short_spin.pack(pady=(0, 10))

        # Long break length
        self.long_label = tk.Label(self.frame, text="Long Break (15-60 min):", font=("Arial", 10), bg='#f9f9f9', fg='#888')
        self.long_label.pack(pady=(0, 0))
        self.long_var = tk.IntVar(value=40)
        self.long_spin = tk.Spinbox(self.frame, from_=15, to=60, textvariable=self.long_var, width=5, font=("Arial", 10), command=self.update_long_length, justify='center')
        self.long_spin.pack(pady=(0, 10))

        self.update_theme()

    def get_counter_text(self):
        return f"🍅 {self.pomodoro_done}   🫐 {self.short_break_done}   🍌 {self.long_break_done}"

    def update_counters(self):
        self.counter_label.config(text=self.get_counter_text())

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def update_length(self):
        val = self.length_var.get()
        if 25 <= val <= 50:
            self.pomodoro_length = val * 60
            if self.state == 'Pomodoro':
                self.current_time = self.pomodoro_length
                self.update_timer_label()

    def update_short_length(self):
        val = self.short_var.get()
        if 3 <= val <= 15:
            self.short_break = val * 60
            if self.state == 'Short Break':
                self.current_time = self.short_break
                self.update_timer_label()

    def update_long_length(self):
        val = self.long_var.get()
        if 15 <= val <= 60:
            self.long_break = val * 60
            if self.state == 'Long Break':
                self.current_time = self.long_break
                self.update_timer_label()

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.pause_button.config(text="⏸ Pause", command=self.pause_timer)
            self.run_timer()

    def run_timer(self):
        if self.current_time > 0:
            self.update_timer_label()
            self.current_time -= 1
            self.timer = self.root.after(1000, self.run_timer)
        else:
            self.is_running = False
            self.cycle_state()

    def update_timer_label(self):
        self.timer_label.config(text="⏰ " + self.format_time(self.current_time))

    def reset_timer(self):
        if self.timer:
            self.root.after_cancel(self.timer)
        self.is_running = False
        self.pause_button.config(text="⏸ Pause", command=self.pause_timer)
        if self.state == 'Pomodoro':
            self.current_time = self.pomodoro_length
        elif self.state == 'Short Break':
            self.current_time = self.short_break
        else:
            self.current_time = self.long_break
        self.update_timer_label()

    def skip_timer(self):
        if self.timer:
            self.root.after_cancel(self.timer)
        self.is_running = False
        self.pause_button.config(text="⏸ Pause", command=self.pause_timer)
        self.cycle_state()

    def pause_timer(self):
        if self.is_running:
            if self.timer:
                self.root.after_cancel(self.timer)
            self.is_running = False
            self.pause_button.config(text="▶ Resume", command=self.resume_timer)

    def resume_timer(self):
        if not self.is_running:
            self.is_running = True
            self.pause_button.config(text="⏸ Pause", command=self.pause_timer)
            self.run_timer()

    def cycle_state(self):
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        if self.state == 'Pomodoro':
            self.pomodoro_done += 1
            self.update_counters()
            self.pomodoro_count += 1
            if self.pomodoro_count % 4 == 0:
                self.state = 'Long Break'
                self.current_time = self.long_break
                self.state_label.config(text="Long Break (Banana)")
                self.emoji_label.config(text="🍌")
                self.long_break_done += 1
                self.update_counters()
                self.show_topmost_popup("Long Break!", "Time for a long break! 40 minutes of rest.")
            else:
                self.state = 'Short Break'
                self.current_time = self.short_break
                self.state_label.config(text="Short Break (Blueberry)")
                self.emoji_label.config(text="🫐")
                self.short_break_done += 1
                self.update_counters()
                self.show_topmost_popup("Short Break!", "Time for a short break! 5 minutes of rest.")
        else:
            # After a break, show 'get back to work' popup
            self.state = 'Pomodoro'
            self.current_time = self.pomodoro_length
            self.state_label.config(text="Pomodoro (Red Tomato)")
            self.emoji_label.config(text="🍅")
            if self.pomodoro_count % 4 == 0:
                self.show_topmost_popup("Pomodoro Cycle Restarted!", "Back to work! Start your next Pomodoro.")
            else:
                self.show_topmost_popup("Time to Get back to work!", "Time to Get back to work!")
        self.update_theme()
        self.update_timer_label()

    def show_topmost_popup(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.withdraw()
        popup.attributes('-topmost', True)
        popup.after(0, lambda: popup.focus_force())
        self.root.after(10, lambda: messagebox.showinfo(title, message, parent=popup))
        popup.after(100, popup.destroy)

    def update_theme(self):
        if self.state == 'Pomodoro':
            self.frame.config(bg='#f9f9f9')
            self.title_label.config(bg='#f9f9f9', fg='#ff6347')
            self.timer_label.config(bg='#f9f9f9', fg='#222')
            self.state_label.config(bg='#f9f9f9', fg='#ff6347')
            self.length_label.config(bg='#f9f9f9', fg='#888')
            self.counter_bar.config(bg='#fff', highlightbackground='#e0e0e0')
            self.counter_label.config(bg='#fff', fg='#444')
        elif self.state == 'Short Break':
            self.frame.config(bg='#f9f9f9')
            self.title_label.config(bg='#f9f9f9', fg='#4682b4')
            self.timer_label.config(bg='#f9f9f9', fg='#222')
            self.state_label.config(bg='#f9f9f9', fg='#4682b4')
            self.length_label.config(bg='#f9f9f9', fg='#888')
            self.counter_bar.config(bg='#fff', highlightbackground='#b3d1f7')
            self.counter_label.config(bg='#fff', fg='#4682b4')
        else:  # Long Break
            self.frame.config(bg='#fffbe7')  # light yellow
            self.title_label.config(bg='#fffbe7', fg='#e6b800')
            self.timer_label.config(bg='#fffbe7', fg='#222')
            self.state_label.config(bg='#fffbe7', fg='#e6b800')
            self.length_label.config(bg='#fffbe7', fg='#b3a76d')
            self.counter_bar.config(bg='#fff', highlightbackground='#ffe066')
            self.counter_label.config(bg='#fff', fg='#e6b800')

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop() 