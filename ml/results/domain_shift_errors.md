# Phân tích lỗi T08 — lệch miền điện thoại → phim

## Phạm vi và quy ước

- Bảng chính dùng checkpoint research canonical `ml/artifacts/phobert_A_best/`; checkpoint backend chỉ đối chiếu câu bắt buộc.
- Nhãn `0 = bình thường`, `1 = tiêu cực`; score trong ngoặc là score nhãn 1; ngưỡng `0,5`.
- Hai score PhoBERT khác nhau vì hai checkpoint khác trọng số; không trộn chúng trong bảng metric chính.

## Câu kiểm tra bắt buộc

`Phim dài lê thê, xem mà mệt` không có trong `movie_test.csv`, nên đây là ca kiểm thử riêng.

| Model/checkpoint | Dự đoán | Score tiêu cực |
|---|---:|---:|
| PhoBERT A research canonical | 0 | 0.387731 |
| SVM A | 1 | 0.501091 |
| Logistic Regression A | 1 | 0.508498 |
| Naive Bayes A | 0 | 0.464394 |
| PhoBERT A backend (tham chiếu, không dùng trong bảng chính) | 0 | 0.012500 |

Cả research và backend PhoBERT đều dự đoán `0`, nhưng checkpoint research có score cao hơn rõ rệt. Kết quả này cho thấy cách chê nhịp phim “dài lê thê” chưa được hai checkpoint nhận ra đủ mạnh.

## 20 lỗi tiêu biểu trên movie test

| # | ID | Nhóm | Nhãn thật | Model sai | Dự đoán/score (PhoBERT; SVM; LR; NB) | Câu | Phân tích |
|---:|---|---|---:|---|---|---|---|
| 1 | MOV0502 | Từ vựng đặc thù phim | 0 | SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 0 (0.074927); SVM A: 1 (0.557509); Logistic Regression A: 1 (0.643219); Naive Bayes A: 1 (0.951871) | gấc gấc hay, khóc trôi kem nền | “khóc trôi kem nền” biểu đạt cảm xúc tích cực theo ngữ cảnh xem phim. |
| 2 | MOV0476 | Từ vựng đặc thù phim | 0 | Naive Bayes A | PhoBERT A: 0 (0.003386); SVM A: 0 (0.492419); Logistic Regression A: 0 (0.487963); Naive Bayes A: 1 (0.753507) | Công nhận phim hay vl luôn | Tiếng lóng nhấn mạnh “vl” đi cùng “hay” bị NB đọc sai. |
| 3 | MOV0479 | Từ vựng đặc thù phim | 1 | PhoBERT A, SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 0 (0.008583); SVM A: 0 (0.484928); Logistic Regression A: 0 (0.474105); Naive Bayes A: 0 (0.474181) | phim ảo vãi | Cụm ngắn “ảo vãi” mơ hồ sắc thái; cả bốn model bỏ sót nhãn tiêu cực. |
| 4 | MOV0207 | Từ vựng đặc thù phim | 1 | PhoBERT A | PhoBERT A: 0 (0.004382); SVM A: 1 (0.528723); Logistic Regression A: 1 (0.574227); Naive Bayes A: 1 (0.852991) | Hát nhiều vl 😂 | Chê phim ca nhạc bằng câu rất ngắn; PhoBERT không nhận ra hàm ý. |
| 5 | MOV0199 | Từ vựng đặc thù phim | 1 | SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 1 (0.977047); SVM A: 0 (0.484825); Logistic Regression A: 0 (0.450205); Naive Bayes A: 0 (0.453702) | phản diện đáng quên v | “Phản diện đáng quên” là phê bình đặc thù phim, ba baseline bỏ sót. |
| 6 | MOV0503 | Chê nhịp phim/nội dung | 1 | PhoBERT A | PhoBERT A: 0 (0.005792); SVM A: 1 (0.551168); Logistic Regression A: 1 (0.625059); Naive Bayes A: 1 (0.614445) | Nội dung dễ đoán , không đáng sợ lắm | “Dễ đoán” và “không đáng sợ” là chê nội dung nhưng PhoBERT dự đoán bình thường. |
| 7 | MOV0432 | Chê nhịp phim/nội dung | 1 | PhoBERT A | PhoBERT A: 0 (0.017422); SVM A: 1 (0.609905); Logistic Regression A: 1 (0.769598); Naive Bayes A: 1 (0.697825) | phim chưa được xuất sắc ở màn nội dung và hù dọa nhưng diễn xuất của các diễn viên cũng không làm bộ phim bị nhàm chán , nội dung vẫn cái twist cũ và hù dọa thì chung chung , xem để giải trí ổn . | Nhiều mệnh đề khen/chê trộn lẫn làm PhoBERT nghiêng về bình thường. |
| 8 | MOV0484 | Chê nhịp phim/nội dung | 1 | PhoBERT A, SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 0 (0.005794); SVM A: 0 (0.486406); Logistic Regression A: 0 (0.469428); Naive Bayes A: 0 (0.343796) | Phim mạch truyện dài dòng lê thê | “Dài dòng lê thê” là lỗi nhịp phim điển hình nhưng cả bốn model bỏ sót. |
| 9 | MOV0171 | Chê nhịp phim/nội dung | 1 | SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 1 (0.748293); SVM A: 0 (0.459977); Logistic Regression A: 0 (0.391032); Naive Bayes A: 0 (0.452943) | tình tiết dễ đoán, kĩ xảo tạm ổn. Nhân vật nữ chính diễn xuất chưa tốt lắm | Chê tình tiết/kĩ xảo/diễn xuất mức nhẹ; ba baseline dự đoán bình thường. |
| 10 | MOV0411 | Chê nhịp phim/nội dung | 1 | PhoBERT A | PhoBERT A: 0 (0.256489); SVM A: 1 (0.645250); Logistic Regression A: 1 (0.829451); Naive Bayes A: 1 (0.729965) | Phần này hơi dài dòng, nếu có thêm chút hành động như phần 7 nữa thì sẽ hay hơn. | Cấu trúc góp ý “nếu... thì hay hơn” che khuất phê bình nhịp phim. |
| 11 | MOV0403 | Chê nhịp phim/nội dung | 1 | PhoBERT A | PhoBERT A: 0 (0.007663); SVM A: 1 (0.653639); Logistic Regression A: 1 (0.833477); Naive Bayes A: 1 (0.743273) | phần này làm hơi hời hợt | “Hời hời hợt” là cụm chê ngắn đặc thù, PhoBERT cho score rất thấp. |
| 12 | MOV0448 | Châm biếm | 1 | SVM A | PhoBERT A: 1 (0.841272); SVM A: 0 (0.494833); Logistic Regression A: 1 (0.503840); Naive Bayes A: 1 (0.767933) | 22:30 - 18/2. Rạp số 8. Rạp phim hay lò thiêu vậy ? Tiết kiệm điện hả ??? Nóng khùm luôn tr 😀 … | So sánh rạp với “lò thiêu” và câu hỏi tu từ; SVM nằm sát dưới ngưỡng. |
| 13 | MOV0405 | Châm biếm | 1 | PhoBERT A, SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 0 (0.003507); SVM A: 0 (0.459347); Logistic Regression A: 0 (0.390112); Naive Bayes A: 0 (0.428151) | Điểm cộng duy nhất chắc là bác Pedro đẹp và diễn hợp | “Điểm cộng duy nhất” hàm ý phần còn lại kém; cả bốn model bỏ sót. |
| 14 | MOV0060 | Châm biếm | 1 | PhoBERT A, SVM A, Logistic Regression A | PhoBERT A: 0 (0.003744); SVM A: 0 (0.470364); Logistic Regression A: 0 (0.436443); Naive Bayes A: 1 (0.616999) | Phim kìa ai xem cảnh đẹp thì oke chứ hay gì | “Cảnh đẹp thì oke chứ hay gì” là phủ định mỉa mai; ba model bỏ sót. |
| 15 | MOV0229 | Châm biếm | 1 | PhoBERT A | PhoBERT A: 0 (0.356066); SVM A: 1 (0.574891); Logistic Regression A: 1 (0.699144); Naive Bayes A: 1 (0.660794) | Xin lỗi nhưng mà.... dù được xem sớm nhưng cũng khá bất ngờ khi cả rạp ai cũng cười banh xác thay vì là khóc trong những cảnh cảm động.... nói vậy cả nhà tự hiểu rồi ha hic | Kể chuyện khán giả cười thay vì khóc để chê gián tiếp; PhoBERT bỏ sót. |
| 16 | MOV0303 | Chê rạp hoặc dịch vụ | 0 | PhoBERT A | PhoBERT A: 1 (0.993133); SVM A: 0 (0.466491); Logistic Regression A: 0 (0.411851); Naive Bayes A: 0 (0.135415) | Ổn, rạp hơi bé, âm thanh tốt, màn hình ok, phù hợp với mức giá | Review pha trộn: rạp bé nhưng giá/âm thanh tốt; PhoBERT báo dương tính giả. |
| 17 | MOV0310 | Chê rạp hoặc dịch vụ | 1 | Naive Bayes A | PhoBERT A: 1 (0.965556); SVM A: 1 (0.564592); Logistic Regression A: 1 (0.661131); Naive Bayes A: 0 (0.404204) | Rạp này khá cũ nên cũng vắng, với khu Lobby hơi kém vệ sinh và nóng, còn lại phòng chiếu với giá cả thì tuyệt vời. Đã to còn rẻ. | Chê cơ sở/lobby nhưng khen phòng chiếu và giá; NB bỏ sót nhãn tiêu cực. |
| 18 | MOV0297 | Chê rạp hoặc dịch vụ | 1 | SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 1 (0.903890); SVM A: 0 (0.425152); Logistic Regression A: 0 (0.295485); Naive Bayes A: 0 (0.135686) | nhân viên có thái độ không tốt, và không tư vấn đúng các combo, ép giá khách hàng | Phàn nàn nhân viên/combo/giá; ba baseline bỏ sót. |
| 19 | MOV0301 | Chê rạp hoặc dịch vụ | 1 | PhoBERT A, SVM A, Logistic Regression A, Naive Bayes A | PhoBERT A: 0 (0.008240); SVM A: 0 (0.457500); Logistic Regression A: 0 (0.370038); Naive Bayes A: 0 (0.467306) | Nhân viên tiếp khách rất rất lâu, nên cải thiện và tăng quầy tiếp khách lên. Làm kiểu này không biết bình thường đón mấy trăm khách ngày kiểu gì. | Chê thời gian phục vụ và số quầy; cả bốn model bỏ sót. |
| 20 | MOV0312 | Chê rạp hoặc dịch vụ | 1 | PhoBERT A | PhoBERT A: 0 (0.005323); SVM A: 1 (0.526045); Logistic Regression A: 1 (0.556018); Naive Bayes A: 1 (0.880997) | mình mua 1 phần bắp nước nhân viên cũng chả thèm hỏi dùng size gì mà tự động up lên size lớn nhất rồi tính tiền | Phàn nàn upsell bắp nước; PhoBERT bỏ sót do từ vựng dịch vụ. |

## Tổng hợp

- Chê nhịp phim/nội dung: **6** câu.
- Từ vựng đặc thù phim: **5** câu.
- Chê rạp hoặc dịch vụ: **5** câu.
- Châm biếm: **4** câu.

Mẫu lỗi cho thấy lệch miền không chỉ ở từ khóa: các model còn khó xử lý phê bình nhẹ/pha trộn, hàm ý châm biếm và từ vựng dịch vụ rạp. Đây là phân tích mô tả trên 20 ca được chọn có chủ đích, không phải ước lượng tần suất cho toàn bộ lỗi.
