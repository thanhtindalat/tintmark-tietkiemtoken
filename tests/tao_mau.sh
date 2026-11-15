# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
set -e
R=$1/du_an_mau; rm -rf $R; mkdir -p $R; cd $R
export GIT_AUTHOR_NAME="Vi Du" GIT_AUTHOR_EMAIL="vidu@example.com" GIT_COMMITTER_NAME="Vi Du" GIT_COMMITTER_EMAIL="vidu@example.com"
git init -q -b main .
mkdir -p tools src extension
for i in $(seq 0 11); do
  { echo "\"\"\"Công cụ mẫu $i.\"\"\""; for j in $(seq 0 26); do echo "def ham_${i}_${j}(x, y=None):"; echo "    return (x, y, $j)"; echo; done; } > tools/cong_cu_$i.py
done
for i in $(seq 0 399); do d=src/goi_$((i/20)); mkdir -p $d; echo "GIA_TRI = $i" > $d/mo_dun_$i.py; done
for i in $(seq 0 109); do echo "// tệp $i" > extension/tep_$i.js; done
echo "// nền" > extension/background.js
git add -A; git commit -q -m "Khởi tạo dự án mẫu"
for c in $(seq 1 320); do
  f=src/goi_$((c%20))/mo_dun_$((c%400)).py
  for k in $(seq 1 6); do echo "# thay đổi $c dòng $k" >> $f; done
  echo "def ham_moi_$c(): return $c" >> tools/cong_cu_$((c%12)).py
  git commit -q -am "Sửa mô-đun $((c%400)): thêm xử lý trường hợp $c"
done
