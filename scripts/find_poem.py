#!/usr/bin/env python3
"""查《诗经》：按篇名或关键句检索，输出全文。

用法:
  python3 find_poem.py 褰裳            # 按篇名精确查
  python3 find_poem.py --grep 同袍     # 按诗句关键词查（列出所在篇目及上下文）
"""
import sys, os, re

TEXT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'shijing.txt')

def load():
    raw = open(TEXT, encoding='utf-8').read()
    # 篇名 = 单独成行、不含标点的短行；正文行含逗号句号
    poems, cur, cur_section = [], None, ''
    for line in raw.split('\n'):
        s = line.strip()
        if not s:
            continue
        if re.match(r'^(国风|小雅|大雅|周颂|鲁颂|商颂|颂)[·．]?', s) or s.endswith('之什') or s == '《诗经》全集':
            cur_section = s
            continue
        if len(s) <= 6 and not re.search(r'[，。？！、；：]', s):
            cur = {'title': s, 'section': cur_section, 'lines': []}
            poems.append(cur)
        elif cur:
            cur['lines'].append(s)
    # 源文本个别段落重复收录，按 (篇名, 国风, 正文) 去重
    seen, uniq = set(), []
    for p in poems:
        key = (p['title'], p['section'], tuple(p['lines']))
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    poems = load()
    if args[0] == '--grep':
        kw = args[1]
        for p in poems:
            for l in p['lines']:
                if kw in l:
                    print(f"《{p['title']}》({p['section']}): {l}")
        return
    kw = args[0].strip('《》')
    hits = [p for p in poems if kw == p['title'] or kw in p['title']]
    if not hits:
        print(f"未找到《{kw}》。可能是逸诗（如《茅鸱》《新宫》《辔之柔矣》《河水》），或试 --grep 按句检索。")
        return
    if len(hits) > 1:
        print(f"注意：《{kw}》有 {len(hits)} 篇同名，务必按国风分辨（如子产赋'郑之《羔裘》'）：\n")
    for p in hits:
        print(f"《{p['title']}》 · {p['section']}")
        print('\n'.join(p['lines']))
        print()

if __name__ == '__main__':
    main()
