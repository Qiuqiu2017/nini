import math
import random
import time
import tkinter as tk

from .state import save

BG = "#0f1115"
SURFACE = "#171a21"
SURFACE2 = "#1e2230"
BORDER = "#2a2f3a"
TEXT = "#e8eaf0"
DIM = "#9aa2b1"
ACCENT = "#3ddc84"
CYAN = "#4dd6ff"
MAGENTA = "#f07bd6"
YELLOW = "#ffd166"
FONT = ("Noto Sans CJK SC", 11)
FONT_BOLD = ("Noto Sans CJK SC", 11, "bold")
MONO = ("Noto Sans Mono CJK SC", 10)


class GUI:
    def __init__(self, engine, state_path):
        self.eng = engine
        self.state_path = state_path
        self.msg = None
        self.shown = 0
        self.typing_widgets = []
        self.typing_tags = []
        self.quitting = False
        self.squeeze_phase = None
        self.root = None

    def run(self):
        root = tk.Tk()
        self.root = root
        root.title("你你 · 挤语")
        root.configure(bg=BG)
        root.geometry("1060x640")
        root.minsize(880, 560)
        root.protocol("WM_DELETE_WINDOW", self._quit)
        self._build(root)
        self._replay()
        root.after(60, self._next)
        root.mainloop()

    def _replay(self):
        for m in self.eng.history:
            if m["who"] == "U":
                self._append(self.user_text, "你 ▸ " + m["cj"], "u")
                if self.eng.subtitles and m["zh"] != m["cj"]:
                    self._append(self.user_text, "  ·" + m["zh"], "d")
            elif m["who"] == "L":
                self._append(self.left_text, self.eng.names["L"] + " ▸ ", "n")
                self._append(self.left_text, m["cj"], "t")
                if self.eng.subtitles and m["zh"] != m["cj"]:
                    self._append(self.left_text, "  ·" + m["zh"], "d")
            elif m["who"] == "R":
                self._append(self.right_text, self.eng.names["R"] + " ▸ ", "n")
                self._append(self.right_text, m["cj"], "t")
                if self.eng.subtitles and m["zh"] != m["cj"]:
                    self._append(self.right_text, "  ·" + m["zh"], "d")
            else:
                for w in (self.left_text, self.right_text):
                    self._append(w, "★ " + m["cj"], "e")

    def _build(self, root):
        top = tk.Frame(root, bg=BG)
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(top, text="你你 · 挤语", bg=BG, fg=ACCENT, font=("Noto Sans CJK SC", 16, "bold")).pack(side="left")
        self.status_label = tk.Label(top, text="", bg=BG, fg=DIM, font=FONT)
        self.status_label.pack(side="left", padx=14)
        self.bar = tk.Canvas(top, width=200, height=16, bg=BG, highlightthickness=0)
        self.bar.pack(side="left")
        self.names_label = tk.Label(top, text="", bg=BG, fg=DIM, font=FONT)
        self.names_label.pack(side="right")

        self.panes = tk.PanedWindow(root, orient="horizontal", bg=BORDER,
                                    sashwidth=5, bd=0, relief="flat")
        self.panes.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.left_text, self.right_text = self._make_panel(self.eng.names["L"], CYAN), \
                                          self._make_panel(self.eng.names["R"], MAGENTA)

        bottom = tk.Frame(root, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(0, 6))

        self.user_text = tk.Text(bottom, height=2, bg=SURFACE2, fg=TEXT,
                                 relief="flat", bd=0, font=FONT, wrap="word",
                                 state="disabled", padx=10, pady=6, highlightthickness=0)
        self.user_text.pack(fill="x", pady=(0, 6))
        self.user_text.tag_configure("u", foreground=YELLOW, font=FONT_BOLD)
        self.user_text.tag_configure("d", foreground="#5c6577", font=FONT)

        bar = tk.Frame(bottom, bg=BG)
        bar.pack(fill="x")
        self.entry = tk.Entry(bar, bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                              relief="flat", font=FONT)
        self.entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.focus_set()
        self._btn(bar, "发送", self._send, primary=True).pack(side="left", padx=(8, 0))

        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(fill="x", padx=16, pady=(0, 4))
        self.sub_var = tk.BooleanVar(value=self.eng.subtitles)
        tk.Checkbutton(ctrl, text="中文翻译", variable=self.sub_var,
                       command=self._toggle_sub, bg=BG, fg=DIM, font=FONT,
                       activebackground=BG, activeforeground=TEXT,
                       selectcolor=SURFACE2, highlightthickness=0).pack(side="left")
        self.pause_btn = self._btn(ctrl, "暂停", self._toggle_pause)
        self.pause_btn.pack(side="left", padx=6)
        self._btn(ctrl, "快点", lambda: self._set_speed(1)).pack(side="left", padx=6)
        self._btn(ctrl, "慢点", lambda: self._set_speed(-1)).pack(side="left", padx=6)
        self._btn(ctrl, "存档", self._do_save).pack(side="left", padx=6)
        self._btn(ctrl, "重置", self._do_reset).pack(side="left", padx=6)
        self.hint_label = tk.Label(ctrl, text="输入中文，按回车打断他们", bg=BG, fg="#5c6577", font=FONT)
        self.hint_label.pack(side="right")

        root.bind("<Escape>", lambda e: self._insta_finish())
        self._update_status()

    def _make_panel(self, name, color):
        frame = tk.Frame(self.panes, bg=SURFACE)
        head = tk.Frame(frame, bg=SURFACE)
        head.pack(fill="x", padx=12, pady=(8, 4))
        tk.Label(head, text="●", bg=SURFACE, fg=color, font=FONT_BOLD).pack(side="left")
        tk.Label(head, text=name, bg=SURFACE, fg=color, font=FONT_BOLD).pack(side="left", padx=(6, 0))
        text = tk.Text(frame, bg=SURFACE, fg=TEXT, relief="flat", bd=0, font=FONT,
                       wrap="word", state="disabled", padx=12, pady=6,
                       highlightthickness=0, cursor="arrow")
        text.pack(fill="both", expand=True)
        text.tag_configure("n", foreground=color, font=FONT_BOLD)
        text.tag_configure("t", foreground=TEXT, font=FONT)
        text.tag_configure("d", foreground="#5c6577", font=FONT)
        text.tag_configure("e", foreground=ACCENT, font=FONT_BOLD)
        self.panes.add(frame, stretch="always")
        return text

    def _btn(self, parent, label, cmd, primary=False):
        return tk.Button(parent, text=label, command=cmd,
                         bg=ACCENT if primary else SURFACE2,
                         fg="#06210f" if primary else TEXT,
                         activebackground=BORDER, activeforeground=TEXT,
                         relief="flat", bd=0, padx=12, pady=4, font=FONT,
                         cursor="hand2", highlightthickness=0)

    def _panel_for(self, who):
        if who == "L":
            return self.left_text
        if who == "R":
            return self.right_text
        return None

    def _append(self, widget, text, tag):
        widget.configure(state="normal")
        if widget.get("end-2c", "end-1c") and not widget.get("end-2c", "end-1c").endswith("\n"):
            widget.insert("end", "\n")
        widget.insert("end", text, tag)
        widget.see("end")
        widget.configure(state="disabled")

    def _start_msg(self, m):
        self.msg = m
        self.shown = 0
        self.typing_widgets = []
        self.typing_tags = []
        if m["who"] in ("E", "S"):
            for w, tag in ((self.left_text, "e"), (self.right_text, "e")):
                self._append(w, "★ " if w is self.left_text else "★ ", tag)
                self.typing_widgets.append(w)
                self.typing_tags.append(tag)
        elif m["who"] == "L":
            w = self.left_text
            self._append(w, self.eng.names["L"] + " ▸ ", "n")
            self.typing_widgets = [w]
            self.typing_tags = ["t"]
        elif m["who"] == "R":
            w = self.right_text
            self._append(w, self.eng.names["R"] + " ▸ ", "n")
            self.typing_widgets = [w]
            self.typing_tags = ["t"]
        if "挤" in m.get("cj", ""):
            self._squeeze()

    def _next(self):
        if self.quitting:
            return
        if self.msg is not None:
            full = len(self.msg["cj"])
            if self.shown < full:
                step = max(1, self.eng.speed)
                piece = self.msg["cj"][self.shown:self.shown + step]
                self.shown += len(piece)
                for i, w in enumerate(self.typing_widgets):
                    w.configure(state="normal")
                    w.insert("end", piece, self.typing_tags[i])
                    w.see("end")
                    w.configure(state="disabled")
                self.root.after(32, self._next)
                return
            self._finish_msg()
            self.root.after(self._pause(), self._next)
            return
        m = self.eng.tick()
        if m is None:
            self.root.after(280, self._next)
            return
        self._start_msg(m)
        self.root.after(60, self._next)

    def _finish_msg(self):
        m = self.msg
        self.msg = None
        self.typing_widgets = []
        if self.eng.subtitles and m["who"] not in ("E", "S") and m["zh"] != m["cj"]:
            w = self.left_text if m["who"] == "L" else self.right_text
            self._append(w, "  ·" + m["zh"], "d")
        self._update_status()

    def _pause(self):
        return random.randint(550, 1300)

    def _squeeze(self):
        if self.squeeze_phase is not None:
            return
        width = self.panes.winfo_width()
        self.squeeze_phase = {"center": width // 2, "t": 0}

        def anim():
            if self.quitting or self.squeeze_phase is None:
                return
            st = self.squeeze_phase
            st["t"] += 1
            if st["t"] > 24:
                self.squeeze_phase = None
                self.panes.sash_place(0, self.panes.winfo_width() // 2, 0)
                return
            off = int(round(2.2 * math.sin(st["t"] / 3.2)))
            self.panes.sash_place(0, st["center"] + off, 0)
            self.root.after(45, anim)

        anim()

    def _send(self):
        text = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not text:
            return
        umsg = self.eng.handle_user(text)
        self._append(self.user_text, "你 ▸ " + umsg["cj"], "u")
        if self.eng.subtitles and umsg["zh"] != umsg["cj"]:
            self._append(self.user_text, "  ·" + umsg["zh"], "d")
        self._update_status()

    def _toggle_sub(self):
        self.eng.subtitles = self.sub_var.get()

    def _toggle_pause(self):
        self.eng.paused = not self.eng.paused
        self.pause_btn.configure(text="继续" if self.eng.paused else "暂停")
        self.hint_label.configure(
            text="（已暂停，按继续恢复聊天）" if self.eng.paused else "输入中文，按回车打断他们")

    def _set_speed(self, delta):
        self.eng.speed = max(1, min(6, self.eng.speed + delta))
        self.hint_label.configure(text=f"说话速度 {self.eng.speed}/6")

    def _do_save(self):
        save(self.eng, self.state_path)
        self.hint_label.configure(text="已存档 " + time.strftime("%H:%M:%S"))

    def _do_reset(self):
        self.eng.reset()
        self.msg = None
        self.typing_widgets = []
        for w in (self.left_text, self.right_text, self.user_text):
            w.configure(state="normal")
            w.delete("1.0", "end")
            w.configure(state="disabled")
        self._update_status()
        self.hint_label.configure(text="语言已重置，从头再挤一遍")

    def _insta_finish(self):
        if self.msg is not None and self.shown < len(self.msg["cj"]):
            piece = self.msg["cj"][self.shown:]
            self.shown = len(self.msg["cj"])
            for i, w in enumerate(self.typing_widgets):
                w.configure(state="normal")
                w.insert("end", piece, self.typing_tags[i])
                w.see("end")
                w.configure(state="disabled")

    def _update_status(self):
        cl = self.eng.conlang
        st = (f"第{cl.current_era()}纪元 · 词 {cl.converted_count()}/{cl.total_words()} · "
              f"进度 {int(cl.progress() * 100)}% · 语言: {self.eng.lang_name or '尚未诞生'}")
        self.status_label.configure(text=st)
        self.names_label.configure(
            text=f"{self.eng.names['L']} 挤 {self.eng.names['R']}")
        self.bar.delete("all")
        w = int(self.bar.winfo_width()) or 200
        h = int(self.bar.winfo_height()) or 16
        self.bar.create_rectangle(0, 0, w, h, fill=SURFACE2, outline="")
        self.bar.create_rectangle(0, 0, w * cl.progress(), h, fill=ACCENT, outline="")
        self.bar.create_text(w // 2, h // 2, text=f"{int(cl.progress() * 100)}%",
                             fill="#06210f", font=("DejaVu Sans", 8, "bold"))

    def _quit(self):
        self.quitting = True
        try:
            save(self.eng, self.state_path)
        except OSError:
            pass
        self.root.destroy()
