# Hướng dẫn gán nhãn bình luận phim — T03

## 1. Mục tiêu và nhãn

Mỗi dòng được gán đúng một nhãn cho câu hỏi: **Bình luận có chứa ít nhất một nội dung tiêu cực hay không?**

- **Nhãn 0 — không có nội dung tiêu cực:** câu chỉ khen, thể hiện hài lòng, mô tả trung tính, hỏi thông tin hoặc không có ý chê/phàn nàn.
- **Nhãn 1 — có ít nhất một nội dung tiêu cực:** câu có bất kỳ ý chê, không hài lòng, thất vọng hoặc phàn nàn nào, dù câu còn có lời khen.

Nhãn 1 bao gồm chê phim nói chung; chê diễn xuất; chê nội dung/kịch bản; chê hình ảnh/âm thanh; chê rạp; chê dịch vụ; chê một phần trong câu dù tổng thể có lời khen; và châm biếm/mỉa mai mang nghĩa tiêu cực.

Đây là bài toán phát hiện sự hiện diện của ý tiêu cực, không phải chấm cảm xúc chung. Chỉ cần một vế tiêu cực có nghĩa là nhãn 1.

## 2. Quy tắc quyết định

1. Đọc toàn bộ câu trong `text`, giữ nguyên ngữ cảnh có trong chính câu đó.
2. Gán 1 nếu có một đối tượng bị chê hoặc có trải nghiệm không hài lòng liên quan đến phim, rạp hay dịch vụ xem phim.
3. Với câu pha trộn khen và chê, luôn gán 1. Không cân số lượng từ khen với số lượng từ chê.
4. Phân biệt phủ định của lời chê: “không tệ”, “không chán” thường là 0; “không hay”, “không đáng tiền” là 1.
5. Câu hỏi tu từ, châm biếm hoặc mỉa mai được hiểu theo nghĩa thực tế. Nếu hàm ý chê thì gán 1.
6. Chỉ dựa vào nội dung câu, không suy đoán từ điểm sao, tên phim, nguồn hay nhãn của người khác.
7. Emoji mang nghĩa rõ ràng được tính là tín hiệu. Emoji mơ hồ đứng một mình thì không tự suy diễn tiêu cực.
8. Câu không dấu, teencode và lỗi chính tả vẫn được đọc theo nghĩa thông thường; không sửa nội dung trước khi gán.
9. Lời chê không liên quan đến phim/rạp/dịch vụ (ví dụ chỉ chê thời tiết) không làm câu thành nhãn 1, trừ khi nó mô tả trải nghiệm xem phim bị ảnh hưởng bởi dịch vụ.
10. Nếu thật sự không đủ ngữ cảnh để quyết định, ghi lý do vào `note` và chuyển Tín xem lại; không tự tạo nhãn thứ ba.

## 3. Phạm vi nội dung tiêu cực

| Nhóm | Dấu hiệu điển hình |
|---|---|
| Phim nói chung | dở, chán, thất vọng, phí thời gian, không đáng tiền |
| Diễn xuất | diễn gượng, thoại đơ, nhân vật thiếu thuyết phục |
| Nội dung/kịch bản | vô lý, lê thê, dễ đoán, kết thúc hụt hẫng |
| Hình ảnh/âm thanh | hình tối, kỹ xảo giả, âm thanh quá nhỏ hoặc quá to |
| Rạp | ghế bẩn, phòng nóng, màn hình mờ, âm thanh phòng chiếu kém |
| Dịch vụ | nhân viên thiếu lịch sự, xếp hàng lâu, đồ ăn nguội, xử lý chậm |
| Pha trộn | có lời khen nhưng bất kỳ vế nào vẫn chê một phần |
| Châm biếm/mỉa mai | bề mặt có vẻ khen nhưng ngữ cảnh thể hiện điều ngược lại |

Không xem các mô tả trung tính như thời lượng, lịch chiếu, thể loại hoặc câu hỏi mua vé là tiêu cực nếu không có ý phàn nàn.

## 4. Ví dụ biên khó

| # | Bình luận | Nhãn | Lý do |
|---:|---|---:|---|
| 1 | Phim không tệ, xem giải trí ổn. | 0 | “Không tệ” phủ định ý chê; phần còn lại tích cực. |
| 2 | Phim không hay như trailer. | 1 | “Không hay” là nhận xét tiêu cực. |
| 3 | Diễn viên đóng hay nhưng kịch bản lê thê. | 1 | Có một vế chê kịch bản. |
| 4 | Kịch bản thường thôi, bù lại hình ảnh quá đẹp. | 1 | “Thường thôi” là chê một phần dù tổng thể có lời khen. |
| 5 | Hay quá, ngủ được nguyên nửa phim luôn 🙂 | 1 | Mỉa mai; ý thực là phim gây buồn ngủ. |
| 6 | Đỉnh cao điện ảnh, kỹ xảo như làm bằng Paint. | 1 | Vế sau làm rõ lời khen mang tính châm biếm. |
| 7 | Ủa hết rồi hả? | 0 | Chưa đủ bằng chứng chê; có thể chỉ là câu hỏi ngạc nhiên. |
| 8 | Ủa hết rồi hả, cái kết cụt ngủn vậy? | 1 | Phàn nàn rõ về kết thúc. |
| 9 | Cũng được, không có gì đặc biệt. | 1 | “Không có gì đặc biệt” là đánh giá thiếu tích cực/chê nhẹ. |
| 10 | Không chán như mình tưởng. | 0 | Phủ định “chán”, kết luận thực tế không tiêu cực. |
| 11 | Phim dài 180 phút. | 0 | Mô tả trung tính về thời lượng. |
| 12 | Phim dài lê thê, cắt 30 phút còn hay hơn. | 1 | Chê nhịp phim và độ dài. |
| 13 | Ko uổng tiền nha, đáng xem lắm 😍 | 0 | Teencode của “không uổng tiền”, ý tích cực. |
| 14 | Ko đáng tiền, qc hay hơn phim. | 1 | Câu không dấu/teencode nhưng có ý chê rõ. |
| 15 | Âm thanh lớn. | 0 | Mô tả mơ hồ, không khẳng định khó chịu. |
| 16 | Âm thanh lớn đến đau cả tai. | 1 | Phàn nàn rõ về âm thanh. |
| 17 | Rạp đông nhưng nhân viên xử lý nhanh, ghế sạch. | 0 | “Đông” là hoàn cảnh; trải nghiệm dịch vụ được khen. |
| 18 | Phim hay, tiếc là rạp nóng và ghế bẩn. | 1 | Chê rạp dù khen phim. |
| 19 | Nhân vật phản diện đáng ghét thật sự. | 0 | Có thể là mô tả vai diễn thành công, không phải chê chất lượng. |
| 20 | Nhân vật phản diện viết quá nhạt, chẳng đáng nhớ. | 1 | Chê cách xây dựng nhân vật. |
| 21 | Buồn khóc hết nước mắt, phim quá cuốn. | 0 | “Buồn” mô tả cảm xúc do phim hay, không phải bất mãn. |
| 22 | Xem xong chỉ thấy buồn vì mất hai tiếng. | 1 | Thể hiện thất vọng/phí thời gian. |
| 23 | Vé hơi cao nhưng trải nghiệm xứng đáng. | 1 | “Vé hơi cao” vẫn là một ý tiêu cực. |
| 24 | Bao giờ có suất 20 giờ? | 0 | Câu hỏi thông tin, không có ý chê. |
| 25 | Chờ bắp 25 phút thì phim chiếu gần xong luôn rồi. | 1 | Phàn nàn dịch vụ chậm, có phóng đại. |
| 26 | 😭😭😭 | 0 | Emoji đứng một mình không đủ ngữ cảnh để kết luận tiêu cực. |
| 27 | Kết phim làm tui khóc 😭 nhưng quá hay. | 0 | Cảm xúc buồn đi cùng đánh giá tích cực, không có ý chê. |
| 28 | Phòng chiếu hôm nay lạnh. | 0 | Mô tả chưa thể hiện khó chịu. |
| 29 | Phòng chiếu lạnh run mà gọi nhân viên không ai hỗ trợ. | 1 | Phàn nàn cả điều kiện rạp lẫn dịch vụ. |
| 30 | Nội dung dễ đoán nhưng trẻ con nhà mình rất thích. | 1 | Có ý chê nội dung dù phần sau tích cực. |

## 5. Quy trình hai annotator

- **Annotator A:** Lê Minh Tín, gán nhãn toàn bộ dữ liệu.
- **Annotator B:** “Người 1”, là người thật và được ẩn danh trong Git.
- Script chọn cố định 100 câu bằng `random_state=42` và tạo `data/phim/kappa_sample.csv` với các cột `id,text,label_a,label_b`.
- Trước khi giao file, Tín có thể ẩn cột `label_a` khỏi bản làm việc của B. B phải gán độc lập toàn bộ 100 câu vào `label_b` và không xem nhãn A.
- Sau khi nhận lại, Tín ghép `label_b` đúng theo `id`; không thay nhãn để làm tăng kappa. Script tính Cohen's kappa giữa `label_a` và `label_b`.
- Mức chấp nhận của T03 là kappa ≥ 0,6. Nếu thấp hơn, hai người rà các nhóm bất đồng, làm rõ guideline rồi gán lại; phải lưu và báo cả kết quả trước lẫn sau.
- Không dùng ChatGPT, Claude hoặc bất kỳ LLM nào làm annotator hay tự điền `label_b`.

## 6. Bảo mật và chất lượng dữ liệu

Không đưa tên người viết, liên kết hồ sơ, email, số điện thoại hoặc `@username` vào `text` hay `note`. Giữ nguyên teencode, câu không dấu và emoji vì đó là đặc điểm tự nhiên của bình luận. Chỉ lấy đoạn ngắn phục vụ nghiên cứu và ghi nguồn ở mức chung, không ghi thông tin nhận diện người viết.
