# -*- coding: utf-8 -*-
import sys, time, threading, tkinter as tk

try:
    import keyboard
except ImportError:
    sys.exit(1)

# winsound есть только на Windows; на всякий случай оборачиваем
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

PASSWORD = "123"
MAX_ATTEMPTS = 3
BLOCKED = ["left windows", "right windows", "alt+tab", "alt+f4",
           "ctrl+esc", "alt+esc", "ctrl+shift+esc"]


def block_keys():
    for k in BLOCKED:
        try:
            keyboard.block_key(k)
        except Exception:
            pass


def unblock_keys():
    for k in BLOCKED:
        try:
            keyboard.unblock_key(k)
        except Exception:
            pass
    try:
        keyboard.unhook_all()
    except Exception:
        pass


# ----------------------------- ЗВУКИ -----------------------------

def _beep_seq(seq, gap=0.0):
    """seq — список (freq, dur_ms). freq=0 -> пауза."""
    if not HAS_SOUND:
        return
    for freq, dur in seq:
        try:
            if freq <= 0:
                time.sleep(dur / 1000.0)
            else:
                winsound.Beep(int(freq), int(dur))
        except Exception:
            pass
        if gap:
            time.sleep(gap)


def sound_startup():
    """Зловещая «сирена» при старте — в отдельном потоке."""
    def _run():
        # низкий гул -> высокий писк -> повтор
        for _ in range(2):
            _beep_seq([(180, 220), (220, 180), (260, 160),
                       (400, 120), (700, 90), (1000, 120)])
            time.sleep(0.15)
    threading.Thread(target=_run, daemon=True).start()


def sound_wrong():
    """Короткий «отказ» при неверном пароле."""
    threading.Thread(
        target=lambda: _beep_seq([(300, 120), (200, 180)]),
        daemon=True,
    ).start()


def sound_correct():
    """Победный аккорд при верном пароле."""
    threading.Thread(
        target=lambda: _beep_seq(
            [(523, 90), (659, 90), (784, 90), (1046, 220)]
        ),
        daemon=True,
    ).start()


def sound_reboot_tick():
    """Тихий клик в фейковом ребуте (вызывается по шагу)."""
    if HAS_SOUND:
        try:
            winsound.Beep(900, 20)
        except Exception:
            pass


def sound_final_joke():
    """Смешной «неровный» мотив в конце шутки."""
    threading.Thread(
        target=lambda: _beep_seq(
            [(880, 80), (660, 80), (880, 80), (990, 140)]
        ),
        daemon=True,
    ).start()


# ----------------------------- ASCII -----------------------------

ASCII = r"""
 #####  #   # ##### ##### #####  #   #  ###   ####  #   #
#      #   # #   # #   # #     #   # #   # #     #  #
#      ##### ##### ##### ####  ##### ##### #     ####
#      #   # #   # #   # #     #   # #   # #     #  #
 #####  #   # ##### ##### #####  #   # #   #  ####  #   #
"""


class Locker:
    def __init__(self):
        self.root = tk.Tk()

        # --- Полноэкранное окно без рамки и кнопок ---
        # ВАЖНО: overrideredirect(True) и attributes("-fullscreen", True)
        # одновременно нельзя — Tkinter выдаёт TclError.
        # Поэтому делаем вручную через geometry().
        self.root.overrideredirect(True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        self.text = tk.Text(self.root, bg="black", fg="#ff3333",
                            font=("Consolas", 14), bd=0, highlightthickness=0)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert(tk.END, ASCII + "\n")
        self.text.insert(tk.END, "ALL YOUR FILES ARE ENCRYPTED WITH AES-256\n")
        self.text.insert(tk.END, "(This is a joke. Nothing is encrypted.)\n\n")
        self.text.insert(tk.END, "Send 0.5 BTC to: 1CyberHackFakeAddrXXXX\n\n")
        self.text.insert(tk.END, "3 WRONG PASSWORDS = SYSTEM REBOOT\n")
        self.text.insert(tk.END, "(Also a joke.)\n\n")
        self.text.insert(tk.END, "Enter password (digits only): ")
        self.text.configure(state="disabled")

        self.entry = tk.Entry(self.root, bg="black", fg="lime",
                              font=("Consolas", 14), insertbackground="lime",
                              bd=0, highlightthickness=0)
        self.entry.pack(fill=tk.X, padx=20, pady=10)
        self.entry.focus_force()

        self.attempts = 0
        self.stop_flag = False
        self.sector = 0
        self.progress_label = tk.Label(self.root, bg="black", fg="lime",
                                       font=("Consolas", 12), anchor="w")
        self.progress_label.pack(fill=tk.X, padx=20, pady=5)

        self.entry.bind("<Return>", self.check_password)

        threading.Thread(target=self.progress_loop, daemon=True).start()

    # --------- прогресс ---------
    def progress_loop(self):
        while not self.stop_flag:
            self.sector += 1
            try:
                self.progress_label.config(
                    text=f"Encrypting sector {self.sector}..."
                )
            except tk.TclError:
                return
            time.sleep(0.1)

    # --------- проверка пароля ---------
    def check_password(self, event=None):
        pwd = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not pwd.isdigit():
            sound_wrong()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\nOnly digits allowed.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            return

        if pwd == PASSWORD:
            self.stop_flag = True
            sound_correct()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\n\nACCESS GRANTED. IT WAS A JOKE.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            unblock_keys()
            self.root.after(1500, self.root.destroy)
            return

        self.attempts += 1
        left = MAX_ATTEMPTS - self.attempts

        if self.attempts >= MAX_ATTEMPTS:
            self.stop_flag = True
            unblock_keys()
            self.fake_reboot()
            return

        sound_wrong()
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"\nWrong. {left} attempts left.\n")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

    # --------- фейковый ребут ---------
    def fake_reboot(self):
        self.progress_label.config(text="SYSTEM IS REBOOTING...")
        self.text.configure(state="normal")
        for i in range(41):
            sound_reboot_tick()
            filled = i * 40 // 40
            bar = "#" * filled + "-" * (40 - filled)
            self.text.delete("end-2l", "end-1l")
            self.text.insert(tk.END, f"\n[{bar}] {i * 100 // 40}%\n")
            self.text.see(tk.END)
            self.root.update()
            time.sleep(0.05)
        self.text.insert(tk.END, "\nJUST KIDDING. NO REBOOT. :)\n")
        sound_final_joke()
        self.root.after(1500, self.root.destroy)

    # --------- запуск ---------
    def run(self):
        block_keys()
        sound_startup()
        self.root.mainloop()


if __name__ == "__main__":
    try:
        Locker().run()
    except KeyboardInterrupt:
        unblock_keys()
        sys.exit(0)
    finally:
        unblock_keys()
