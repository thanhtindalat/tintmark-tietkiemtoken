#!/usr/bin/env python3
"""Hook tintmark-token: do nguong ngu canh cua phien va nhac vong lap cho quyet.

Noi vao ~/.claude/settings.json cho su kien UserPromptSubmit va PostToolUse.
Doc JSON cua hook tu stdin (session_id, transcript_path, cwd, hook_event_name).
Duoi nguong va khong co gi can nhac: khong in gi (0 token).
Moi loi deu bi nuot va thoat 0 de khong bao gio chan phien lam viec.
"""
import json
import os
import sys
import time

GOC = os.environ.get('TINTMARK_TOKEN_DIR') or os.path.expanduser('~/.claude/tintmark-token')
GOC_CU = os.path.expanduser('~/.claude/ti-token')   # ten thu muc truoc khi doi ten skill (15/11/2026)
NEN = os.environ.get('NEN_DATA_DIR') or os.path.expanduser('~/.claude/plugin-tintmark-tietkiem')
if not os.environ.get('NEN_DATA_DIR') and not os.path.exists(NEN) and os.path.isdir(os.path.expanduser('~/.claude/plugin-nen-token')):
    NEN = os.path.expanduser('~/.claude/plugin-nen-token')   # chua chuyen du lieu sau khi doi ten plugin (15/11/2026)
MAC_DINH = {
    'nhac': 250000,          # bao nguoi dung, viet ban giao
    'doi': 300000,           # khong nhan viec moi, mo phien ke nhiem
    'buoc_nhac_lai': 50000,  # sau khi da nhac, nhac lai moi lan tang them chung nay
    'nhac_vong_lap_gio': 12,  # nhac muc cho quyet toi da 1 lan / chung nay gio
    'quet_vong_lap_ngay': 7,  # goi y quet lai vong lap sau chung nay ngay
    'cho_giay': 8,           # tin nguoi dung gui khi da qua nguong doi: giu lai chung nay giay roi moi cho qua (0 = khong cho)
}
CAU_MOI = 'Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới.'
THE = ('tạo MỘT thẻ kế nhiệm (start_session "own_initiative", "fresh", tên cũ + số; lời giao = lệnh bàn giao, '
       'gồm bước lưu trữ phiên cũ theo dòng Chuỗi phiên (archive_session, chỉ giữ 2 phiên mới nhất) và ghi id mới vào sổ phiên; mô tả có câu "%s")' % CAU_MOI)


def doc_json(duong, mac_dinh):
    try:
        with open(duong, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return mac_dinh


def ghi_json(duong, du_lieu):
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    tam = duong + '.tam%d' % os.getpid()
    with open(tam, 'w', encoding='utf-8') as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=1)
    os.replace(tam, duong)


def cau_hinh(cwd):
    c = dict(MAC_DINH)
    c.update({k: v for k, v in doc_json(os.path.join(GOC, 'cau_hinh.json'), {}).items() if k in MAC_DINH})
    # cau hinh rieng: tim tu cwd len toi thu muc goc
    d = cwd or ''
    for _ in range(8):
        if not d or d == os.path.dirname(d):
            break
        rieng = doc_json(os.path.join(d, '.claude', 'tintmark-token.json'), None)
        if isinstance(rieng, dict):
            c.update({k: v for k, v in rieng.items() if k in MAC_DINH})
            break
        d = os.path.dirname(d)
    return c


def ngu_canh(nhat_ky):
    """So token ngu canh o luot goi model gan nhat cua phien chinh (bo subagent)."""
    try:
        co = os.path.getsize(nhat_ky)
    except OSError:
        return 0
    for doc in (400000, 4000000, 40000000):
        with open(nhat_ky, 'rb') as f:
            f.seek(max(0, co - doc))
            khoi = f.read().decode('utf-8', 'ignore')
        for dong in reversed(khoi.splitlines()):
            if '"usage"' not in dong:
                continue
            try:
                d = json.loads(dong)
            except Exception:
                continue
            if d.get('isSidechain'):
                continue
            m = d.get('message')
            if not isinstance(m, dict) or m.get('model') == '<synthetic>':
                continue
            u = m.get('usage')
            if not isinstance(u, dict):
                continue
            return sum(int(u.get(k) or 0) for k in (
                'input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'))
        if doc >= co:
            break
    return 0


def nhac_nguong(vao, c, su_kien='UserPromptSubmit'):
    phien = str(vao.get('session_id') or '')
    nhat_ky = vao.get('transcript_path') or ''
    if not phien or not nhat_ky:
        return None
    n = ngu_canh(nhat_ky)
    if n < c['nhac']:
        return None
    tep = os.path.join(GOC, 'trang_thai', phien.replace('/', '_') + '.json')
    tt = doc_json(tep, {})
    if not isinstance(tt, dict):
        tt = {}
    muc = 2 if n >= c['doi'] else 1
    da_muc = int(tt.get('muc') or 0)
    da_n = int(tt.get('n') or 0)
    if n < da_n - 50000:      # phien vua duoc nen / don: tinh lai tu dau
        da_muc, da_n = 0, 0
    nay = time.time()
    k = n // 1000
    the = '' if tt.get('the_da_tao') else ' Chưa có thẻ thì %s.' % THE
    if muc == 2 and su_kien == 'UserPromptSubmit':
        # Tin gui len khi da qua nguong doi: nhac o MOI luot (khong chi mot lan), va giu tin lai vai giay.
        if nay - float(tt.get('luc_doi') or 0) < 3:     # hook noi trung (settings + plugin) chay cung luc: mot cai noi
            return None
        ghi_json(tep, dict(tt, muc=2, n=max(n, da_n), luc=int(nay), luc_doi=nay, the_da_tao=True))
        try:
            cho = min(float(c.get('cho_giay') or 0), 30)
            if cho > 0:
                time.sleep(cho)
        except Exception:
            pass
        return ('[tintmark-token] ĐỔI PHIÊN: %dk token (> %dk). KHÔNG làm việc vừa gửi ở phiên này; chốt tệp bàn giao (ban-giao.md). '
                '(a) Người dùng gõ: start_session "user_asked", "fresh", tên cũ + số; lời giao CHỈ gồm lệnh bàn giao '
                '(lưu trữ phiên cũ theo dòng Chuỗi phiên, id phiên này: %s) + NGUYÊN VĂN tin vừa gửi; trả lời một dòng "%s" kèm link. '
                '(b) Tin do phiên khác gửi / sự kiện tự động:%s Trả lời một dòng "phiên đã đầy, gửi lại cho phiên <tên mới> sau khi người dùng bấm Bắt đầu". '
                'Sau đó lưu trữ phiên này, không nhắn nữa.'
                % (k, c['doi'] // 1000, phien, CAU_MOI, the))
    if muc <= da_muc and n < da_n + c['buoc_nhac_lai']:
        return None
    ghi_json(tep, dict(tt, muc=muc, n=n, luc=int(nay), the_da_tao=True))
    if muc == 1:
        return ('[tintmark-token] NHẮC: %dk token (nhắc %dk, đổi %dk). Câu đầu trả lời: "Phiên đã %dk token. %s" '
                'Cập nhật tệp bàn giao (ban-giao.md: dưới ~1.500 chữ, chỉ trỏ đường dẫn); dòng Chuỗi phiên có id thật, id phiên này: %s.%s '
                'Xong việc dở, không mở việc lớn mới.'
                % (k, c['nhac'] // 1000, c['doi'] // 1000, k, CAU_MOI, phien, the))
    return ('[tintmark-token] ĐỔI PHIÊN: %dk token (> %dk). Không nhận việc mới; dừng ở điểm an toàn, chốt tệp bàn giao.%s Báo: "%s" '
            'Lượt người dùng gõ: mở phiên kế nhiệm mới hoàn toàn (fresh, không fork), lời giao = lệnh bàn giao, tên cũ + số. '
            'Sau đó lưu trữ phiên này, không nhắn nữa.'
            % (k, c['doi'] // 1000, the, CAU_MOI))


def nhac_vong_lap(vao, c):
    """Chi chay o UserPromptSubmit: nhac muc cho quyet, bao muc qua han, goi y quet lai."""
    tep = os.path.join(GOC, 'vong_lap.json')
    so = doc_json(tep, None)
    if not isinstance(so, dict):
        return None
    nay = time.time()
    cwd = os.path.realpath(vao.get('cwd') or '')
    dong = []
    doi = False
    for ma, m in sorted((so.get('muc') or {}).items()):
        if not isinstance(m, dict) or m.get('trang_thai') != 'cho':
            continue
        han = float(m.get('han') or 0)
        nhac_cuoi = float(m.get('nhac_cuoi') or 0)
        ten = m.get('ten') or ma
        if han and nay > han:
            if nay - nhac_cuoi < 6 * 3600:
                continue
            dong.append('QUÁ HẠN không ai trả lời: tạm dừng (không xoá) vòng lặp "%s" (id %s, loại %s) bằng công cụ '
                        'tương ứng, chạy `vong_lap.py da-tat --id %s`, rồi báo người dùng một dòng là đã tự tắt và cách bật lại.'
                        % (ten, ma, m.get('loai') or '?', ma))
        else:
            du_an = os.path.realpath(m['du_an']) if m.get('du_an') else ''
            if du_an and not (cwd == du_an or cwd.startswith(du_an + os.sep)):
                continue
            if nay - nhac_cuoi < float(c['nhac_vong_lap_gio']) * 3600:
                continue
            han_chu = time.strftime('%d/%m %H:%M', time.localtime(han)) if han else 'chưa đặt'
            dong.append('Chờ người dùng quyết: tắt vòng lặp "%s" (id %s, %s; lý do: %s)? Hạn %s, quá hạn sẽ tự tắt. '
                        'Nhắc người dùng một dòng ở cuối câu trả lời; họ trả lời thì chạy `vong_lap.py tra-loi --id %s --tat|--giu`.'
                        % (ten, ma, m.get('tan_suat') or '?', m.get('ly_do') or '?', han_chu, ma))
        m['nhac_cuoi'] = nay
        doi = True
    quet = float(so.get('lan_quet_cuoi') or 0)
    nhac_quet = float(so.get('lan_nhac_quet') or 0)
    ngay = float(c['quet_vong_lap_ngay']) * 86400
    if quet and nay - quet > ngay and nay - nhac_quet > ngay:
        dong.append('Đã hơn %d ngày chưa quét vòng lặp / lịch tự chạy. Khi xong việc đang làm, quét theo tintmark-token (don-ngu-canh.md mục 2).'
                    % int(c['quet_vong_lap_ngay']))
        so['lan_nhac_quet'] = nay
        doi = True
    if doi:
        ghi_json(tep, so)
    if not dong:
        return None
    return '[tintmark-token] VÒNG LẶP: ' + ' | '.join(dong)


def chuyen_du_lieu_cu():
    """So vong lap / cau hinh con nam o thu muc ten cu thi chep sang (khong xoa ban cu)."""
    if os.environ.get('TINTMARK_TOKEN_DIR'):
        return
    for ten in ('cau_hinh.json', 'vong_lap.json'):
        moi, cu = os.path.join(GOC, ten), os.path.join(GOC_CU, ten)
        if not os.path.exists(moi) and os.path.isfile(cu):
            d = doc_json(cu, None)
            if d is not None:
                ghi_json(moi, d)


def thong_bao_plugin():
    """Hang cho thong bao cua plugin tintmark-tietkiem (bo loc tu tat, ban moi, cap nhat hong): in mot lan roi xoa."""
    tep = os.path.join(NEN, 'thong_bao.json')
    ds = doc_json(tep, None)
    if not isinstance(ds, list) or not ds:
        return None
    ghi_json(tep, [])
    return '[tintmark-tietkiem] ' + ' | '.join(str(x) for x in ds[:5]) + ' (Báo người dùng một dòng.)'


def nhac_phan_hoi_cu():
    """Phan hoi con mo qua 3 ngay: bao mot dong, toi da 1 lan / 24 gio (moc phan_hoi_lan_nhac)."""
    goc = os.path.join(NEN, 'phan_hoi')
    if not os.path.isdir(goc):
        return None
    moc = os.path.join(NEN, 'phan_hoi_lan_nhac')
    try:
        if time.time() - os.path.getmtime(moc) < 86400:
            return None
    except OSError:
        pass
    cu = []
    for ten in sorted(os.listdir(goc)):
        m = doc_json(os.path.join(goc, ten, 'meta.json'), None)
        if isinstance(m, dict) and m.get('trang_thai', 'mo') != 'dong' and time.time() - float(m.get('luc') or time.time()) > 3 * 86400:
            cu.append(ten)
    if not cu:
        return None
    with open(moc, 'w') as f:
        f.write(str(int(time.time())))
    return ('[tintmark-tietkiem] %d phản hồi mở quá 3 ngày (%s). Xử lý theo tu-sua.md hoặc đóng bằng phan_hoi.py dong. '
            '(Báo người dùng một dòng.)' % (len(cu), ', '.join(cu[:3])))


def kiem_cap_nhat():
    """Moi 24 gio goi nen `cap_nhat.py tu-dong` (neu la ban plugin); khong cho, khong in gi."""
    kich = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                        'scripts', 'cap_nhat.py')
    if not os.path.isfile(kich):
        return
    moc = os.path.join(NEN, 'cap_nhat_lan_kiem')
    try:
        if time.time() - os.path.getmtime(moc) < 86400:
            return
    except OSError:
        pass
    os.makedirs(NEN, exist_ok=True)
    with open(moc, 'w') as f:
        f.write(str(int(time.time())))
    import subprocess
    subprocess.Popen([sys.executable, kich, 'tu-dong'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)


def main():
    try:
        vao = json.loads(sys.stdin.read() or '{}')
    except Exception:
        return
    if not isinstance(vao, dict):
        return
    su_kien = vao.get('hook_event_name') or 'UserPromptSubmit'
    try:
        chuyen_du_lieu_cu()
    except Exception:
        pass
    c = cau_hinh(vao.get('cwd') or '')
    tin = []
    a = nhac_nguong(vao, c, su_kien)
    if a:
        tin.append(a)
    if su_kien == 'UserPromptSubmit':
        for ham in (lambda: nhac_vong_lap(vao, c), thong_bao_plugin, nhac_phan_hoi_cu):
            try:
                b = ham()
            except Exception:
                b = None
            if b:
                tin.append(b)
        try:
            kiem_cap_nhat()
        except Exception:
            pass
    if tin:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': su_kien, 'additionalContext': '\n'.join(tin)}},
                         ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
