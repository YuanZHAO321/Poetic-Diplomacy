#!/usr/bin/env python3
"""查《尚书》：按篇名或关键句检索。

用法:
  python3 find_shu.py 康诰             # 按篇名调出全篇（自动标注今文/伪古文）
  python3 find_shu.py --grep 明德慎罚   # 按句检索，输出所在篇与上下文

注意：《左传》引《书》与今本常有一两字之异（如↔若、弗↔不、人↔民、
懋↔茂、沉↔沈）。--grep 查不到时换异文字再试；仍不见者按逸书处理。
"""
import sys, os, re

TEXT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'shangshu.txt')

# 东晋梅赜本晚出二十五篇（伪古文）：引文若仅见于这些篇，
# 多为伪古文作者反向抄撮《左传》等先秦引文而成，不可倒果为因。
WEIGUWEN = {'大禹谟','五子之歌','胤征','仲虺之诰','汤诰','伊训',
            '太甲上','太甲中','太甲下','咸有一德','说命上','说命中','说命下',
            '泰誓上','泰誓中','泰誓下','武成','旅獒','微子之命','蔡仲之命',
            '周官','君陈','毕命','君牙','冏命'}
SECTIONS = {'虞书','夏书','商书','周书'}

def load():
    chapters, cur, cur_section = [], None, ''
    for line in open(TEXT, encoding='utf-8'):
        s = line.strip()
        if not s:
            continue
        s = re.sub(r'^◎(虞|夏|商|周)书[·．]', '', s)  # "◎周书·泰誓上" → "泰誓上"
        if s in SECTIONS:
            cur_section = s
            continue
        if len(s) <= 8 and not re.search(r'[，。？！、；：“”]', s):
            cur = {'title': s, 'section': cur_section, 'lines': []}
            chapters.append(cur)
        elif cur:
            cur['lines'].append(s)
    return chapters

def tag(t):
    return '伪古文·晚出' if t in WEIGUWEN else '今文'

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    chapters = load()
    if args[0] == '--grep':
        kw = args[1]
        found = False
        for c in chapters:
            for l in c['lines']:
                if kw in l:
                    found = True
                    i = l.find(kw)
                    print(f"《{c['title']}》({c['section']}·{tag(c['title'])}): "
                          f"…{l[max(0,i-20):i+len(kw)+30]}…")
        if not found:
            print(f"未找到「{kw}」。试异文（如↔若、弗↔不、人↔民、懋↔茂），仍无则为逸书。")
        return
    kw = args[0].strip('《》')
    hits = [c for c in chapters if kw == c['title'] or kw in c['title']]
    if not hits:
        print(f"未找到《{kw}》篇。今本五十八篇之外者为逸篇。")
        return
    for c in hits:
        print(f"《{c['title']}》 · {c['section']} · {tag(c['title'])}")
        print('\n'.join(c['lines']))
        print()

if __name__ == '__main__':
    main()
