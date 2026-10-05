# Phân tích lỗi T02 — UIT-ViSFD test

Phân tích dùng dự đoán `text_norm`. Mỗi mô hình có đúng 20 câu sai, được gán nhóm bằng quy tắc từ khóa cố định để hỗ trợ rà soát thủ công; nhóm không phải nhãn chuẩn của bộ dữ liệu.

## Tổng hợp nhóm lỗi trong 20 câu/mô hình

| Nhóm | PhoBERT A | SVM | Logistic Regression | Naive Bayes |
|---|---:|---:|---:|---:|
| Phủ định | 5 | 5 | 5 | 5 |
| Chê một phần | 5 | 5 | 5 | 4 |
| Châm biếm | 0 | 2 | 2 | 3 |
| Từ lóng/viết tắt | 5 | 4 | 4 | 4 |
| Nhãn nhiễu/thiếu ngữ cảnh | 0 | 0 | 0 | 0 |
| Khác | 5 | 4 | 4 | 4 |

## 20 câu sai — PhoBERT A

| # | Index | Nhãn thật | Dự đoán | Nhóm | Câu |
|---:|---:|---:|---:|---|---|
| 1 | 27 | 0 | 1 | Phủ định | Cho em hỏi là máy em, mua được 1 tuần mà máy lâu lâu em nghe cái cốc, như là bị lỏng gì ở trong vậy, như vậy có vấn đề j k anh |
| 2 | 41 | 1 | 0 | Chê một phần | Pin 5000 nhưng dùng trong 1 ngày anh nhân viên cute cam chụp đẹp  Nhưng xem vd trên Youtube chỉ 720p là căng |
| 3 | 8 | 0 | 1 | Từ lóng/viết tắt | Mua đc 1 tuần và đt sài khá tốt.. Giá tầm trung mà v là ok lắm rồi. Pin cực kì mạnh. Điểm yếu là cam trc thôi chứ cam sau đẹp lắm nha. Mọi người sài kĩ một tí thì máy tốt lắm, chứ máy gần 4tr mà lên đây chê này chê nọ là sao?? V là tốt lắm rồi |
| 4 | 28 | 1 | 0 | Khác | Sau vài ngày sd sp... thấy đt cx tạm ổn. Nếu vừa xài vừa xạc thì cảm ứq sẽ bị đơ, pin tuột nhanh. Vân tay xài cx khá ổn... |
| 5 | 34 | 0 | 1 | Phủ định | Mình mua 3 ngày về xài thấy rất tốt. Do công việc nên hầu như xài suốt ngày, 4g mình bật 24/24 nhưng pin xài chỉ 70% ( 6 giờ sáng đến 20 giờ) . Trong khi những dt khác mình xài phải sạt 2 lần. Về tất cả chức năng còn lại mình thấy rất mượt, mình rất hài lòng về sản phẩm. Máy chạy không bị nóng. Mình sẽ mua thêm sản phẩm cho gia đình xài. |
| 6 | 58 | 0 | 1 | Chê một phần | Video màu sắc nhợt nhạt lắm. Nhưng chuyển từ bé màn hình lên full màn trong Youtube thì video lại nhảy màu sắc sống động hơn. Chỉ 1s mong sớm sửa lỗi |
| 7 | 315 | 0 | 1 | Từ lóng/viết tắt | Mới mua sài dc 2 ngày sạc 50 mấy phút la đầy pin sài khá ok lâu tuột 20% pin sài dc 2tiêng mấy đúng đồng tiền bác gạo |
| 8 | 69 | 0 | 1 | Khác | Mua cũng được gần 1tuaan sài khá ổn, dung lượng cao, pin sài khá lâu mà có cái muốn làm dì cũng phải vô cài đặt mơis được. |
| 9 | 54 | 1 | 0 | Phủ định | Sử dụng một tuần, máy màn hình đẹp xem phim nghe nhạc rất tốt.chơi game nặng như liên quân PUBG rất mượt nhưng chơi khoảng một tiếng máy nóng lên là bị giật lag. Pin 4000 nhưng thật tế ko trâu vì màn hình lớn độ phân giải cao nên tuột pin khá nhanh.chụp ảnh được màu sắc trung thực rõ nét. Trong tầm giá 5tr con này là tốt nhất |
| 10 | 64 | 1 | 0 | Chê một phần | Máy hoàn thiện về mặt thiết kế cũng như hiệu năng, chơi pubg, tft mobile mượt mà, nhưng do sạc nhanh 30w nên lúc đầu hơi nóng |
| 11 | 387 | 0 | 1 | Từ lóng/viết tắt | sài được tuần ngon chán so vs giá hàng việt nam chất lượng cao kkkkkk ngon bổ rẻ |
| 12 | 170 | 1 | 0 | Khác | Mua con này thôi tôi lấy A10 samsung ngon hơn nhiều, chip exynos 7884 chạy liên quân max cấu hình...bao đâm |
| 13 | 65 | 0 | 1 | Phủ định | máy mình dùng sau 3 tháng khá ổn định . về pin và hiệu náng sản phẩm này đem lại . không có nút 6* để mình ấn luôn . ae nên mua con này thiết kế vừa đẹp mà cấu hình cao chạy đa nhiệm tốt ! |
| 14 | 157 | 0 | 1 | Chê một phần | Mình sử dụng máy được 15 ngày : Camera tốt, pin trâu, cầm nắm thoải mái, hiệu năng cao trong tầm giá,... Bị lỗi xem Youtube HDR bị xám nhưng đã được fix qua các bản cập nhật. |
| 15 | 630 | 1 | 0 | Từ lóng/viết tắt | Máy dùng khá mượt pin trâu chs game ngon ( nếu chs pubg mà dùng gyro thì nên xem xét vì máy này dùng gyro di tâm khá chậm) hợp vs ai mua về chs game còn ai muốn sống ảo chụp hình đẹp thì mua máy khác |
| 16 | 178 | 0 | 1 | Khác | mới mua 10 ngày, màn đẹp, pin trâu, cảm ứng nhạy, wifi oke, chỉ có cảm biến vân tay kém |
| 17 | 72 | 0 | 1 | Phủ định | Mới mua về sử dụng được 1 tuần mà sao mình thấy mỗi lần đăng ảnh lên FB hay instagram thì ảnh đều bị vỡ bị mặc dù ảnh lúc chụp rất nét không biết có thể đổi trả được k |
| 18 | 184 | 1 | 0 | Chê một phần | Mình mua được 10 ngày dùng mọi thứ ok nhưng sao sạc đến 98% pin lại dùng ạ momg được mọi người góp ý |
| 19 | 858 | 1 | 0 | Từ lóng/viết tắt | sản phẩm đc mấy hôm đầu là ngon thôi ae ạ chứ 1 vài tuần sau chơi game kém bắt wifi TẠM TẠM đc mỗi chụp ảnh đẹp MÀ XEM PHIM CŨNG nét thôi mình cho 4 sao nhé nhân viên phục vụ tốt lắm CŨNG TẠM ỔN GIÁ |
| 20 | 205 | 0 | 1 | Khác | Sao dt redmi note 8 pro của e cứ hiện lỗi " Nhiệm vụ thực hiện thất bại, hãy thử lại sau (-2019)" vậy ạ |

## 20 câu sai — SVM

| # | Index | Nhãn thật | Dự đoán | Nhóm | Câu |
|---:|---:|---:|---:|---|---|
| 1 | 9 | 1 | 0 | Phủ định | Pin nhanh hết vân tay cũng chưa đk nhạy  Nhân vien tgdd tư vấn nhiệt tình dễ thương 5 sao về phong cách bán hàng |
| 2 | 38 | 1 | 0 | Chê một phần | Sản phẩm khá tốt trong tầm giá nhưng sao sạc pin nó nóng thế mặc dù tôi đã tắt ánh sáng và mạng đi và xoá các tác vụ trang nhưng nó vẫn thế |
| 3 | 1879 | 0 | 1 | Châm biếm | Vì khe 2 dùng chung nên dùng thẻ nhớ thì chỉ dùng được 1 sim. Mua bản 128gb sẽ tiện hơn nếu dùng 2 sim :))) |
| 4 | 109 | 1 | 0 | Từ lóng/viết tắt | Sản phẩm tốt ,pin trâu mới mua đc nữa ngày có điều cam hơi lồi nhân viên phục vụ tận tình |
| 5 | 69 | 0 | 1 | Khác | Mua cũng được gần 1tuaan sài khá ổn, dung lượng cao, pin sài khá lâu mà có cái muốn làm dì cũng phải vô cài đặt mơis được. |
| 6 | 27 | 0 | 1 | Phủ định | Cho em hỏi là máy em, mua được 1 tuần mà máy lâu lâu em nghe cái cốc, như là bị lỏng gì ở trong vậy, như vậy có vấn đề j k anh |
| 7 | 58 | 0 | 1 | Chê một phần | Video màu sắc nhợt nhạt lắm. Nhưng chuyển từ bé màn hình lên full màn trong Youtube thì video lại nhảy màu sắc sống động hơn. Chỉ 1s mong sớm sửa lỗi |
| 8 | 1950 | 1 | 0 | Châm biếm | Rất ok,thiết kế đt rất đẹp,điều pin tuột nhanh:))chụp hình rất ok ,chơi game bao mượt |
| 9 | 180 | 0 | 1 | Từ lóng/viết tắt | Thêm 300k lấy con realms 5i gam 4gb ngon hơn nhiều.điện thoại này chỉ có cũ sạc nhanh chứ đc gì đâu.ai mua phải cân nhắc nha. |
| 10 | 136 | 1 | 0 | Khác | Đã mua 3 ngày. So sánh với vsmart live và huawei 2i đã sử dụng pin rõ chán. Tần suất sử dụng ít hơn hẳn mấy cái trước mà pin làm mới nửa ca còn 20% pin. Chỉ zalo, lâu lâu lướt face, game cờ tướng nhẹ, youtube nếu so ngang pin máy 2F này bằng một nửa máy đã sử dụng. Còn cấu hình mượt đẹp, chụp hình cũng tốt. |
| 11 | 30 | 1 | 0 | Phủ định | Sản phẩm tốt, nhân viên nhiệt tình tới tận mình ra về, có điều pin không như mình mong đợi mặc dù không tác vụ gì nhiều, 32gb bộ nhớ thật sự khó đủ với mình mặc dù mình không chứa gì nhiều. Nói chung mọi thứ khác đều ok ^^ |
| 12 | 187 | 1 | 0 | Chê một phần | Top 1-2 về tầm tiền và chức năng sử dụng nha, nhược điểm cũng có nhưng tầm tiền là quá tốt( màn hình HD+, cam bình thường so tầm tiền, to dày...uu the:màn hình rộng dễ nhìn, nhạy sáng tốt, có cam góc rộng, sạc nhanh vs redminote 7 same same |
| 13 | 630 | 1 | 0 | Từ lóng/viết tắt | Máy dùng khá mượt pin trâu chs game ngon ( nếu chs pubg mà dùng gyro thì nên xem xét vì máy này dùng gyro di tâm khá chậm) hợp vs ai mua về chs game còn ai muốn sống ảo chụp hình đẹp thì mua máy khác |
| 14 | 170 | 1 | 0 | Khác | Mua con này thôi tôi lấy A10 samsung ngon hơn nhiều, chip exynos 7884 chạy liên quân max cấu hình...bao đâm |
| 15 | 54 | 1 | 0 | Phủ định | Sử dụng một tuần, máy màn hình đẹp xem phim nghe nhạc rất tốt.chơi game nặng như liên quân PUBG rất mượt nhưng chơi khoảng một tiếng máy nóng lên là bị giật lag. Pin 4000 nhưng thật tế ko trâu vì màn hình lớn độ phân giải cao nên tuột pin khá nhanh.chụp ảnh được màu sắc trung thực rõ nét. Trong tầm giá 5tr con này là tốt nhất |
| 16 | 227 | 1 | 0 | Chê một phần | Máy rất mượt, nhưng mà khi chơi pubg thì bị loạn cảm ứng , pin rất trâu , giao hàng rất nhanh , tận tình |
| 17 | 858 | 1 | 0 | Từ lóng/viết tắt | sản phẩm đc mấy hôm đầu là ngon thôi ae ạ chứ 1 vài tuần sau chơi game kém bắt wifi TẠM TẠM đc mỗi chụp ảnh đẹp MÀ XEM PHIM CŨNG nét thôi mình cho 4 sao nhé nhân viên phục vụ tốt lắm CŨNG TẠM ỔN GIÁ |
| 18 | 178 | 0 | 1 | Khác | mới mua 10 ngày, màn đẹp, pin trâu, cảm ứng nhạy, wifi oke, chỉ có cảm biến vân tay kém |
| 19 | 72 | 0 | 1 | Phủ định | Mới mua về sử dụng được 1 tuần mà sao mình thấy mỗi lần đăng ảnh lên FB hay instagram thì ảnh đều bị vỡ bị mặc dù ảnh lúc chụp rất nét không biết có thể đổi trả được k |
| 20 | 312 | 0 | 1 | Chê một phần | Chạy antutu được 277636 điểm. thật tuyệt khi một sản phẩm rẻ như này mà được điểm số cao như vậy |

## 20 câu sai — Logistic Regression

| # | Index | Nhãn thật | Dự đoán | Nhóm | Câu |
|---:|---:|---:|---:|---|---|
| 1 | 9 | 1 | 0 | Phủ định | Pin nhanh hết vân tay cũng chưa đk nhạy  Nhân vien tgdd tư vấn nhiệt tình dễ thương 5 sao về phong cách bán hàng |
| 2 | 38 | 1 | 0 | Chê một phần | Sản phẩm khá tốt trong tầm giá nhưng sao sạc pin nó nóng thế mặc dù tôi đã tắt ánh sáng và mạng đi và xoá các tác vụ trang nhưng nó vẫn thế |
| 3 | 1879 | 0 | 1 | Châm biếm | Vì khe 2 dùng chung nên dùng thẻ nhớ thì chỉ dùng được 1 sim. Mua bản 128gb sẽ tiện hơn nếu dùng 2 sim :))) |
| 4 | 109 | 1 | 0 | Từ lóng/viết tắt | Sản phẩm tốt ,pin trâu mới mua đc nữa ngày có điều cam hơi lồi nhân viên phục vụ tận tình |
| 5 | 69 | 0 | 1 | Khác | Mua cũng được gần 1tuaan sài khá ổn, dung lượng cao, pin sài khá lâu mà có cái muốn làm dì cũng phải vô cài đặt mơis được. |
| 6 | 27 | 0 | 1 | Phủ định | Cho em hỏi là máy em, mua được 1 tuần mà máy lâu lâu em nghe cái cốc, như là bị lỏng gì ở trong vậy, như vậy có vấn đề j k anh |
| 7 | 41 | 1 | 0 | Chê một phần | Pin 5000 nhưng dùng trong 1 ngày anh nhân viên cute cam chụp đẹp  Nhưng xem vd trên Youtube chỉ 720p là căng |
| 8 | 1950 | 1 | 0 | Châm biếm | Rất ok,thiết kế đt rất đẹp,điều pin tuột nhanh:))chụp hình rất ok ,chơi game bao mượt |
| 9 | 180 | 0 | 1 | Từ lóng/viết tắt | Thêm 300k lấy con realms 5i gam 4gb ngon hơn nhiều.điện thoại này chỉ có cũ sạc nhanh chứ đc gì đâu.ai mua phải cân nhắc nha. |
| 10 | 136 | 1 | 0 | Khác | Đã mua 3 ngày. So sánh với vsmart live và huawei 2i đã sử dụng pin rõ chán. Tần suất sử dụng ít hơn hẳn mấy cái trước mà pin làm mới nửa ca còn 20% pin. Chỉ zalo, lâu lâu lướt face, game cờ tướng nhẹ, youtube nếu so ngang pin máy 2F này bằng một nửa máy đã sử dụng. Còn cấu hình mượt đẹp, chụp hình cũng tốt. |
| 11 | 54 | 1 | 0 | Phủ định | Sử dụng một tuần, máy màn hình đẹp xem phim nghe nhạc rất tốt.chơi game nặng như liên quân PUBG rất mượt nhưng chơi khoảng một tiếng máy nóng lên là bị giật lag. Pin 4000 nhưng thật tế ko trâu vì màn hình lớn độ phân giải cao nên tuột pin khá nhanh.chụp ảnh được màu sắc trung thực rõ nét. Trong tầm giá 5tr con này là tốt nhất |
| 12 | 58 | 0 | 1 | Chê một phần | Video màu sắc nhợt nhạt lắm. Nhưng chuyển từ bé màn hình lên full màn trong Youtube thì video lại nhảy màu sắc sống động hơn. Chỉ 1s mong sớm sửa lỗi |
| 13 | 630 | 1 | 0 | Từ lóng/viết tắt | Máy dùng khá mượt pin trâu chs game ngon ( nếu chs pubg mà dùng gyro thì nên xem xét vì máy này dùng gyro di tâm khá chậm) hợp vs ai mua về chs game còn ai muốn sống ảo chụp hình đẹp thì mua máy khác |
| 14 | 170 | 1 | 0 | Khác | Mua con này thôi tôi lấy A10 samsung ngon hơn nhiều, chip exynos 7884 chạy liên quân max cấu hình...bao đâm |
| 15 | 72 | 0 | 1 | Phủ định | Mới mua về sử dụng được 1 tuần mà sao mình thấy mỗi lần đăng ảnh lên FB hay instagram thì ảnh đều bị vỡ bị mặc dù ảnh lúc chụp rất nét không biết có thể đổi trả được k |
| 16 | 187 | 1 | 0 | Chê một phần | Top 1-2 về tầm tiền và chức năng sử dụng nha, nhược điểm cũng có nhưng tầm tiền là quá tốt( màn hình HD+, cam bình thường so tầm tiền, to dày...uu the:màn hình rộng dễ nhìn, nhạy sáng tốt, có cam góc rộng, sạc nhanh vs redminote 7 same same |
| 17 | 858 | 1 | 0 | Từ lóng/viết tắt | sản phẩm đc mấy hôm đầu là ngon thôi ae ạ chứ 1 vài tuần sau chơi game kém bắt wifi TẠM TẠM đc mỗi chụp ảnh đẹp MÀ XEM PHIM CŨNG nét thôi mình cho 4 sao nhé nhân viên phục vụ tốt lắm CŨNG TẠM ỔN GIÁ |
| 18 | 178 | 0 | 1 | Khác | mới mua 10 ngày, màn đẹp, pin trâu, cảm ứng nhạy, wifi oke, chỉ có cảm biến vân tay kém |
| 19 | 75 | 1 | 0 | Phủ định | Máy dùng rất ổn, nhưng chơi ff không đc nhạy cho lắm, khá ổn rất đáng vs giá tiền |
| 20 | 227 | 1 | 0 | Chê một phần | Máy rất mượt, nhưng mà khi chơi pubg thì bị loạn cảm ứng , pin rất trâu , giao hàng rất nhanh , tận tình |

## 20 câu sai — Naive Bayes

| # | Index | Nhãn thật | Dự đoán | Nhóm | Câu |
|---:|---:|---:|---:|---|---|
| 1 | 9 | 1 | 0 | Phủ định | Pin nhanh hết vân tay cũng chưa đk nhạy  Nhân vien tgdd tư vấn nhiệt tình dễ thương 5 sao về phong cách bán hàng |
| 2 | 41 | 1 | 0 | Chê một phần | Pin 5000 nhưng dùng trong 1 ngày anh nhân viên cute cam chụp đẹp  Nhưng xem vd trên Youtube chỉ 720p là căng |
| 3 | 1879 | 0 | 1 | Châm biếm | Vì khe 2 dùng chung nên dùng thẻ nhớ thì chỉ dùng được 1 sim. Mua bản 128gb sẽ tiện hơn nếu dùng 2 sim :))) |
| 4 | 109 | 1 | 0 | Từ lóng/viết tắt | Sản phẩm tốt ,pin trâu mới mua đc nữa ngày có điều cam hơi lồi nhân viên phục vụ tận tình |
| 5 | 21 | 0 | 1 | Khác | Máy đã được nâng cấp  bản cập nhật và sửa lỗi Bluetooth đã nghe nhạc qua Bluetooth ngon lành |
| 6 | 27 | 0 | 1 | Phủ định | Cho em hỏi là máy em, mua được 1 tuần mà máy lâu lâu em nghe cái cốc, như là bị lỏng gì ở trong vậy, như vậy có vấn đề j k anh |
| 7 | 58 | 0 | 1 | Chê một phần | Video màu sắc nhợt nhạt lắm. Nhưng chuyển từ bé màn hình lên full màn trong Youtube thì video lại nhảy màu sắc sống động hơn. Chỉ 1s mong sớm sửa lỗi |
| 8 | 1950 | 1 | 0 | Châm biếm | Rất ok,thiết kế đt rất đẹp,điều pin tuột nhanh:))chụp hình rất ok ,chơi game bao mượt |
| 9 | 180 | 0 | 1 | Từ lóng/viết tắt | Thêm 300k lấy con realms 5i gam 4gb ngon hơn nhiều.điện thoại này chỉ có cũ sạc nhanh chứ đc gì đâu.ai mua phải cân nhắc nha. |
| 10 | 69 | 0 | 1 | Khác | Mua cũng được gần 1tuaan sài khá ổn, dung lượng cao, pin sài khá lâu mà có cái muốn làm dì cũng phải vô cài đặt mơis được. |
| 11 | 30 | 1 | 0 | Phủ định | Sản phẩm tốt, nhân viên nhiệt tình tới tận mình ra về, có điều pin không như mình mong đợi mặc dù không tác vụ gì nhiều, 32gb bộ nhớ thật sự khó đủ với mình mặc dù mình không chứa gì nhiều. Nói chung mọi thứ khác đều ok ^^ |
| 12 | 64 | 1 | 0 | Chê một phần | Máy hoàn thiện về mặt thiết kế cũng như hiệu năng, chơi pubg, tft mobile mượt mà, nhưng do sạc nhanh 30w nên lúc đầu hơi nóng |
| 13 | 2221 | 0 | 1 | Châm biếm | Sản phẩm tốt 😊 Ai chơi game cứ mang 1 em về mà chơi nhé  Ngắn gọn thế thôu =))) |
| 14 | 853 | 1 | 0 | Từ lóng/viết tắt | Mới dùng thấy cũng ok, game mượt, máy kg nóng, cam đủ dùng chỉ là pin hơi nhanh tụt, thêm thời gian nữa sẽ đánh giá sau. |
| 15 | 115 | 0 | 1 | Khác | Máy đẹp, hiệu năng tốt. Đợi sử dụng một thời gian xem thế nào. Chỉ có nhiêu đây thôi :D |
| 16 | 35 | 0 | 1 | Phủ định | Mình thấy các bạn cứ chê. Mình thấy máy dùng ok mà. Ko bị lag , fb , tiktok , coi phim , loa đều ok cả. Mình dùng dt để quay phim , chụp ảnh , bán hàng online thôi chứ k game gủng gì. Dùng messeger , rep ib ko bị đơ là sung sướng, nghe gọi loa to rõ ràng.Nhất là khoản thu cũ đổi mới còn hỗ trợ trả góp O% nữa Mình đổi note8 lấy máy này . Lo note8 nhỏ , máy dùng hơn 2 năm dãi nắng dầm mưa cùng mình rồi nên giờ cũng hay đơ nên dạo này hơi stress. Lăn tăn mãi chưa đổi vì bỏ ra nhiều tiền để mua máy mới quá tiếc. Ko nghĩ lại đơn giản đến thế luôn. Đưa máy cũ đến , cầm máy mới về. Bắt đầu từ tháng sau mỗi tháng thanh toán 1tr3 trong vòng 9 tháng  Thích bạn nhân viên tư vấn , nhiệt tình cực kỳ |
| 17 | 187 | 1 | 0 | Chê một phần | Top 1-2 về tầm tiền và chức năng sử dụng nha, nhược điểm cũng có nhưng tầm tiền là quá tốt( màn hình HD+, cam bình thường so tầm tiền, to dày...uu the:màn hình rộng dễ nhìn, nhạy sáng tốt, có cam góc rộng, sạc nhanh vs redminote 7 same same |
| 18 | 858 | 1 | 0 | Từ lóng/viết tắt | sản phẩm đc mấy hôm đầu là ngon thôi ae ạ chứ 1 vài tuần sau chơi game kém bắt wifi TẠM TẠM đc mỗi chụp ảnh đẹp MÀ XEM PHIM CŨNG nét thôi mình cho 4 sao nhé nhân viên phục vụ tốt lắm CŨNG TẠM ỔN GIÁ |
| 19 | 170 | 1 | 0 | Khác | Mua con này thôi tôi lấy A10 samsung ngon hơn nhiều, chip exynos 7884 chạy liên quân max cấu hình...bao đâm |
| 20 | 54 | 1 | 0 | Phủ định | Sử dụng một tuần, máy màn hình đẹp xem phim nghe nhạc rất tốt.chơi game nặng như liên quân PUBG rất mượt nhưng chơi khoảng một tiếng máy nóng lên là bị giật lag. Pin 4000 nhưng thật tế ko trâu vì màn hình lớn độ phân giải cao nên tuột pin khá nhanh.chụp ảnh được màu sắc trung thực rõ nét. Trong tầm giá 5tr con này là tốt nhất |

## Nhận xét trade-off

- PhoBERT A đạt F1 tiêu cực `0.921600`, cao nhất nhưng có dung lượng và độ trễ CPU lớn nhất; GPU chỉ được ghi như số tham khảo lịch sử.
- SVM đạt F1 tiêu cực `0.891643` và thường là lựa chọn truyền thống cân bằng nhất giữa chất lượng, tốc độ và dung lượng.
- Logistic Regression đạt `0.890224`; xác suất/điểm quyết định dễ khai thác hơn SVM nếu cần hiệu chỉnh sau này.
- Naive Bayes nhỏ và đơn giản, nhưng F1 tiêu cực `0.874400` thấp nhất trong bốn mô hình.
- Các ví dụ sai cho thấy phủ định, câu vừa khen vừa chê và cách viết mạng xã hội vẫn là các nguồn lỗi chính; không dùng những lỗi test này để đổi siêu tham số.
