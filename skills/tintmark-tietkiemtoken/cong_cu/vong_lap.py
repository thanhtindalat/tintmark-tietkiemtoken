#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""So vong lap cho quyet cua tintmark-tietkiemtoken (~/.claude/tintmark-tietkiemtoken/vong_lap.json).

  vong_lap.py de-xuat --id ID --ten "..." --loai lich|cron|nen|khac --tan-suat "..." --ly-do "..." [--du-an DUONG_DAN] [--han-gio 48]
  vong_lap.py tra-loi --id ID --tat | --giu [--ra-lai-ngay 30]
  vong_lap.py da-tat  --id ID [--tu-dong]
  vong_lap.py da-quet
  vong_lap.py liet-ke

Script chi ghi so. Viec tat that (tam dung lich, xoa cron, dung tien trinh) do phien lam bang cong cu tuong ung.
"""
import argparse
import json
import os
import time

_GOC = os.environ.get('TINTMARK_TOKEN_DIR') or os.path.expanduser('~/.claude/tintmark-tietkiemtoken')
if not os.environ.get('TINTMARK_TOKEN_DIR') and not os.path.exists(_GOC) and os.path.isdir(os.path.expanduser('~/.claude/tintmark-token')):
    _GOC = os.path.expanduser('~/.claude/tintmark-token')   # ten cu truoc 15/11/2026
TEP = os.path.join(_GOC, 'vong_lap.json')


def doc():
    try:
        with open(TEP, encoding='utf-8') as f:
            d = json.load(f)
            if isinstance(d, dict):
                d.setdefault('muc', {})
                return d
    except Exception:
        pass
    return {'muc': {}}


def ghi(d):
    os.makedirs(os.path.dirname(TEP), exist_ok=True)
    tam = TEP + '.tam'
    with open(tam, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tam, TEP)


def gio(t):
    return time.strftime('%d/%m/%Y %H:%M', time.localtime(t)) if t else '-'


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest='lenh', required=True)
    a = s.add_parser('de-xuat')
    a.add_argument('--id', required=True); a.add_argument('--ten', required=True)
    a.add_argument('--loai', default='lich'); a.add_argument('--tan-suat', default='')
    a.add_argument('--ly-do', default=''); a.add_argument('--du-an', default='')
    a.add_argument('--han-gio', type=float, default=48)
    b = s.add_parser('tra-loi')
    b.add_argument('--id', required=True)
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument('--tat', action='store_true'); g.add_argument('--giu', action='store_true')
    b.add_argument('--ra-lai-ngay', type=float, default=30)
    c = s.add_parser('da-tat'); c.add_argument('--id', required=True); c.add_argument('--tu-dong', action='store_true')
    s.add_parser('da-quet'); s.add_parser('liet-ke')
    o = p.parse_args()
    d = doc(); nay = time.time()
    if o.lenh == 'de-xuat':
        cu = d['muc'].get(o.id) or {}
        if cu.get('trang_thai') == 'giu' and nay < float(cu.get('ra_lai') or 0):
            print('Bo qua: nguoi dung da chon GIU "%s" toi %s.' % (o.id, gio(cu.get('ra_lai'))))
            return
        if cu.get('trang_thai') == 'cho':
            print('Da co de xuat cho quyet cho "%s", han %s.' % (o.id, gio(cu.get('han'))))
            return
        d['muc'][o.id] = {'ten': o.ten, 'loai': o.loai, 'tan_suat': o.tan_suat, 'ly_do': o.ly_do,
                          'du_an': os.path.abspath(o.du_an) if o.du_an else '', 'trang_thai': 'cho',
                          'de_xuat_luc': nay, 'han': nay + o.han_gio * 3600, 'nhac_cuoi': nay}
        ghi(d)
        print('Da ghi de xuat tat "%s". Han tra loi: %s (qua han tu tat).' % (o.ten, gio(nay + o.han_gio * 3600)))
    elif o.lenh == 'tra-loi':
        m = d['muc'].get(o.id)
        if not m:
            print('Khong co muc', o.id); return
        if o.giu:
            m.update(trang_thai='giu', tra_loi_luc=nay, ra_lai=nay + o.ra_lai_ngay * 86400)
            print('GIU "%s"; ra lai sau %s.' % (m['ten'], gio(m['ra_lai'])))
        else:
            m.update(trang_thai='dong_y_tat', tra_loi_luc=nay)
            print('Nguoi dung DONG Y tat "%s": hay tat that roi chay da-tat.' % m['ten'])
        ghi(d)
    elif o.lenh == 'da-tat':
        m = d['muc'].get(o.id)
        if not m:
            print('Khong co muc', o.id); return
        m.update(trang_thai='da_tat', tat_luc=nay, tu_dong=bool(o.tu_dong or m.get('trang_thai') == 'cho'))
        ghi(d)
        print('Da ghi: "%s" da tat luc %s%s.' % (m['ten'], gio(nay), ' (tu dong vi qua han)' if m['tu_dong'] else ''))
    elif o.lenh == 'da-quet':
        d['lan_quet_cuoi'] = nay
        ghi(d)
        print('Da ghi lan quet:', gio(nay))
    else:
        print('Lan quet cuoi:', gio(d.get('lan_quet_cuoi')))
        for ma, m in sorted(d['muc'].items()):
            them = {'cho': 'han ' + gio(m.get('han')), 'giu': 'ra lai ' + gio(m.get('ra_lai')),
                    'da_tat': 'tat luc ' + gio(m.get('tat_luc'))}.get(m.get('trang_thai'), '')
            print('- [%s] %s | %s | %s | %s | %s' % (m.get('trang_thai'), ma, m.get('ten'), m.get('tan_suat'), m.get('ly_do'), them))


if __name__ == '__main__':
    main()
