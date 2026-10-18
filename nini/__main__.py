import argparse
import os
import sys

from .brain import Engine
from .state import default_state_path, load


def _force_utf8():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def demo(n, seed):
    eng = Engine(seed)
    step = 0
    print("你你 · 挤语 —— 两个「你」挤在一起，把中文一步步挤成新语言")
    print("=" * 62)
    samples = ["你们聊到哪啦?", "挤语好玩吗?", "新词来一个!", "停一下，让我想想", "继续挤!"]
    while step < n:
        m = eng.tick()
        if m is None:
            eng.paused = False
            continue
        step += 1
        who = m["who"]
        label = {
            "L": eng.names["L"],
            "R": eng.names["R"],
            "U": "你",
            "S": "系统",
            "E": "新纪元",
        }[who]
        if who in ("E", "S"):
            print(f"  {label}  {m['cj']}")
        else:
            print(f"{label}: {m['cj']}")
            if m["zh"] != m["cj"]:
                print(f"    (中文) {m['zh']}")
        if step % 15 == 0:
            text = eng.rng.choice(samples)
            umsg = eng.handle_user(text)
            if umsg:
                print(f"你: {umsg['cj']}")
                if umsg["zh"] != umsg["cj"]:
                    print(f"    (中文) {umsg['zh']}")
    print("=" * 62)
    print(eng.status_line())


def check():
    import os as _os
    eng = Engine(seed=42)
    for _ in range(1600):
        m = eng.tick()
        if m is None:
            eng.paused = False
            continue
    cl = eng.conlang
    assert cl.converted_count() > 60, "转化的词太少"
    assert len(cl.eras_done) >= 8, "纪元推进太慢"
    assert cl.progress() > 0.5, "进度异常"
    cj, zh = cl.translate("你好，我很喜欢你")
    assert cj != zh, "翻译未生效"
    assert "你好" not in cj, "翻译未生效"
    assert "咩啾" in cj or "啾" in cj, "句尾粒子缺失"
    from .state import load as _load, save as _save
    path = "/tmp/nini_check_state.json"
    _save(eng, path)
    eng2 = _load(path)
    assert eng2.conlang.converted_count() == cl.converted_count(), "存档不一致"
    assert eng2.msg_count == eng.msg_count
    _os.remove(path)
    print("selfcheck OK")


def _tui(engine, path):
    import locale
    for cand in ("", "C.UTF-8", "en_US.UTF-8"):
        try:
            locale.setlocale(locale.LC_ALL, cand)
            break
        except locale.Error:
            continue
    from .ui import TUI
    TUI(engine, path).run()


def _gui(engine, path):
    from .gui import GUI
    GUI(engine, path).run()


def main(argv=None):
    _force_utf8()
    ap = argparse.ArgumentParser(
        prog="nini", description="你你 · 挤语：两个「你」挤在一起，把中文一步步挤成新语言"
    )
    ap.add_argument("--demo", type=int, metavar="N", help="非交互演示 N 条消息后退出")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--reset", action="store_true", help="清除存档重新开始")
    ap.add_argument("--check", action="store_true", help="自检后退出")
    ap.add_argument("--tui", action="store_true", help="使用终端界面（默认使用图形界面）")
    ap.add_argument("--state", default=None, help="存档文件路径")
    args = ap.parse_args(argv)

    if args.check:
        check()
        return
    path = args.state or default_state_path()
    if args.reset and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
    if args.demo:
        demo(args.demo, args.seed)
        return
    engine = load(path, seed=args.seed)
    if args.tui:
        _tui(engine, path)
        return
    try:
        _gui(engine, path)
        return
    except ImportError:
        sys.stderr.write("未安装 tkinter，改用终端界面。\n")
    except Exception as e:
        sys.stderr.write(f"图形界面不可用（{e}），改用终端界面。\n")
    if not sys.stdin.isatty():
        demo(40, args.seed)
        print("（非终端环境，已自动进入演示模式；在终端里运行可交互界面）")
        return
    _tui(engine, path)


if __name__ == "__main__":
    main()
