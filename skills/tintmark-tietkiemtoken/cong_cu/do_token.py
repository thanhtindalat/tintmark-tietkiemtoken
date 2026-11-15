#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Bao cao token theo phien tu nhat ky Claude Code tren may (~/.claude/projects).

  python3 do_token.py [so_ngay=7] [--du-an CHUOI_LOC_DUONG_DAN]

Chi phi "quy doi" = vao moi x1 + ghi cache x1,25 + doc cache x0,1 + dau ra x5 (cung mot model).
So lieu la uoc tinh tu nhat ky, khong phai hoa don.
"""
import collections
import glob
import json
import os
import sys
import time

NGUONG = 300000


def main():
    so_ngay = 7.0
    loc = ''
    a = sys.argv[1:]
    while a:
        x = a.pop(0)
        if x == '--du-an' and a:
            loc = a.pop(0)
        else:
            try:
                so_ngay = float(x)
            except ValueError:
                pass
    han = time.time() - so_ngay * 86400
    phien = {}
    for f in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')):
        ma = os.path.basename(f)
        try:
            if os.path.getmtime(f) < han or ma in phien:
                continue
        except OSError:
            continue
        if loc and loc not in f:
            continue
        p = dict(f=f, ten='', luot=0, dinh=0, cuoi=0, q=0.0, cr=0, cw=0, out=0, inp=0,
                 tren=0, q_tren=0.0, vuot=0.0, nguoi=0, q_nguoi=0.0, model=collections.Counter())
        da = set()
        try:
            for dong in open(f, errors='ignore'):
                try:
                    d = json.loads(dong)
                except Exception:
                    continue
                if d.get('type') in ('custom-title', 'ai-title', 'summary'):
                    p['ten'] = d.get('customTitle') or d.get('aiTitle') or d.get('summary') or p['ten']
                m = d.get('message')
                if not isinstance(m, dict) or d.get('isSidechain'):
                    continue
                u = m.get('usage')
                if not isinstance(u, dict) or m.get('id') in da or m.get('model') == '<synthetic>':
                    continue
                da.add(m.get('id'))
                i = u.get('input_tokens') or 0
                cw = u.get('cache_creation_input_tokens') or 0
                cr = u.get('cache_read_input_tokens') or 0
                o = u.get('output_tokens') or 0
                q = i + 1.25 * cw + 0.1 * cr + 5 * o
                ctx = i + cw + cr
                p['luot'] += 1; p['q'] += q; p['cr'] += cr; p['cw'] += cw; p['out'] += o; p['inp'] += i
                p['dinh'] = max(p['dinh'], ctx); p['cuoi'] = ctx
                p['model'][m.get('model') or '?'] += q
                if ctx > NGUONG:
                    p['tren'] += 1; p['q_tren'] += q; p['vuot'] += q * (1 - NGUONG / ctx)
                if cw > 150000:
                    p['nguoi'] += 1; p['q_nguoi'] += 1.25 * cw
        except OSError:
            continue
        if p['luot']:
            phien[ma] = p
    ds = list(phien.values())
    if not ds:
        print('Khong co phien nao trong %g ngay.' % so_ngay)
        return
    T = sum(p['q'] for p in ds)
    S = lambda k: sum(p[k] for p in ds)
    print('== tintmark-tietkiemtoken (by Tintmark): %g ngay, %d phien, %d luot goi model' % (so_ngay, len(ds), S('luot')))
    print('Ty trong chi phi quy doi: doc cache %.0f%% | ghi cache %.0f%% | dau ra %.0f%% | vao moi %.0f%%' % (
        10 * S('cr') / T, 125 * S('cw') / T, 500 * S('out') / T, 100 * S('inp') / T))
    print('Luot co ngu canh > %dk: %.0f%% so luot, %.0f%% chi phi; phan vuot nguong (tran tiet kiem uoc tinh): %.0f%%' % (
        NGUONG // 1000, 100 * S('tren') / S('luot'), 100 * S('q_tren') / T, 100 * S('vuot') / T))
    print('Ghi lai ca phien vi cache nguoi (>150k / luot): %d lan, %.0f%% chi phi' % (S('nguoi'), 100 * S('q_nguoi') / T))
    mm = collections.Counter()
    for p in ds:
        mm.update(p['model'])
    print('Theo model (% chi phi): ' + ', '.join('%s %.0f%%' % (k, 100 * v / T) for k, v in mm.most_common(5)))
    b = collections.Counter()
    for p in ds:
        x = p['dinh']
        b['<100k' if x < 1e5 else '100-250k' if x < 2.5e5 else '250-300k' if x < 3e5 else '300-500k' if x < 5e5 else '>500k'] += 1
    print('Dinh ngu canh: ' + ', '.join('%s: %d' % (k, b[k]) for k in ('<100k', '100-250k', '250-300k', '300-500k', '>500k')))
    print('\nTop 15 phien (% chi phi | dinh k | hien tai k | luot | lan nguoi | model chinh | ten)')
    for p in sorted(ds, key=lambda p: -p['q'])[:15]:
        ten = p['ten'] or os.path.basename(os.path.dirname(p['f']))[-28:]
        print('  %5.1f%% %5d %5d %5d %3d  %-20s %s' % (100 * p['q'] / T, p['dinh'] // 1000, p['cuoi'] // 1000, p['luot'],
              p['nguoi'], p['model'].most_common(1)[0][0][-20:], ten[:50]))


if __name__ == '__main__':
    main()
