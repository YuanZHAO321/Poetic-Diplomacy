#!/usr/bin/env python3
"""查《左传》：按年调阅或按关键词全文检索（log 检索接口）。

用法:
  python3 find_zuo.py --grep 吕相绝秦          # 全文检索，自动标注年份，默认前 8 处
  python3 find_zuo.py --grep 赋 20             # 第二个参数放宽命中上限
  python3 find_zuo.py --year 僖公二十三年       # 调阅该年全部经传
  python3 find_zuo.py --year 成公十三年 绝秦    # 只输出该年中含关键词的段落

用途：核对事例库（episodes.md）之外的先例细节、调出名辞令全文、
验证"某年某人说过某话"。援引《左传》原文前先来这里核实。
"""
import sys, os, re

TEXT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'zuozhuan.txt')

def load():
    raw = open(TEXT, encoding='utf-8').read()
    flat = raw.replace('\n', '')          # 源文本硬换行排版，压平便于检索
    years = [(m.start(), m.group(1)) for m in re.finditer(r'◇(\S+?年)', flat)]
    return flat, years

def year_at(flat, years, pos):
    cur = '（隐公篇首）'
    for p, y in years:
        if p <= pos: cur = y
        else: break
    return cur

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); return
    flat, years = load()
    mode, key = args[0], args[1]
    if mode == '--grep':
        limit = int(args[2]) if len(args) > 2 else 8
        hits = [m.start() for m in re.finditer(re.escape(key), flat)]
        if not hits:
            print(f"未找到「{key}」。人名地名多有异写（如吕相/魏相），换写法或缩短关键词再试。")
            return
        print(f"共 {len(hits)} 处" + (f"，显示前 {limit} 处（加数字参数可放宽）" if len(hits) > limit else "") + "：\n")
        for pos in hits[:limit]:
            print(f"〖{year_at(flat, years, pos)}〗…{flat[max(0,pos-100):pos+200]}…\n")
    elif mode == '--year':
        key = key.strip('◇')
        spans = []
        for i, (p, y) in enumerate(years):
            if y == key:
                end = years[i+1][0] if i+1 < len(years) else len(flat)
                spans.append((p, end))
        if not spans:
            print(f"未找到「{key}」。年份写法须与原书一致，如：僖公二十三年、襄公二十七年。")
            return
        for p, end in spans:
            body = flat[p:end]
            if len(args) > 2:                 # 年内关键词过滤：命中点前 200 后 800 字开窗，重叠合并
                kw = args[2]
                hits = [m.start() for m in re.finditer(re.escape(kw), body)]
                if not hits:
                    print(f"（{key} 内未见「{kw}」）")
                    continue
                windows, last_end = [], -1
                for h in hits:
                    s, e = max(0, h-200), min(len(body), h+800)
                    if s <= last_end:
                        windows[-1] = (windows[-1][0], e)
                    else:
                        windows.append((s, e))
                    last_end = e
                body = '\n…\n'.join(f"…{body[s:e]}…" for s, e in windows)
            print(body)
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
