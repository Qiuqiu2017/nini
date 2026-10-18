import random
import re

VOWELS = "aoeiuü"
VOWEL_TONES = {
    "a": "āáǎà",
    "o": "ōóǒò",
    "e": "ēéěè",
    "i": "īíǐì",
    "u": "ūúǔù",
    "ü": "ǖǘǚǜ",
}

SYLLABLES = [
    "mi", "mu", "ni", "nu", "pi", "pu", "ki", "ku", "li", "lu",
    "za", "zo", "de", "da", "bo", "be", "la", "lo", "ka", "ke",
    "ta", "te", "xi", "xu", "qiu", "nia", "mie", "piu", "dua",
    "rua", "kwa", "zhi", "po", "pa", "ma", "mo", "lei", "niu",
    "gua", "diu", "lü", "mü", "nü", "gü", "hu", "fei",
]

CUTE_TAILS = ["", "", "～咪", "～叽", "～啾", "～鸭", "-挤"]


def tone_syllable(syl, tone):
    if tone == 0:
        return syl
    idxs = [i for i, c in enumerate(syl) if c in VOWELS]
    if not idxs:
        return syl
    if len(idxs) > 1:
        first = idxs[0]
        if syl[first] in "iuü" and syl[idxs[1]] not in "iuü":
            idx = idxs[1]
        else:
            idx = first
    else:
        idx = idxs[0]
    c = syl[idx]
    return syl[:idx] + VOWEL_TONES[c][tone - 1] + syl[idx + 1:]


def invent_word(rng, style="cute"):
    n = rng.choice([1, 1, 2, 2])
    s = "".join(tone_syllable(rng.choice(SYLLABLES), rng.randint(0, 4)) for _ in range(n))
    if style == "cute" and rng.random() < 0.55:
        s += rng.choice(CUTE_TAILS)
    return s


LEX = [
    ("你好", "泥吼", 1), ("谢谢", "蟹蟹", 1), ("好", "吼", 1), ("很", "狠", 1),
    ("别", "别挤", 1), ("挤", "挤挤", 1), ("猫", "喵喵", 1), ("狗", "汪汪", 1),
    ("大家", "大挤", 1), ("说", "说说", 1),

    ("我", "窝", 2), ("你", "泥", 2), ("的", "嗝", 2), ("啊", "鸭", 2),
    ("喜欢", "稀饭", 2), ("开心", "开熏", 2), ("可爱", "阔爱", 2), ("太", "泰", 2),
    ("知道", "造", 2), ("没有", "米有", 2), ("可以", "阔以", 2),

    ("我们", "咱挤", 3), ("是", "系", 3), ("吗", "咩", 3), ("呢", "捏", 3),
    ("吧", "叭", 3), ("好吃", "吼吃", 3), ("名字", "名名", 3), ("语言", "语语", 3),
    ("这样", "酱", 3), ("真的", "真叽", 3), ("但是", "但素", 3), ("觉得", "觉着", 3),
    ("吃", "吃吃", 3), ("饭", "饭饭", 3), ("水", "水水", 3), ("来", "来来", 3),

    ("什么", "啥米", 4), ("为什么", "为啥米", 4), ("了", "辽", 4), ("不行", "不星", 4),
    ("说话", "说挤", 4), ("聊天", "聊挤", 4), ("新", "新新", 4), ("今天", "今挤", 4),
    ("一起", "一挤", 4), ("因为", "因喂", 4), ("然后", "然吼", 4), ("看", "看看", 4),
    ("去", "去去", 4), ("想", "想想", 4), ("要", "要要", 4), ("大", "大大", 4),
    ("小", "小小", 4), ("喝", "喝喝", 4), ("也", "也也", 4), ("茶", "茶茶", 4),
    ("家", "家家", 4), ("笑", "笑挤", 4),

    ("不", "不叽", 5), ("讨厌", "讨盐", 5), ("无聊", "无料", 5), ("词", "词词", 5),
    ("东西", "东挤", 5), ("快", "快挤", 5), ("睡", "睡睡", 5), ("那样", "酿", 5),
    ("再", "再再", 5), ("就", "就挤", 5), ("都", "都都", 5), ("听", "听听", 5),
    ("走", "走走", 5), ("讲", "讲挤", 5), ("饿", "饿饿", 5), ("累", "累累", 5),
    ("困", "困挤", 5), ("月亮", "月挤", 5), ("星星", "星挤", 5), ("歌", "歌歌", 5),
    ("哭", "哭挤", 5), ("有", "有挤", 5), ("两个", "两个挤", 5), ("现在", "现现", 5),
    ("奶茶", "茶奶奶", 5), ("所以", "所挤", 5), ("一点", "一挤点", 5),

    ("世界", "世挤", 6), ("人", "人挤", 6), ("慢", "慢挤", 6), ("感觉", "感挤", 6),
    ("如果", "如挤", 6), ("更", "更挤", 6), ("最", "最挤", 6), ("又", "又挤", 6),
    ("记得", "记挤", 6), ("忘", "忘挤", 6), ("饱", "饱饱", 6), ("天", "天天", 6),
    ("地", "地挤", 6), ("风", "风风", 6), ("雨", "雨挤", 6), ("云", "云挤", 6),
    ("太阳", "太挤", 6), ("梦", "梦挤", 6), ("一个", "一个叽", 6), ("多", "多多", 6),
    ("少", "少少", 6), ("明天", "明挤", 6), ("昨天", "昨挤", 6), ("爱", "爱爱", 6),

    ("电脑", "电挤", 7), ("手机", "手挤", 7), ("屏幕", "屏挤", 7), ("键盘", "键挤", 7),
    ("程序", "程挤", 7), ("终端", "终挤", 7), ("颜色", "色挤", 7), ("声音", "声挤", 7),
    ("音乐", "音挤", 7), ("游戏", "游挤", 7),

    ("大海", "海挤", 8), ("山", "山挤", 8), ("树", "树挤", 8), ("花", "花挤", 8),
    ("草", "草挤", 8), ("鱼", "鱼挤", 8), ("鸟", "鸟挤", 8), ("虫", "虫挤", 8),
    ("蝴蝶", "蝴挤", 8), ("天空", "空挤", 8),

    ("朋友", "朋挤", 9), ("老师", "师挤", 9), ("同学", "学挤", 9), ("工作", "工挤", 9),
    ("学校", "校挤", 9), ("商店", "店挤", 9), ("城市", "城挤", 9), ("路", "路挤", 9),
    ("车", "车挤", 9), ("门", "门挤", 9),

    ("时间", "时挤", 10), ("早上", "早挤", 10), ("中午", "午挤", 10), ("晚上", "晚挤", 10),
    ("睡觉", "睡挤", 10), ("起床", "起挤", 10), ("刷牙", "刷挤", 10), ("衣服", "衣挤", 10),
    ("鞋", "鞋挤", 10), ("眼镜", "镜挤", 10),
]

RULES = {
    1: "语气粒子「鸭」登场",
    2: "「的」挤成「嗝」",
    3: "「吗」→「咩」、「呢」→「捏」、「吧」→「叭」",
    4: "动词爱叠字：吃吃、看看、睡睡",
    5: "句尾随机挂「～啾」",
    6: "程度副词后置：「很好」→「好狠」",
    7: "「系」(是) 有时可以挤掉",
    8: "「嗝」也挤掉：「窝嗝喵喵」→「窝喵喵」",
    9: "双音节以上新词压成「头＋挤」",
    10: "新生语言诞生，句尾统一「～咩啾」",
}

STOP = {
    "你", "我", "他", "她", "它", "你们", "我们", "他们", "她们", "它们",
    "这", "那", "个", "们", "和", "与", "在", "给", "到", "过", "着",
    "把", "被", "让", "对", "从", "向", "会", "能", "没", "上", "下",
    "里", "外", "中", "还", "只", "也", "都", "得", "地", "又", "而",
    "或", "很", "太", "最", "更", "别", "不", "是", "的", "了", "吗",
    "呢", "吧", "啊", "哦", "嗯", "呀", "啦", "嘛", "呗", "哈", "嘿",
    "哎", "喂", "喔", "咯", "咯", "什么", "怎么", "为什么", "这样",
    "那样", "这个", "那个", "就是", "可以", "但是", "因为", "所以",
    "然后", "如果", "觉得", "知道", "现在", "今天", "明天", "昨天",
}

ADVERBS = {"很", "太", "最", "超级"}


class Conlang:
    def __init__(self, rng):
        self.rng = rng
        self._order = [z for z, _, _ in LEX]
        self.lex = {z: n for z, n, _ in LEX}
        self.eras = {z: e for z, _, e in LEX}
        self.converted = []
        self.dynamic = {}
        self.eras_done = []

    def reset(self):
        self.converted = []
        self.dynamic = {}
        self.eras_done = []

    def unconverted(self):
        return [z for z in self._order if z not in self.converted and z not in self.dynamic]

    def total_words(self):
        return len(LEX) + sum(1 for z in self.dynamic if z not in self.lex)

    def converted_count(self):
        return len(self.converted) + sum(1 for z in self.dynamic if z not in self.lex)

    def era_complete(self, e):
        return all(
            z in self.converted or z in self.dynamic
            for z, _, er in LEX if er <= e
        )

    def invent_next(self, style=None):
        z = self.unconverted()[0]
        new = invent_word(self.rng, style or self.rng.choice(["cute", "short"]))
        self.converted.append(z)
        return z, new

    def current_era(self):
        return max(self.eras_done) + 1 if self.eras_done else 1

    def progress(self):
        w = self.converted_count() / self.total_words() * 0.8
        r = len(self.eras_done) / len(RULES) * 0.2
        return min(1.0, w + r)

    def mapping(self):
        m = {z: self.lex[z] for z in self.converted}
        m.update(self.dynamic)
        return m

    @staticmethod
    def _compress(word):
        if len(word) <= 2:
            return word
        return word[:2] + "挤"

    def _postpose_adv(self, tokens):
        out = []
        i = 0
        while i < len(tokens):
            text, zh = tokens[i]
            if zh in ADVERBS and i + 1 < len(tokens) and tokens[i + 1][1] is not None:
                out.append(tokens[i + 1])
                out.append(tokens[i])
                i += 2
            else:
                out.append(tokens[i])
                i += 1
        return out

    @staticmethod
    def _drop_ge(tokens):
        out = []
        for i, t in enumerate(tokens):
            if t[0] == "嗝" and 0 < i < len(tokens) - 1 \
                    and tokens[i - 1][1] is not None and tokens[i + 1][1] is not None:
                continue
            out.append(t)
        return out

    def _suffixes(self, text):
        if not text:
            return text
        tail = ""
        while text and text[-1] in "。!?！？…":
            tail = text[-1] + tail
            text = text[:-1]
        if not text:
            return tail
        if 10 in self.eras_done:
            return text + "～咩啾" + tail
        r = self.rng.random()
        if 5 in self.eras_done and r < 0.35:
            return text + "～啾" + tail
        if 1 in self.eras_done and r < 0.3:
            return text + "鸭" + tail
        return text + tail

    def translate(self, text):
        mapping = self.mapping()
        if not mapping:
            return text, text
        keys = sorted(mapping, key=len, reverse=True)
        pat = re.compile("|".join(re.escape(k) for k in keys))
        tokens = []
        pos = 0
        for m in pat.finditer(text):
            if m.start() > pos:
                tokens.append((text[pos:m.start()], None))
            tokens.append((mapping[m.group(0)], m.group(0)))
            pos = m.end()
        if pos < len(text):
            tokens.append((text[pos:], None))

        if 6 in self.eras_done:
            tokens = self._postpose_adv(tokens)
        if 7 in self.eras_done and self.rng.random() < 0.5:
            tokens = [t for t in tokens if t[1] != "是"]
        if 8 in self.eras_done and self.rng.random() < 0.6:
            tokens = self._drop_ge(tokens)
        if 9 in self.eras_done:
            tokens = [
                (self._compress(t[0]), t[1]) if t[1] is not None and len(t[0]) > 2 else t
                for t in tokens
            ]
        conlang = "".join(t[0] for t in tokens)
        conlang = self._suffixes(conlang)
        return conlang, text

    def sample_converted(self, k=5):
        words = self.converted[-k:]
        return [(z, self.dynamic.get(z) or self.lex[z]) for z in words]
