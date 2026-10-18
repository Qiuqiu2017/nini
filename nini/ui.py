import curses
import math
import random
import signal
import time
import unicodedata


def dwidth(s):
    w = 0
    for ch in s:
        if unicodedata.combining(ch):
            continue
        w += 2 if unicodedata.east_asian_width(ch) in "WF" else 1
    return w


def trunc(s, width):
    if dwidth(s) <= width:
        return s
    out = ""
    for ch in s:
        if dwidth(out + ch) > width - 1:
            return out + "…"
        out += ch
    return out


def wrap_text(s, width):
    if width <= 0:
        return [""]
    lines = []
    cur = ""
    for ch in s:
        if dwidth(cur + ch) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    lines.append(cur)
    return lines


class TUI:
    def __init__(self, engine, state_path):
        self.eng = engine
        self.state_path = state_path
        self.rng = random.Random()
        self.msg = None
        self.shown = 0
        self.next_char_at = 0.0
        self.msg_done_at = 0.0
        self.next_tick_at = 0.0
        self.frame = 0
        self.squeeze = 0
        self.flash = ""
        self.flash_until = 0
        self.input_mode = False
        self.input_buf = ""
        self.confirm = None

    def run(self):
        def _sig(signum, frame):
            from .state import save
            try:
                save(self.eng, self.state_path)
            except OSError:
                pass
            raise SystemExit(0)
        signal.signal(signal.SIGTERM, _sig)
        signal.signal(signal.SIGINT, _sig)
        try:
            curses.wrapper(self._main)
        except curses.error as e:
            raise SystemExit(f"无法初始化终端界面: {e}")

    def _main(self, scr):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
        curses.init_pair(5, curses.COLOR_WHITE, -1)
        self.pair = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        scr.timeout(60)
        self._first_draw = True
        while True:
            now = time.monotonic()
            self.frame += 1
            if self.squeeze > 0:
                self.squeeze -= 1
            if self.input_mode:
                scr.timeout(-1)
                self._draw(scr)
                ch = scr.get_wch()
                if self._handle_input(scr, ch):
                    scr.timeout(60)
                    continue
                continue
            scr.timeout(60)
            self._advance(now)
            ch = None
            try:
                ch = scr.get_wch()
            except curses.error:
                pass
            if ch is not None:
                if ch == "q" or ch == "Q":
                    self._save()
                    return
                elif ch == "t" or ch == "T":
                    self.eng.subtitles = not self.eng.subtitles
                    self._flash("翻译字幕: 开" if self.eng.subtitles else "翻译字幕: 关")
                elif ch == "p" or ch == "P":
                    self.eng.paused = not self.eng.paused
                    self._flash("已暂停" if self.eng.paused else "继续挤")
                elif ch == "s" or ch == "S":
                    self._save()
                    self._flash("已存档")
                elif ch == "r" or ch == "R":
                    self.eng.reset()
                    self.msg = None
                    self.shown = 0
                    self._flash("语言已重置，重新开始挤")
                elif ch in ("\n", "\r") or ch == curses.KEY_ENTER:
                    self.input_mode = True
                    self.input_buf = ""
                elif ch == "\x1b":
                    if self.msg and self.shown < len(self.msg["cj"]):
                        self.shown = len(self.msg["cj"])
                        self.msg_done_at = time.monotonic() + 0.2
                elif ch == curses.KEY_RESIZE:
                    pass
            self._draw(scr)

    def _save(self):
        from .state import save
        save(self.eng, self.state_path)

    def _flash(self, text):
        self.flash = text
        self.flash_until = time.monotonic() + 2.0

    def _advance(self, now):
        if self.msg:
            full = len(self.msg["cj"])
            if self.shown < full:
                if now >= self.next_char_at:
                    self.shown += max(1, self.eng.speed)
                    self.next_char_at = now + 0.05
                return
            if self.msg_done_at == 0.0:
                self.msg_done_at = now + self.rng.uniform(0.8, 2.0)
                return
            if now < self.msg_done_at:
                return
            self.msg = None
            self.next_tick_at = now + self.rng.uniform(0.2, 0.8)
            return
        if now < self.next_tick_at:
            return
        m = self.eng.tick()
        if m is None:
            self.next_tick_at = now + 0.3
            return
        self.msg = m
        self.shown = 0
        self.msg_done_at = 0.0
        self.next_char_at = now + 0.2
        if "挤" in m.get("cj", ""):
            self.squeeze = 26

    def _handle_input(self, scr, ch):
        if ch == "\x1b":
            self.input_mode = False
            self.input_buf = ""
            return True
        if ch in ("\n", "\r") or ch == curses.KEY_ENTER:
            self.input_mode = False
            text = self.input_buf
            self.input_buf = ""
            if text.strip():
                self.eng.handle_user(text)
                self.next_tick_at = time.monotonic() + 0.15
            return True
        if ch in ("\x7f", "\x08") or ch == curses.KEY_BACKSPACE or ch == 263:
            self.input_buf = self.input_buf[:-1]
            return False
        if ch == curses.KEY_RESIZE:
            return False
        if isinstance(ch, str):
            if ch.isprintable() and len(self.input_buf) < 120:
                self.input_buf += ch
        return False

    def _draw(self, scr):
        h, w = scr.getmaxyx()
        scr.erase()
        if h < 12 or w < 46:
            try:
                scr.addstr(0, 0, "窗口太小，请放大终端 (至少 46x12)。")
            except curses.error:
                pass
            scr.refresh()
            return
        self._draw_top(scr, w)
        divider = w // 2
        if self.squeeze > 0:
            divider += int(round(1.5 * math.sin(self.frame / 5)))
            divider = max(16, min(w - 16, divider))
        self._draw_borders(scr, w, divider, h)
        self._draw_panel(scr, "R", divider + 1, w - divider - 1, 2, h - 8)
        self._draw_panel(scr, "L", 0, divider, 2, h - 8)
        self._draw_divider(scr, divider, h)
        self._draw_leak(scr, divider, h)
        self._draw_user(scr, w, h)
        self._draw_input(scr, w, h)
        scr.refresh()

    def _draw_top(self, scr, w):
        st = self.eng.status_line()
        p = self.eng.conlang.progress()
        bar_len = 12
        filled = int(p * bar_len)
        bar = "▓" * filled + "░" * (bar_len - filled)
        left = f" 你你 · 挤语   {st}  {bar} {int(p * 100)}%"
        right = f"{self.eng.names['L']} | {self.eng.names['R']}  "
        space = w - dwidth(left) - dwidth(right)
        try:
            scr.addstr(0, 0, left, curses.A_BOLD | curses.color_pair(4))
            scr.addstr(0, w - dwidth(right), right, curses.color_pair(2))
            if self.flash and time.monotonic() < self.flash_until:
                scr.addstr(0, max(0, dwidth(left) + 2), trunc(self.flash, max(4, space - 2)),
                           curses.A_BOLD | curses.color_pair(3))
        except curses.error:
            pass

    def _draw_borders(self, scr, w, divider, h):
        try:
            top = "┌" + "─" * (divider - 1) + "┬" + "─" * (w - divider - 2) + "┐"
            bot = "└" + "─" * (divider - 1) + "┴" + "─" * (w - divider - 2) + "┘"
            scr.addstr(1, 0, top, curses.color_pair(5))
            scr.addstr(h - 7, 0, bot, curses.color_pair(5))
        except curses.error:
            pass

    def _draw_divider(self, scr, divider, h):
        try:
            for y in range(2, h - 7):
                scr.addstr(y, divider, "│", curses.color_pair(5))
        except curses.error:
            pass

    def _draw_leak(self, scr, divider, h):
        if self.squeeze <= 0 or self.frame % 9 != 0:
            return
        last = None
        for m in reversed(self.eng.history):
            if m["who"] == "L":
                last = m
                break
        if not last or not last["cj"]:
            return
        ch = self.rng.choice(last["cj"])
        y = self.rng.randint(2, max(2, h - 8))
        try:
            scr.addstr(y, divider + 1, ch, curses.color_pair(1))
        except curses.error:
            pass

    def _panel_msgs(self, side):
        for m in self.eng.history:
            if m["who"] == side or m["who"] in ("E", "S"):
                yield m

    def _draw_panel(self, scr, side, x, width, y_top, y_bot):
        color = 1 if side == "L" else 2
        inner = width - 2
        if inner <= 0:
            return
        blocks = []
        msgs = list(self._panel_msgs(side))
        current = None
        if self.msg is not None and (
            self.msg["who"] == side or self.msg["who"] in ("E", "S")
        ):
            current = self.msg
        for m in reversed(msgs):
            if m is current:
                text = m["cj"][:self.shown]
                if self.shown < len(m["cj"]):
                    text += "▌"
            else:
                text = m["cj"]
            if m["who"] in ("E", "S"):
                color = 4
            else:
                color = 1 if side == "L" else 2
            lines = []
            chunks = wrap_text(text, inner)
            lines.append((chunks[0] if chunks else "", color, True))
            for c in chunks[1:]:
                lines.append(("  " + c, color, False))
            if self.eng.subtitles and m["who"] not in ("E", "S") and m.get("zh") and m["zh"] != m["cj"]:
                zchunks = wrap_text(m["zh"], inner - 4)
                for zc in zchunks[:2]:
                    lines.append(("  ·" + zc, 5, False))
            blocks.append(lines)
        y = y_bot
        for lines in blocks:
            y -= len(lines)
            if y < y_top:
                break
            for i, (text, col, bold) in enumerate(lines):
                attr = curses.color_pair(col)
                try:
                    scr.addstr(y + i, x, trunc(text, width - 1), attr)
                except curses.error:
                    pass

    def _draw_user(self, scr, w, h):
        last = None
        for m in reversed(self.eng.history):
            if m["who"] == "U":
                last = m
                break
        try:
            if last:
                scr.addstr(h - 6, 0, trunc("你 ▸ " + last["cj"], w - 1),
                           curses.A_BOLD | curses.color_pair(3))
                if self.eng.subtitles:
                    scr.addstr(h - 5, 0, trunc("  (中文) " + last["zh"], w - 1),
                               curses.A_DIM | curses.color_pair(5))
            else:
                scr.addstr(h - 6, 0, "按 Enter 加入聊天，随时可以打断他们。",
                           curses.A_DIM | curses.color_pair(5))
        except curses.error:
            pass

    def _draw_input(self, scr, w, h):
        try:
            if self.input_mode:
                scr.addstr(h - 3, 0, "你 ▸ ", curses.A_BOLD | curses.color_pair(3))
                scr.addstr(h - 3, dwidth("你 ▸ "), trunc(self.input_buf, w - 8),
                           curses.color_pair(3))
                scr.addstr(h - 3, min(w - 1, dwidth("你 ▸ ") + dwidth(self.input_buf)),
                           "▌", curses.color_pair(3))
            else:
                scr.addstr(h - 3, 0, "» ", curses.A_DIM)
                scr.addstr(h - 3, 2, "按 Enter 说话…", curses.A_DIM)
            if self.flash and time.monotonic() < self.flash_until:
                scr.addstr(h - 3, max(0, w - dwidth(self.flash) - 1), self.flash,
                           curses.A_BOLD | curses.color_pair(3))
            hint = ("[Enter]说话 [Esc]打断 [T]翻译:%s [P]暂停:%s [S]存档 [R]重置 [Q]退出"
                    % ("开" if self.eng.subtitles else "关",
                       "开" if self.eng.paused else "关"))
            scr.addstr(h - 2, 0, trunc(hint, w - 1), curses.A_DIM | curses.color_pair(5))
        except curses.error:
            pass
