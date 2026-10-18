import json
import os

from .brain import Engine

VERSION = 1


def default_state_path():
    return os.environ.get("NINI_STATE") or os.path.join(
        os.path.expanduser("~"), ".config", "nini", "state.json"
    )


def save(engine, path):
    data = {
        "version": VERSION,
        "seed": engine.seed,
        "rng": list(engine.rng.getstate()[1]),
        "converted": engine.conlang.converted,
        "dynamic": engine.conlang.dynamic,
        "eras_done": engine.conlang.eras_done,
        "names": engine.names,
        "msg_count": engine.msg_count,
        "since_word": engine.since_word,
        "last_who": engine.last_who,
        "speed": engine.speed,
        "subtitles": engine.subtitles,
        "paused": engine.paused,
        "lang_name": engine.lang_name,
        "history": engine.history[-300:],
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def load(path, seed=None):
    engine = Engine(seed)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return engine
    if data.get("version") != VERSION:
        return engine
    try:
        st = engine.rng.getstate()
        engine.rng.setstate((st[0], tuple(data["rng"]), st[2]))
    except (KeyError, TypeError):
        pass
    engine.conlang.converted = list(data.get("converted") or [])
    engine.conlang.dynamic = dict(data.get("dynamic") or {})
    engine.conlang.eras_done = list(data.get("eras_done") or [])
    engine.names = data.get("names") or engine.names
    engine.msg_count = data.get("msg_count") or 0
    engine.since_word = data.get("since_word") or 0
    engine.last_who = data.get("last_who")
    engine.speed = data.get("speed") or 3
    engine.subtitles = data.get("subtitles", True)
    engine.paused = bool(data.get("paused"))
    engine.lang_name = data.get("lang_name")
    engine.history = data.get("history") or []
    engine.queue = []
    if engine.msg_count == 0:
        engine._greet()
    return engine
