# -*- coding: utf-8 -*-
import sys, os, base64, tempfile, time, threading, random, tkinter as tk

try:
    import keyboard
except ImportError:
    sys.exit(1)

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

PASSWORD = "123"
MAX_ATTEMPTS = 3
BLOCKED = ["left windows", "right windows", "alt+tab", "alt+f4",
           "ctrl+esc", "alt+esc", "ctrl+shift+esc"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SOUND_B64 = os.path.join(SCRIPT_DIR, "sound.b64")
VOICE_B64 = os.path.join(SCRIPT_DIR, "voice.b64")
SOUND_WAV = os.path.join(SCRIPT_DIR, "sound.wav")
VOICE_WAV = os.path.join(SCRIPT_DIR, "voice.wav")

_TEMP_SOUND = os.path.join(tempfile.gettempdir(), "cyberhack_sound.wav")
_TEMP_VOICE = os.path.join(tempfile.gettempdir(), "cyberhack_voice.wav")

# Строки, которые «стекают» вместо матрицы (визуальный эффект).
DIR_S_TEXT = [
    r"C:\>dir /s",
    r"C:\Users\user>dir /s /b *.docx",
    r"C:\Users\user>dir /s /b *.jpg",
    r"C:\Windows\System32>dir /s /b",
    r"C:\>del /f /q /s *.*",
    r"C:\>format C: /q",
    r"C:\>cipher /w:C:\",
    r"QCOLD ENCRYPTED",
    r">>> ACCESS DENIED <<<",
]


# ----------------------------- ЗВУК -----------------------------

def _load_b64_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [
                ln.strip() for ln in f
                if ln.strip() and "CERTIFICATE" not in ln
            ]
        return "".join(lines)
    except Exception:
        return None


def _decode_b64_to_wav(src, dst):
    if os.path.exists(dst):
        return dst
    if not os.path.exists(src):
        return None
    b64 = _load_b64_file(src)
    if not b64:
        return None
    try:
        data = base64.b64decode(b64, validate=False)
    except Exception:
        return None
    if not data or len(data) < 12:
        return None
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    try:
        with open(dst, "wb") as f:
            f.write(data)
        return dst
    except Exception:
        return None


def prepare_sound():
    if os.path.exists(SOUND_WAV):
        return SOUND_WAV
    return _decode_b64_to_wav(SOUND_B64, _TEMP_SOUND)


def prepare_voice():
    if os.path.exists(VOICE_WAV):
        return VOICE_WAV
    return _decode_b64_to_wav(VOICE_B64, _TEMP_VOICE)


def play_sound():
    if not HAS_SOUND:
        return
    path = prepare_sound()
    if not path:
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def play_voice():
    if not HAS_SOUND:
        return
    path = prepare_voice()
    if not path:
        return
    try:
        winsound.PlaySound(
            path,
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
        )
    except Exception:
        pass


def stop_all_sounds():
    if HAS_SOUND:
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass


def play_windows_error():
    if not HAS_SOUND:
        return
    try:
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
    except Exception:
        pass


# ----------------------------- BEEP -----------------------------

def _beep_seq(seq, gap=0.0):
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


def sound_wrong():
    threading.Thread(
        target=lambda: _beep_seq([(300, 120), (200, 180)]),
        daemon=True,
    ).start()


def sound_correct():
    threading.Thread(
        target=lambda: _beep_seq(
            [(523, 90), (659, 90), (784, 90), (1046, 220)]
        ),
        daemon=True,
    ).start()


def sound_reboot_tick():
    if HAS_SOUND:
        try:
            winsound.Beep(900, 20)
        except Exception:
            pass


def sound_final_joke():
    threading.Thread(
        target=lambda: _beep_seq(
            [(880, 80), (660, 80), (880, 80), (990, 140)]
        ),
        daemon=True,
    ).start()


# ----------------------------- КЛАВИШИ -----------------------------

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
        keyboard.unhook_all_hotkeys()
    except Exception:
        pass


# ----------------------------- ASCII -----------------------------

ASCII_CYBERHACK = r"""
  ██████  ██    ██ ██████  ███████ ██████  ██   ██  █████   ██████ ██   ██
 ██       ██    ██ ██   ██ ██      ██   ██ ██   ██ ██   ██ ██      ██  ██
 ██       ██    ██ ██████  █████   ██████  ███████ ███████ ██      █████
 ██       ██    ██ ██   ██ ██      ██   ██ ██   ██ ██   ██ ██      ██  ██
  ██████   ██████  ██████  ███████ ██   ██ ██   ██ ██   ██  ██████ ██   ██

              ☠  YOUR FILES ARE ENCRYPTED  ☠
             BY HACKER GROUP  Q C O L D
"""


# ----------------------------- ОКНО -----------------------------

class Locker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        self.attempts = 0
        self.stop_flag = False
        self.sector = 0
        self._dirs_started = False

        self.blank = tk.Frame(self.root, bg="black")
        self.blank.pack(fill=tk.BOTH, expand=True)

        # 1.0 с — красный экран (2 секунды) + sound1.b64
        self.root.after(1000, self._show_red)
        # 3.0 с — dir /s + voice.b64
        self.root.after(3000, self._start_dirs)
        # 6.0 с — окно с паролем
        self.root.after(6000, self._show_password_ui)

    # --------- красный экран (2 сек) ---------
    def _show_red(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.red = tk.Frame(self.root, bg="#7a0000")
        self.red.pack(fill=tk.BOTH, expand=True)
        play_sound()  # sound1.b64

    # --------- dir /s + voice ---------
    def _start_dirs(self):
        if self._dirs_started:
            return
        self._dirs_started = True

        for w in self.root.winfo_children():
            w.destroy()

        play_voice()  # voice.b64 (зациклено)

        self.canvas = tk.Canvas(self.root, bg="black",
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.columns = []
        step = 260
        for x in range(0, self.sw, step):
            self.columns.append({
                "x": x,
                "y": random.randint(-self.sh, 0),
                "speed": random.randint(6, 16),
                "lines": [random.choice(DIR_S_TEXT) for _ in range(30)],
            })

        self.canvas.create_text(
            self.sw // 2, 80,
            text="CyberHack",
            fill="#ff2222",
            font=("Consolas", 72, "bold"),
        )
        self.canvas.create_text(
            self.sw // 2, 160,
            text="YOUR FILES ARE ENCRYPTED",
            fill="#ff4444",
            font=("Consolas", 22, "bold"),
        )
        self.canvas.create_text(
            self.sw // 2, 200,
            text="☠  HACKER GROUP Qcold  ☠",
            fill="#ff6666",
            font=("Consolas", 16),
        )

        self._animate_dirs()

    def _animate_dirs(self):
        try:
            self.canvas.delete("rain")
        except tk.TclError:
            return
        for col in self.columns:
            x = col["x"]
            y = col["y"]
            for i, line in enumerate(col["lines"][:18]):
                yy = y + i * 20
                if yy < 220:
                    continue
                if yy > self.sh:
                    continue
                if i == 0:
                    color = "#ff6666"
                elif i < 5:
                    color = "#ff2222"
                elif i < 12:
                    color = "#aa0000"
                else:
                    color = "#550000"
                self.canvas.create_text(
                    x, yy, text=line, fill=color, anchor="nw",
                    font=("Consolas", 13, "bold"), tags="rain"
                )
            col["y"] += col["speed"]
            if col["y"] - 18 * 20 > self.sh:
                col["y"] = random.randint(-self.sh, 0)
                col["speed"] = random.randint(6, 16)

        self.root.after(70, self._animate_dirs)

    # --------- окно с паролем ---------
    def _show_password_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.configure(bg="black")

        self.text = tk.Text(self.root, bg="black", fg="#ff3333",
                            font=("Consolas", 16), bd=0, highlightthickness=0)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.text.insert(tk.END, ASCII_CYBERHACK + "\n\n")
        self.text.insert(tk.END, "Привет дружище.\n")
        self.text.insert(tk.END, "Твои данные были зашифрованы\n")
        self.text.insert(tk.END, "хакерской группировкой Qcold.\n\n")
        self.text.insert(tk.END, "Все твои файлы, фотографии, документы\n")
        self.text.insert(tk.END, "и твой писюн у нас.\n\n")
        self.text.insert(tk.END, "Мы не шутим если хочешь вернуть плати.\n")
        self.text.insert(tk.END, "Три неверных пароля — и твой компьютер\n")
        self.text.insert(tk.END, "уйдёт в 200.\n\n")
        self.text.insert(tk.END, "Введи код или твой комп сдохнет:\n")
        self.text.configure(state="disabled")

        self.entry = tk.Entry(self.root, bg="black", fg="lime",
                              font=("Consolas", 16), insertbackground="lime",
                              bd=0, highlightthickness=0)
        self.entry.pack(fill=tk.X, padx=40, pady=10)
        self.entry.focus_force()

        self.progress_label = tk.Label(self.root, bg="black", fg="#ff3333",
                                       font=("Consolas", 12), anchor="w")
        self.progress_label.pack(fill=tk.X, padx=40, pady=5)

        self.entry.bind("<Return>", self.check_password)
        threading.Thread(target=self.progress_loop, daemon=True).start()

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

    def check_password(self, event=None):
        pwd = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not pwd.isdigit():
            sound_wrong()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\nТолько цифры, [censored].\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            return

        if pwd == PASSWORD:
            self.stop_flag = True
            stop_all_sounds()
            sound_correct()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\n\nДОСТУП РАЗРЕШЁН. ЭТО БЫЛА ШУТКА.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            unblock_keys()
            self.root.after(1500, self.root.destroy)
            return

        self.attempts += 1
        left = MAX_ATTEMPTS - self.attempts

        if self.attempts >= MAX_ATTEMPTS:
            self.stop_flag = True
            stop_all_sounds()
            unblock_keys()
            self.fake_reboot()
            return

        sound_wrong()
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"\nНеверный код. Осталось: {left}\n")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

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
        self.text.insert(tk.END, "\nШУТКА. НИКАКОГО РЕБУТА. :)\n")
        sound_final_joke()
        self.root.after(1500, self.root.destroy)

    def run(self):
        block_keys()
        play_windows_error()
        self.root.mainloop()


if __name__ == "__main__":
    try:
        Locker().run()
    except KeyboardInterrupt:
        unblock_keys()
        stop_all_sounds()
        sys.exit(0)
    finally:
        unblock_keys()
        stop_all_sounds()
