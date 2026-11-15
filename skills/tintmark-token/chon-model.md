# Chọn model và mức nỗ lực

## 1. Bảng việc → model

| Loại việc | Dấu hiệu | Model | Nỗ lực |
|---|---|---|---|
| Sổ sách: phiên Yêu cầu, Báo cáo | ghi sổ yêu cầu, chuyển tin, cập nhật bảng, tổng hợp báo cáo từ dữ liệu có sẵn, đổi tên / sắp xếp | Sonnet (Haiku nếu chỉ chép / lọc) | thấp |
| Lịch tự chạy | kiểm có việc mới không, chép dữ liệu, rà soát theo danh sách | Haiku / Sonnet | thấp |
| Điều phối | đọc tệp trạng thái, chia việc, soạn lời giao việc | Sonnet (Haiku nếu chỉ chuyển tin) | vừa |
| Viết nội dung, kịch bản, tài liệu | có mẫu, có giọng sẵn | Sonnet | vừa |
| Kiểm thử theo kịch bản | bước rõ, tiêu chí đạt rõ | Sonnet | vừa |
| Dò tìm / đọc rộng | tìm tệp, gom thông tin nhiều nơi | subagent model nhỏ, chỉ nhận kết luận | — |
| Sửa mã kho thật, gỡ lỗi khó | nhiều tệp, hỏng thì ảnh hưởng người dùng | Opus (hoặc model mạnh nhất có) | cao |
| Kiến trúc, kế hoạch lớn, quyết định khó đảo ngược | | model mạnh nhất | cao |
| Phát hành, thao tác có rủi ro | | model mạnh nhất | cao |

Tên model thay theo đời (Haiku / Sonnet / Opus / Fable…): hiểu là **nhỏ / vừa / mạnh**.

## 2. Luật

0. **Mặc định:** phiên Yêu cầu, Báo cáo, Điều phối (và mọi phiên chủ yếu ghi sổ / chuyển tin) chạy Sonnet hoặc Haiku. Opus chỉ cho mã khó, kiến trúc, phát hành. Phiên sổ sách đang chạy Opus thì đổi khi kế nhiệm (luật 5).
1. Việc khó không hạ model. Sai một lần ở việc khó đắt hơn mọi khoản tiết kiệm.
2. Hạ model chỉ khi: việc lặp, tiêu chí kiểm rõ, ngữ cảnh nhỏ, sai thì phát hiện được ngay.
3. Nghi ngờ: thử model nhỏ trên 1 việc có tiêu chí kiểm; đạt thì chuyển cả loại việc đó.
4. Model nhỏ làm hỏng 2 lần liên tiếp cùng loại việc → nâng một bậc và ghi vào sổ phiên, không cố thêm.
5. Đổi model của một phiên đang to làm mất cache (một lần ghi lại cả phiên). Vì vậy đổi model **cùng lúc với đổi phiên**: phiên kế nhiệm mở bằng model đúng. Phiên < 100k thì đổi ngay được.
6. Phiên không tự đổi model của chính nó; phiên điều phối đổi cho phiên khác (app có thể hỏi người dùng), hoặc người dùng chọn trong menu model.
7. Chế độ nhanh (fast) và nỗ lực cao tốn hơn: chỉ bật khi người dùng bảo.

## 3. Cơ chế sắp xếp model cho cả dự án

1. Sổ phiên có cột **Loại việc** và **Model chuẩn** cho từng phiên (theo bảng mục 1).
2. Khi mở phiên mới / kế nhiệm: lấy model từ cột Model chuẩn, không theo model của phiên đang mở nó.
3. Rà định kỳ (khi chạy `do_token.py`, hoặc khi hạn mức tuần > 60% lúc còn hơn nửa tuần): so model thực tế với model chuẩn; phiên lệch thì xếp vào danh sách "đổi khi kế nhiệm"; phiên sổ sách < 100k thì đổi luôn.
4. Tỉ lệ nên hướng tới: model mạnh < 60% chi phí. Cao hơn nghĩa là việc sổ sách đang chạy model mạnh.
5. Phiên đổi loại việc (từ sổ sách sang sửa mã) → tách phiên mới đúng model, không nâng model phiên sổ sách.

## 4. Trên Claude Chat

Không có sổ phiên tự động; quy ước theo **Project** và theo **tên cuộc trò chuyện**:
- Mỗi Project ghi model chuẩn ngay trong hướng dẫn của Project (ví dụ "Project này dùng Sonnet; chỉ chuyển Opus khi cần lập kế hoạch lớn").
- Mở chat mới: chọn model trong hộp chọn trước khi gõ câu đầu. Việc tra cứu, viết lại, tóm tắt: model nhỏ / vừa. Phân tích nhiều tài liệu, chiến lược, mã khó: model mạnh.
- Bật "suy nghĩ mở rộng" / nghiên cứu sâu chỉ cho câu hỏi cần; tắt lại sau đó.
- Một chat một chủ đề; đổi chủ đề thì mở chat mới thay vì nâng model.

## 5. Subagent

Mỗi subagent tốn 20–30k khởi động. Giao khi: đọc rộng mà chỉ cần kết luận; việc độc lập chạy song song; cần đánh giá không bị ảnh hưởng bởi ngữ cảnh chính. Không giao việc vài lệnh. Chọn model nhỏ cho dò tìm, yêu cầu trả kết quả ngắn kèm `đường_dẫn:dòng`.
