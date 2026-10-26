# T28 — Chỉ mục ảnh và probe

Bắt đầu 26/10, hoàn tất báo cáo 27/10/2026 (Asia/Saigon). Ảnh PNG và JSON probe đặt ngoài repo tại thư mục visualization của chat để tuân thủ allowlist mục 6 (reports chỉ cho phép Markdown). Các số đo chính được chép vào implementation report trong Git.

Ảnh trước dùng frontend tại baseline `bca6d23`; ảnh sao tái hiện bằng mouseover → 40 ms → mouseout → 400 ms với CSS/StarRating baseline. Ảnh sau dùng source T28, trình duyệt Edge qua Playwright có sẵn; không thêm thư viện. Các ảnh toàn trang có thể dùng chung cho nhiều lỗi xuất hiện trên cùng màn hình.

| Lỗi | Trước 375px | Sau 375px | Trước 1280px | Sau 1280px |
|---|---|---|---|---|
| UI-01 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-1280.png>) |
| UI-02 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-1280.png>) |
| UI-03 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-1280.png>) |
| UI-04 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-explore-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-explore-1280.png>) |
| UI-05 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-1280.png>) |
| FX-01 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-stars-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-stars-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-stars-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-stars-1280.png>) |
| FX-02 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-stars-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-stars-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-stars-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-stars-1280.png>) |
| FX-03 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-detail-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-detail-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-detail-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-detail-1280.png>) |
| FX-04 | [before 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-375.png>) | [after 375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-375.png>) | [before 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/before-home-1280.png>) | [after 1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/after-home-1280.png>) |

## Tài khoản và phim mới

| Tình huống | 375px | 1280px |
|---|---|---|
| Tài khoản real, empty | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-real-empty-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-real-empty-1280.png>) |
| Tài khoản real, activity | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-real-activity-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-real-activity-1280.png>) |
| Tài khoản mock, empty | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-mock-empty-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-mock-empty-1280.png>) |
| Tài khoản mock, activity | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-mock-activity-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/account-mock-activity-1280.png>) |
| Phim mới qua form admin, home | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-home-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-home-1280.png>) |
| Phim mới qua form admin, explore | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-explore-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-explore-1280.png>) |
| Phim mới qua form admin, detail | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-detail-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-detail-1280.png>) |
| Phim mới qua form admin, dialog | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-dialog-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/new-movie-dialog-1280.png>) |

## Dữ liệu probe

- [probes.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/probes.json>)
- [header-footer-hero.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/header-footer-hero.json>)
- [mock-status.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/mock-status.json>)
- [regression.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/regression.json>)
- [ac13.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/ac13.json>)
- [additional.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/additional.json>)
- [health.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/health.json>)

Đây là bằng chứng thực thi của Codex, chờ Claude kiểm tra độc lập; không phải kết luận review.

- [Đối chiếu OBS-01 trên master](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/baseline-obs01.txt>)

- [Hồi quy điều hướng/hero/PosterIntro/menu/tìm kiếm](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/navigation.json>)

- [Header với họ tên đủ 100 ký tự](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28/long-name-header.json>)
