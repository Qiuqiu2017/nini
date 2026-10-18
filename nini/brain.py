import random
import re

from .conlang import Conlang, RULES, STOP, invent_word

FOOD = ["饭", "面条", "饺子", "火锅", "奶茶", "蛋糕", "水果", "冰淇淋", "包子", "烤串"]
ANIMALS = ["猫", "狗", "兔子", "鱼", "鸟", "熊猫", "蝴蝶", "仓鼠", "企鹅"]
THINGS = ["星星", "月亮", "太阳", "风", "雨", "云", "山", "海", "花", "树", "梦", "歌", "茶"]

NORMAL = [
    "泥能不能别挤窝?",
    "挤一挤更暖和。",
    "再挤窝就把泥嗝字都抢走!",
    "看, 窝们两个挤成一颗爱心辽。",
    "屏幕太挤辽, 泥往那边挪挪。",
    "窝今天想吃{food}。",
    "泥见过{animal}吗? 它好可爱。",
    "窝昨晚梦见{thing}辽。",
    "天好蓝, 适合挤在一起发呆。",
    "泥觉得{thing}和{thing2}哪个更吼?",
    "窝想给{animal}取个名字。",
    "听说{thing}很吼吃, 窝们去试试?",
    "窝有点累辽, 借泥肩膀靠靠。",
    "今天风好大, 把窝嗝{word}都吹跑辽。",
    "窝们嗝新语言越来越像样辽。",
    "{word}这个词还能挤得更短!",
    "泥说, 新语言以后叫什么名字好?",
    "等改造完, 窝们就出名辽!",
    "旧话听起来好陌生鸭。",
    "以后窝们只说挤语, 谁先犯规谁输。",
    "泥最喜欢哪个新词?",
    "泥饿不饿? 窝有点饿辽。",
    "泥觉得窝们还要聊多久?",
    "泥会不会有一天把窝忘辽?",
    "窝数羊数到一半, 羊说: 泥挤到窝辽。",
    "如果猫会打字, 它一定先踩空格。",
    "窝把闹钟挤坏辽, 所以睡到现在。",
    "{word}这个词今天看起来格外顺眼。",
    "窝刚想到一句很厉害嗝话, 然后忘辽。",
    "泥听, 外面有{animal}在唱歌。",
    "窝们嗝字典越来越厚辽。",
    "泥挤过来一点, 窝给泥看个好东西。",
    "窝今天心情很好, 因为泥在。",
    "小声点, 别把键盘吵醒辽。",
    "窝刚才偷偷把「{word}」念辽十遍。",
    "泥有没有觉得, 挤在一起时间过得特别快?",
    "窝发明辽一个新动作, 叫「挤一下」。",
    "等窝们嗝语言出生, 第一句话要说啥?",
    "泥看窝干嘛? 窝脸上有字咩?",
    "窝梦见新语言会发光, 一挤就亮。",
]

GREET = [
    "泥吼鸭! 挤过来点, 给泥留了位置。",
    "哎鸭! 泥终于说话辽, 窝们正聊得欢。",
    "吼久不见! 窝们还在努力造新语言捏。",
    "欢迎挤进来! 窝们刚才说到一半。",
]

WHO = [
    "窝们是两个「你」, 被塞进同一块屏幕里。",
    "窝是{name}, 旁边是{name2}, 窝们负责把中文挤成新语言。",
    "窝们挤在一起越久, 新语言就越像样。",
]

PROGRESS_LINE = "现在系第{era}纪元, 已经改造辽 {n}/{total} 个词, 进度 {p}%。"

SQUEEZE = [
    "挤挤更健康!",
    "别挤别挤, 窝要扁辽!",
    "窝们天生就是挤在一起嗝。",
    "泥再挤, 窝就把泥嗝词也挤进来。",
]

NAME_LINE = "窝叫{name}, 旁边这挤叫{name2}, 都是窝们自己挤出来嗝。"

LOVE = [
    "窝也稀饭泥鸭!",
    "突然说这个, 挤得窝脸都红辽。",
    "呜…泥这么一挤, 窝心跳都加速辽。",
]

BYE = [
    "泥要走啦? 那窝们小声点聊。",
    "拜拜泥! 窝们继续挤在这里等泥。",
    "快回来鸭, 挤语还没出生捏。",
]

DEFAULT = [
    "「{echo}」…窝听进去辽。",
    "泥这话窝得挤一挤才能懂。",
    "有道理! 快记进字典。",
    "嗷, 窝懂辽(其实米有)。",
    "泥挤过来讲, 窝认真听。",
]

REACTIONS = [
    (["你好", "嗨", "哈喽", "hi", "hello", "在吗", "早上好", "晚上好", "泥吼"], GREET),
    (["你是谁", "你们是谁", "介绍一下", "自我介绍", "干嘛"], WHO),
    (["语言", "翻译", "改造", "进化", "新语言", "进度", "挤语"], None),
    (["加速", "快点", "快一点", "说快点"], ["好嘞! 窝们聊快一点!", "挤速全开!"], "faster"),
    (["慢点", "说慢点", "慢一点"], ["行叭, 挤得温柔点。", "吼叭, 窝们慢慢挤。"], "slower"),
    (["停", "暂停", "安静", "别说话"], ["那窝们先眯一会儿…", "嘘——窝们屏住呼吸。"], "pause"),
    (["继续", "接着说", "继续聊", "接着聊"], ["窝们回来辽! 刚才聊到哪儿捏?", "继续挤!"], "resume"),
    (["挤"], SQUEEZE, "squeeze"),
    (["名字", "叫什么", "名名"], [NAME_LINE]),
    (["喜欢", "爱", "稀饭"], LOVE),
    (["再见", "拜拜", "走啦", "溜了", "晚安"], BYE),
    (["新词", "造词", "词"], ["泥想听新词? 窝刚好憋了一挤!"], "invent"),
    (["吃", "饿", "饭", "好吃", "吼吃"], ["窝也饿辽! 一起挤去吃点{food}?", "泥一说吃, 窝肚子就咕咕挤。"]),
    (["好玩", "有趣", "厉害", "好玩吗"], ["超吼玩! 泥挤进来更吼玩。", "当然! 窝们可是语言发明家。"]),
]

HANZI = re.compile(r"[\u4e00-\u9fff]{2,}")


class Engine:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.seed = seed
        self.conlang = Conlang(self.rng)
        self.speed = 3
        self.subtitles = True
        self.paused = False
        self.reset()

    def reset(self):
        self.conlang.reset()
        self.names = {"L": "", "R": ""}
        self.msg_count = 0
        self.since_word = 0
        self.last_who = None
        self.queue = []
        self.history = []
        self.lang_name = None
        self.invent_soon = False
        if not self.names["L"]:
            self.names["L"] = invent_word(self.rng, "cute") or "啾啾"
        if not self.names["R"]:
            other = invent_word(self.rng, "cute") or "咪咪"
            while other == self.names["L"]:
                other = invent_word(self.rng, "cute")
            self.names["R"] = other
        if self.msg_count == 0:
            self._greet()

    def _greet(self):
        l, r = self.names["L"], self.names["R"]
        self.queue += [
            {"who": "L", "zh": "泥吼鸭! 窝们挤在同一个屏幕里辽!", "cj": None},
            {"who": "R", "zh": f"太挤辽! 泥先介绍一下自己?", "cj": None},
            {"who": "L", "zh": f"窝系{l}, 窝稀饭造新词。", "cj": None},
            {"who": "R", "zh": f"窝系{r}, 窝负责把词挤短。", "cj": None},
        ]
        for m in self.queue:
            m["cj"], m["zh"] = self.conlang.translate(m["zh"])

    def _log(self, msg):
        self.history.append(msg)
        if len(self.history) > 400:
            self.history = self.history[-400:]
        self.msg_count += 1
        if msg["who"] in ("L", "R"):
            self.last_who = msg["who"]

    def speak(self, who, zh):
        cj, orig = self.conlang.translate(zh)
        msg = {"who": who, "zh": orig, "cj": cj}
        self._log(msg)
        return msg

    def _fill(self, template, who, echo=""):
        l, r = self.names["L"], self.names["R"]
        other = r if who == "L" else l
        word = None
        sample = self.conlang.sample_converted(6)
        if sample:
            word = self.rng.choice(sample)[0]
        thing = self.rng.choice(THINGS)
        thing2 = self.rng.choice([t for t in THINGS if t != thing])
        return template.format(
            food=self.rng.choice(FOOD),
            animal=self.rng.choice(ANIMALS),
            thing=thing,
            thing2=thing2,
            word=word or "挤",
            name=self.names[who],
            name2=other,
            echo=echo[:12],
        )

    def _chat_line(self, who):
        return self._fill(self.rng.choice(NORMAL), who)

    def _announce(self, who, zh_line, old_word, new_word=None):
        masked = zh_line
        if old_word is not None:
            masked = masked.replace(old_word, "\x00")
        if new_word is not None:
            masked = masked.replace(new_word, "\x01")
        cj, zh = self.conlang.translate(masked)
        if old_word is not None:
            cj = cj.replace("\x00", old_word)
        if new_word is not None:
            cj = cj.replace("\x01", new_word)
        return {"who": who, "zh": zh_line, "cj": cj}

    def _word_event(self):
        self.invent_soon = False
        z, new = self.conlang.invent_next()
        l, r = self.names["L"], self.names["R"]
        if self.rng.random() < 0.45:
            short = self.conlang._compress(new)
            self.conlang.dynamic[z] = short
            new = short
            self.queue += [
                self._announce("L", f"窝宣布!「{z}」从今以后就叫「{new}」!", z, new),
                {"who": "R", "zh": "太长辽! 挤短点!", "cj": None},
                self._announce("L", f"那挤成「{new}」, 行叭?", None, new),
                {"who": "R", "zh": "行叭, 挤进字典。", "cj": None},
            ]
        else:
            react = self.rng.choice([
                "行叭, 挤进字典。",
                "喵鸭! 这个名字窝稀饭。",
                "吼! 快记下来!",
                f"「{new}」? 挤一挤还行。",
            ])
            self.queue += [
                self._announce("L", f"窝宣布!「{z}」从今以后就叫「{new}」!", z, new),
                {"who": "R", "zh": react, "cj": None},
            ]
        for m in self.queue:
            if m["cj"] is None:
                m["cj"], m["zh"] = self.conlang.translate(m["zh"])
        self.since_word = 0
        self._maybe_era_up(z)

    def _maybe_era_up(self, z):
        e = self.conlang.eras.get(z)
        if e is None:
            e = self.conlang.current_era()
        done = self.conlang.era_complete(e) and e not in self.conlang.eras_done
        if not done:
            return
        self.conlang.eras_done.append(e)
        self.queue.append({
            "who": "E",
            "zh": f"【第{e}纪元】{RULES[e]}",
            "cj": f"【第{e}纪元】{RULES[e]}",
        })
        if e >= 10 and not self.lang_name:
            self.lang_name = invent_word(self.rng, "cute").strip("～") + "挤语"
            self.queue.append({
                "who": "E",
                "zh": f"从今以后, 这种新语言就叫「{self.lang_name}」!",
                "cj": f"从今以后, 这种新语言就叫「{self.lang_name}」!",
            })

    def tick(self):
        if self.queue:
            m = self.queue.pop(0)
            self._log(m)
            return m
        if self.paused:
            return None
        if self.invent_soon and self.conlang.unconverted():
            self._word_event()
            m = self.queue.pop(0)
            self._log(m)
            return m
        if self.since_word >= 2 and self.conlang.unconverted():
            self._word_event()
            m = self.queue.pop(0)
            self._log(m)
            return m
        who = "R" if self.last_who == "L" else "L"
        zh = self._chat_line(who)
        self.since_word += 1
        return self.speak(who, zh)

    def _progress_text(self):
        cl = self.conlang
        p = int(cl.progress() * 100)
        return PROGRESS_LINE.format(
            era=cl.current_era(),
            n=cl.converted_count(),
            total=cl.total_words(),
            p=p,
        )

    def handle_user(self, text):
        text = (text or "").strip()
        if not text:
            return None
        cj, zh = self.conlang.translate(text)
        umsg = {"who": "U", "zh": text, "cj": cj}
        self.history.append(umsg)
        if len(self.history) > 400:
            self.history = self.history[-400:]
        self._react(text)
        return umsg

    def _react(self, text):
        low = text.lower()
        flag = None
        lines = None
        matched = False
        for kws, tmpls, *extra in REACTIONS:
            if any(k in low for k in kws):
                matched = True
                lines = tmpls
                flag = extra[0] if extra else None
                break
        if not matched:
            lines = [self.rng.choice(DEFAULT)]
        elif lines is None:
            lines = [self._progress_text()]
        if flag == "faster":
            self.speed = min(6, self.speed + 1)
        elif flag == "slower":
            self.speed = max(1, self.speed - 1)
        elif flag == "pause":
            self.paused = True
        elif flag == "resume":
            self.paused = False
        elif flag == "invent":
            self.invent_soon = True
        n = self.rng.choice([1, 1, 2])
        who = "R" if self.last_who == "L" else "L"
        picked = self.rng.sample(lines, min(n, len(lines)))
        for zh in picked:
            if "{era}" in zh:
                zh = self._progress_text()
            zh = self._fill(zh, who, echo=text)
            self.queue.append({"who": who, "zh": zh, "cj": None})
            who = "R" if who == "L" else "L"
        for m in self.queue[-len(picked):]:
            m["cj"], m["zh"] = self.conlang.translate(m["zh"])
        self._maybe_adopt(text)

    def _maybe_adopt(self, text):
        words = HANZI.findall(text)
        cl = self.conlang
        unknown = [
            w for w in words
            if w not in cl.lex and w not in cl.dynamic and w not in STOP
            and w not in cl.converted
        ]
        if not unknown or self.rng.random() > 0.6:
            return
        w = self.rng.choice(unknown[:5])
        style = self.rng.choice(["dup", "ji", "ge", "head"])
        if style == "dup":
            new = w + w[-1]
        elif style == "ji":
            new = w + "挤"
        elif style == "ge":
            new = w + "叽"
        else:
            new = w[0] + "挤挤"
        cl.dynamic[w] = new
        self.queue += [
            self._announce("L", f"「{w}」! 这个词窝稀饭, 以后它叫「{new}」!", w, new),
            {"who": "R", "zh": "泥说辽算? 算辽, 挤进字典叭。", "cj": None},
        ]
        for m in self.queue[-2:]:
            if m["cj"] is None:
                m["cj"], m["zh"] = self.conlang.translate(m["zh"])

    def status_line(self):
        cl = self.conlang
        return (
            f"第{cl.current_era()}纪元 · 词 {cl.converted_count()}/{cl.total_words()} · "
            f"进度 {int(cl.progress() * 100)}% · "
            f"语言: {self.lang_name or '尚未诞生'}"
        )
