# -*- coding: utf-8 -*-
import sys, time, threading, tkinter as tk
try:
    import keyboard
except ImportError:
    sys.exit(1)

PASSWORD = "123"
MAX_ATTEMPTS = 3
BLOCKED = ["left windows","right windows","alt+tab","alt+f4",
           "ctrl+esc","alt+esc","ctrl+shift+esc"]

def block_keys():
    for k in BLOCKED:
        try: keyboard.block_key(k)
        except: pass

def unblock_keys():
    for k in BLOCKED:
        try: keyboard.unblock_key(k)
        except: pass
    try: keyboard.unhook_all()
    except: pass

ASCII = """
 #####  #   # ##### ##### #####  #   #  ###   ####  #   #
#      #   # #   # #   # #     #   # #   # #     #  #
#      ##### ##### ##### ####  ##### ##### #     ####
#      #   # #   # #   # #     #   # #   # #     #  #
 #####  #   # ##### ##### #####  #   # #   #  ####  #   #
"""

class Locker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # 去掉标题栏和关闭按钮
        self.root.attributes("-fullscreen", True)  # 全屏
        self.root.attributes("-topmost", True)     # 永远置顶
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

    def progress_loop(self):
        while not self.stop_flag:
            self.sector += 1
            self.progress_label.config(text=f"Encrypting sector {self.sector}...")
            time.sleep(0.1)

    def check_password(self, event=None):
        pwd = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not pwd.isdigit():
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\nOnly digits allowed.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            return
        if pwd == PASSWORD:
            self.stop_flag = True
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
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"\nWrong. {left} attempts left.\n")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

    def fake_reboot(self):
        self.progress_label.config(text="SYSTEM IS REBOOTING...")
        self.text.configure(state="normal")
        for i in range(41):
            bar = "#" * (i * 40 // 40) + "-" * (40 - i * 40 // 40)
            self.text.delete("end-2l", "end-1l")
            self.text.insert(tk.END, f"\n[{bar}] {i*100//40}%\n")
            self.text.see(tk.END)
            self.root.update()
            time.sleep(0.05)
        self.text.insert(tk.END, "\nJUST KIDDING. NO REBOOT. :)\n")
        self.root.after(1500, self.root.destroy)

    def run(self):
        block_keys()
        self.root.mainloop()

if __name__ == "__main__":
    try:
        Locker().run()
    except KeyboardInterrupt:
        unblock_keys()
        sys.exit(0)
    finally:
        unblock_keys()
