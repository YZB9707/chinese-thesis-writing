# -*- coding: utf-8 -*-
"""按《中文本科毕业论文写作》那份规范，审一遍稿子的硬规则。

用法：
    python rule_audit.py thesis.txt
    python rule_audit.py "C:/Users/联想/论文.docx"

读 .docx 需要 Hermes venv 的 python（装了 python-docx）；纯 .txt 用哪个都行。
退出码 1 = 有硬伤（第一人称／感叹号／破折号／段长无起伏／超长句扎堆／排比模板），
0 = 通过；标注“提示”的项不影响退出码。
"""
import argparse
import re
import statistics as st
import sys

HAN = re.compile(r"[\u4e00-\u9fa5]")
ROAD = ["具体来说", "首先", "其次", "再次", "接着", "最后", "凡是", "用来", "另外"]
FIRST_PERSON = ["我们", "咱们", "我"]


def han(s):
    return len(HAN.findall(s))


NL = chr(10)
SKIP = re.compile(r"^(第[一二三四五六七八九十]+[章节篇]|摘\s*要|关键词|目\s*录|参考文献|致\s*谢|附\s*录|注\s*释)")


def is_body(p):
    """标题、目录、摘要标签不算正文段落，否则段长统计全是噪声。"""
    if SKIP.match(p):
        return False
    if "………" in p or "......" in p:
        return False
    if han(p) < 25 and not re.search("[" + "。，；：" + "]", p):
        return False
    return han(p) >= 12 or p.endswith(("。", "？", "！"))


def load(path):
    if path.lower().endswith(".docx"):
        from docx import Document
        raw = [x.text.strip() for x in Document(path).paragraphs if x.text.strip()]
    else:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            raw = [x.strip() for x in re.split(NL + r"\s*" + NL, fh.read()) if x.strip()]
    return [x for x in raw if is_body(x)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--min-para", type=int, default=150)
    ap.add_argument("--max-para", type=int, default=260)
    ap.add_argument("--max-sent", type=int, default=30)
    ap.add_argument("--long-ratio", type=float, default=2.0)
    a = ap.parse_args()

    paras = load(a.path)
    text = "".join(paras)
    plens = [han(p) for p in paras]
    sents = [s.strip() for s in re.split(r"(?<=[。！？])", text) if s.strip()]
    slens = [han(s) for s in sents] or [0]
    commas = text.count("，") / max(1, text.count("。"))

    print(f"汉字 {han(text)}｜段 {len(paras)}｜句 {len(sents)}")
    print(f"句长 均值 {st.mean(slens):.1f}｜标准差 {st.pstdev(slens):.2f}（≥6 才有起伏）"
          f"｜最短 {min(slens)}｜最长 {max(slens)}｜逗号÷句号 {commas:.2f}")
    print(f"段长 {plens}")

    # ---- 句子节拍：判 24% 那类“段落对了、句长还是齐”的稿子 ----
    longn = sum(1 for x in slens if x > 25)
    share = longn / max(1, len(sents)) * 100
    print(f">25 字长句 {longn}/{len(sents)} = {share:.1f}%（4%—6% 自然；接近 0 说明一句长句都没有）")
    psent = [len([s for s in re.split(r"(?<=[。！？])", p) if s.strip()]) for p in paras]
    print(f"段内句数 {psent}")
    if psent and min(psent) > 0:
        print(f"段内句数 最小 {min(psent)} / 最大 {max(psent)} = {max(psent) / min(psent):.2f}（≥3 才算不齐）")
    pairs = re.findall(r"[\u4e00-\u9fa5]{2,5}，[\u4e00-\u9fa5]{2,5}。", text)
    if pairs:
        print(f"对仗短对（≤5 字对≤5 字）{len(pairs)} 处，平均每 {len(sents) / len(pairs):.1f} 句一处")
        if len(pairs) > len(sents) / 6:
            print(f"提示：对仗密于每 6 句一处，{pairs[:6]} 这类拆到 3—4 处")
    dic = text.count("这一点")
    if dic > 2:
        print(f"提示：指代词“这一点”{dic} 次（上限 2），换成具体指代")
    tab = len(re.findall(r"表\s*\d+\s*是", text))
    if tab > 1:
        print(f"提示：“表 X 是……”句式用了 {tab} 次，第二次起换说法")

    bad = []
    for w in FIRST_PERSON:
        if w in text:
            bad.append(f"第一人称「{w}」出现 {text.count(w)} 次")
    if "！" in text:
        bad.append(f"感叹号 {text.count('！')} 个")
    if "——" in text:
        bad.append(f"破折号 {text.count('——')} 处")

    if plens:
        lo, hi = min(plens), max(plens)
        if hi < lo * a.long_ratio:
            bad.append(f"段长无起伏：最长 {hi} / 最短 {lo} = {hi / lo:.2f}，要 ≥{a.long_ratio}（挑数据最密的两段并成长段）")
        short = [(i + 1, n) for i, n in enumerate(plens) if n < a.min_para]
        long_ = [(i + 1, n) for i, n in enumerate(plens) if n > a.max_para]
        if short:
            print(f"提示：{len(short)} 段短于 {a.min_para} 字 {short[:6]}（摘要／致谢可放过）")
        if long_:
            print(f"提示：{len(long_)} 段长于 {a.max_para} 字 {long_[:6]}")

    over = [(slens[i], sents[i][:26]) for i in range(len(sents)) if slens[i] > a.max_sent]
    for ln, head in over:
        print(f"  超长句 {ln} 字：{head}…")
    if len(over) > 3:
        bad.append(f"{len(over)} 句超过 {a.max_sent} 字（在最接近中点的逗号处断开）")

    pare = re.findall(r"[^。！？；]*、[^。！？；]*、[^。！？；]*", text)
    if pare:
        print(f"提示：顿号连排（一句里 ≥2 个顿号）{len(pare)} 处")
    road = {w: text.count(w) for w in ROAD if text.count(w)}
    if road:
        print(f"提示：排步骤号路标词 {road}")
    trans = [s for s in sents if han(s) <= 12 and s.startswith(("于是", "研究的意义", "问题的另一半", "小结", "总之", "可见"))]
    if trans:
        print(f"提示：零信息过渡句候选 {trans[:6]}")

    for i, p in enumerate(paras):
        if len(re.findall(r"对[^，。]{2,6}来说", p)) >= 2:
            bad.append(f"第 {i + 1} 段「对……来说」两句同构，属排比")
        if p.count("研究说") + p.count("研究主张") + p.count("研究指出") >= 3:
            bad.append(f"第 {i + 1} 段「X 研究说……」三连同构，属排比")
    if "首先" in text and "其次" in text:
        bad.append("用了「首先……其次……」排步骤号")

    print()
    if bad:
        for b in bad:
            print("✗", b)
        sys.exit(1)
    print("✓ 硬规则通过（提示项仍要看）")


if __name__ == "__main__":
    main()
