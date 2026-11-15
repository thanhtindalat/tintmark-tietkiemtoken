# Đo và báo số tiết kiệm cho trung thực

Công cụ đo trên máy: `cong_cu/do_token.py`, `scripts/thong_ke.py` của plugin (`nen-lenh.md`).

## 1. Nguyên tắc số liệu

- **Chi tiêu khác tiết kiệm.** Chi tiêu là cái một khoảng thời gian ĐÃ tốn; luôn nói rõ khoảng thời gian, không nhân ra tháng / năm.
- **Tiết kiệm là "chưa biết"** khi chưa có so sánh đo được trên cùng đầu vào, có và không có thay đổi. Số dự kiến trong kế hoạch vẫn được nêu nhưng phải ghi "ước tính".
- Chênh kích thước trước / sau nén chỉ là số byte của output đó, chưa phải tiền: `thong_ke.py` báo "đã nén bao nhiêu ký tự", không báo "đã tiết kiệm bao nhiêu tiền".
- Gói thuê bao: chi phí biên bằng 0; số tiền chỉ là giá trị quy đổi theo giá API, thứ thật sự bị giới hạn là hạn mức.
- Không cộng gộp các loại bằng chứng thành một con số đẹp. Xếp từ mạnh tới yếu: (1) đo lại đúng thứ đã sửa; (2) bật / tắt luân phiên trên cùng việc; (3) so trước / sau theo thời gian, không đối chứng; (4) đã ghi nhận nhưng chưa quy được, không tính là tiết kiệm.
- Luôn nêu yếu tố gây nhiễu, nhất là khi kết quả đẹp (tuần đó ít việc, đổi model, đổi số phiên). Phiên rẻ hơn mà lỗi nhiều hơn thì không phải tiết kiệm.
- Kết quả tệ báo thẳng, kèm cách hoàn tác.

## 2. Đánh giá một thay đổi tối ưu

1. Chọn một hiện tượng cụ thể; tìm cơ chế gây ra nó (tệp, dòng, lệnh), không đoán theo tên.
2. Đề xuất MỘT thay đổi nhỏ nhất kèm cách đo cặp: bản cũ và bản mới trên cùng đầu vào cố định, cùng một thước đo, kèm một kiểm chất lượng phải giữ được.
3. Thiếu đầu vào cố định, kiểm chất lượng hoặc thước đo chung: dừng, nói rõ thiếu gì.
4. Chất lượng giảm hoặc kết quả không rõ: hoàn tác đúng thay đổi đó.

Mẫu báo:
```text
Quan sát: <hiện tượng>
Thay đổi: <tệp:dòng, đổi gì>
Đo cặp: <đầu vào, kết quả cũ, kết quả mới>
Kiểm chất lượng: <kết quả thật>
Kết luận: giữ / bỏ / chưa rõ
```

## 3. Đọc số đo

- Kết quả rỗng nghĩa là không có tín hiệu, không phải chi phí 0.
- Không kết luận nguyên nhân từ một con số tổng hay một phiên đắt; so nhóm nghi ngờ với nhóm đối chứng hoặc kỳ trước.
- Nhóm theo việc con người gọi tên được (phiên nào, lịch nào, loại việc nào), không theo tên công nghệ.

## 4. Giữ cache (phiên và mã gọi API)

- Trong phiên: phần đầu phiên càng ổn định càng trúng cache. Đổi model, đổi bộ connector / skill, sửa tệp luật giữa phiên to đều làm ghi lại cả phiên; làm những việc đó lúc đổi phiên (`chon-model.md` luật 5).
- Khi viết mã gọi API: phần ổn định dài (lời hệ thống, tài liệu nền) đặt trước và đánh dấu cache, phần thay đổi đặt sau; chỉ thử lại lỗi tạm thời (mất kết nối, quá tải, lỗi máy chủ), tối đa 3 lần; kiểm ngân sách TRƯỚC khi gọi. Tham số và giá thay đổi nhanh: tra skill `claude-api` trước khi viết, không dùng bảng giá chép sẵn.
