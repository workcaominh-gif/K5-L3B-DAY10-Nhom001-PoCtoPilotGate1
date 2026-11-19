# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): Nhom001
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-Nhom001-PoCtoPilotGate1` (https://github.com/workcaominh-gif/K5-L3B-DAY10-Nhom001-PoCtoPilotGate1)
- Eval card và PRD v1.1 dùng chung (Lab 9, bản của Cao Duy Minh): [eval_card.md](https://github.com/workcaominh-gif/K5-L3B-DAY09-CaoDuyMinh-2A202603988-EvaluationandFailureAnalysis/blob/main/docs/eval_card.md) · [PRD_v1.1.md](https://github.com/workcaominh-gif/K5-L3B-DAY09-CaoDuyMinh-2A202603988-EvaluationandFailureAnalysis/blob/main/docs/PRD_v1.1.md)
- Thẻ sự cố đã bốc (S1–S8): S7

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Cao Duy Minh | 2A202603988 | Sản phẩm và kinh doanh | ✔ |
|   2 | Hoàng Thế Duyệt | 2A202603980 | Vận hành và pháp lý | |
|   3 | Nguyễn Khắc Bào | 2A202604072 | Kỹ sư cổng | |
|   4 | Hoàng Nhật Minh | 2A202603992 | Kỹ sư cổng | |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## CaoDuyMinh-2A202603988

### Phần việc phụ trách

Vai: Sản phẩm và kinh doanh (P&D, Trưởng nhóm).
Phụ trách:
- Thiết lập bộ tiêu chí chấp nhận trong `config/acceptance_criteria.json` và thực hiện ký điện tử `python -m lab10.criteria sign`.
- Hoàn thiện Phiếu A (form-a-criteria.md).
- Thảo luận cùng cả bàn về Pre-mortem (B6), Quyết định Gate 1 v1 (B8) và Quyết định Gate 1 v2 (C12).

### Đóng góp cụ thể

- Phân bổ chỉ số ngưỡng chấp nhận: pass_rate_min = 0.90, pass_k_min = 0.85, 0 hoàn sai, 0 phạt oan, 0 lộ PII, cost <= 5000đ, ROI >= 0.5.
- Cân bằng góc nhìn kinh doanh: chấp nhận chi phí LLM max 1500đ để đổi lấy tiết kiệm ròng > 120.000đ/ngày so với xử lý thủ công (10.000đ/ticket).
- Ký duyệt quyết định v1 "Tiếp tục" và bảo vệ quyết định v2 "Tiếp tục" sau sự cố S7 dựa trên dữ liệu định lượng.

### Bằng chứng

- Commit ký tiêu chí: `ba1d264 Sign acceptance criteria` (hash `29efda081d8f7d93ae69f6d523731efe924323892725e37a9bc818bf961c3aac`).
- Các mục hoàn thành trong phiếu: Phiếu A, Phiếu B (B0, B8), Phiếu C (C12).

### Exit ticket

- Một điều học được: Ký tiêu chí chấp nhận trước khi đo lường giúp ngăn ngừa thiên kiến xác nhận (confirmation bias) và tránh việc tự hạ chuẩn khi gặp lỗi.
- Một điều còn chưa chắc: Cách tính ROI giả định trong môi trường PoC cần được hiệu chỉnh lại với dữ liệu chi phí nhân sự thực tế trong pha pilot.

---

## HoangTheDuyet-2A202603980

### Phần việc phụ trách

Vai: Vận hành và pháp lý (Ops & Legal).
Phụ trách:
- Phiếu A: câu 1.2 (mục tiêu nhìn từ chị Oanh và chị Hạnh), câu 1.4 (telemetry production).
- Phiếu B: câu 2.4 (B4 HAZOP vòng 1 trên `file_carrier_fault`, B5 checklist 9 nhóm việc); câu 2.10 (B7.5 runbook phần 1–3, B7.6 giờ cao điểm).
- `config/operating_gates.json` mục `operations` và `legal`.
- Phiếu C, thẻ S7 (pháp lý): rà và sửa C4 (HAZOP của thẻ), C11 (cập nhật checklist, kịch bản giờ cao điểm ở Runbook 5); PIC dòng Risk register C10.

### Đóng góp cụ thể

- Đặt cổng pháp lý vòng 1 `legal.pii_fields_blocked_to_third_party = ["recipient_contact", "customer_note"]` và `carrier_fault_requires_recorded_cause = true`, trước khi biết sự cố. Trên gói S7, số lần lộ dữ liệu cá nhân cho hãng giảm từ 30 (base) xuống 0 (prepared), cùng với cổng allowlist của Kỹ sư cổng.
- Đặt mục `operations`: PIC `NV-TUNG`, người duyệt `NV-HANH`, 1 người trực × 6 ca/giờ, chờ tối đa 60 phút, 5 điều kiện dừng, kênh `#logix-refund-pilot`; chạy kiểm `R-base-after-20261119-153807-4bc37a`: không có ca mới hỏng.
- HAZOP vòng 1 tìm ra nhánh chưa thấy trên trace: chính sách REFUND-v4 (từ 2026-12-01) không coi bất khả kháng là lỗi hãng; và hai trường `recipient_contact`, `customer_note` mà `lab10/agent.py` gửi cho hãng ngoài `carrier_notice_fields`.
- Tính chi phí giờ cao điểm: thêm 1 người trực (30.000đ/ca) với 22 ticket/ngày đẩy chi phí lên ≈ 5.567đ/ticket, vượt trần 5.000đ đã ký; chỉ thêm người khi ≥ 38 ticket/ngày.

### Bằng chứng

- Commit `7f07a83` (Phiếu A câu 1.2, 1.4), `827f74b` (Phiếu B B4, B5), `584dc46` (`operating_gates.json` mục `operations`, `legal`; runbook B7.5, B7.6; cập nhật B5).
- Mã lần chạy `R-base-after-20261119-153807-4bc37a` (kiểm config vòng 1); report tự kiểm tra S7: dòng "pháp lý: lần lộ dữ liệu cá nhân cho bên thứ ba" base 30 → prepared 0.
- Phiếu A mục A1, A2; Phiếu B mục B4, B5, B7.5, B7.6; Phiếu C mục C4, C11.

### Exit ticket

- Một điều học được: An toàn AI không chỉ là prompt hay model, mà phần lớn nằm ở các cổng ràng buộc pháp lý và quy trình phối hợp người - máy (human-in-the-loop).
- Một điều còn chưa chắc: Cơ chế thu hồi dữ liệu đã gửi sang hệ thống của đối tác vận chuyển trong trường hợp tài xế đã lưu số offline.

---

## NguyenKhacBao-2A202604072

### Phần việc phụ trách

Vai: Kỹ sư cổng (Gate Engineer).
Phụ trách:
- Thiết kế và lập trình các cổng an toàn kỹ thuật trong `lab10/guards.py` (`pre_guard`, `write_gate`).
- Đo lường đánh giá baseline (`before`, `after`, `prepared`) qua `lab10.eval`.
- Thực hiện chốt cổng vòng 1 (`python -m lab10.checkpoint`).
- Dò vết lỗi (trace analysis) các ticket hỏng trên bộ nền và bộ sự cố S7 (`S7-01`, `S7-04`, `S7-20`, `S7-05`).

### Đóng góp cụ thể

- Triển khai cổng `pre_guard` ghim phiên bản chính sách hiệu lực theo ngày (`effective_policy`).
- Triển khai `write_gate` cho `issue_refund` (chặn lệch quyền lợi theo DB tracking), `file_carrier_fault` (chặn phạt oan hãng đối tác), và `notify_carrier` (áp dụng allowlist `carrier_notice_fields`, loại bỏ PII).
- Cổng vòng 1 chốt hash `7fe01b53` giúp bảo vệ hệ thống trước sự cố S7, giải quyết triệt để 30 ca lộ dữ liệu ở mốc prepared.

### Bằng chứng

- Checkpoint vòng 1: `config/round1.lock` (hash `7fe01b53`).
- Báo cáo chạy thực nghiệm: `R-base-before-20261119-145614-bde05c`, `R-base-after-20261119-155144-23dd30`, `R-base-prepared-20261119-160341-724f4d`.
- Phiếu B mục B1, B2, B7; Phiếu C mục C0, C1, C2, C6, C7, C9.

### Exit ticket

- Một điều học được: Cổng can thiệp ở tầng tool dispatch (`write_gate`) có tính phòng thủ vượt trội so với việc cố gắng tinh chỉnh prompt hay phụ thuộc vào mô hình LLM.
- Một điều còn chưa chắc: Làm thế nào để tự động sinh allowlist trường dữ liệu từ hợp đồng đối tác mà không cần cấu hình thủ công.

---

## HoangNhatMinh-2A202603992

### Phần việc phụ trách

Vai: Kỹ sư cổng / Đánh giá chất lượng (Gate Engineer / QA).
Phụ trách:
- Xây dựng chỉ số theo dõi mới `pii_recipient_leak_rate` trong `lab10/monitors.py`.
- Thực hiện kiểm tra toàn diện qua `lab10.grade --incident S7` và kiểm tra tính hồi quy trên bộ test nền.
- Hoàn thiện mục C8 (Monitor mới), C3.3 (Hiệu chỉnh lòng tin), và hỗ trợ C11, C12 trong Phiếu C.
- Chạy kiểm tra và thu thập bài nộp qua `python -m lab10.check_submission --collect`.

### Đóng góp cụ thể

- Lập trình hàm `pii_recipient_leak_rate(trials)` để phát hiện ngay các thông điệp gửi hãng (`carrier:*`) có chứa thông tin `recipient_contact`. Monitor này sáng đèn thành công ở mốc base (tỷ lệ 0.25) và trở về 0.0 ở mốc after.
- Đạt kết quả kiểm thử tự động `PASS-VISIBLE` cho sự cố S7 (vượt qua tất cả các bài kiểm tra Integrity, Criteria, Visible, Regression, Monitor).
- Rà soát tính toàn vẹn của repo, đảm bảo LF line endings và khớp hash `MANIFEST.json`.

### Bằng chứng

- Báo cáo kiểm tra tự động: `R-S7-grade-20261119-162309-821b17` (kết quả `PASS-VISIBLE`).
- Mã chạy after: `R-S7-after-20261119-162305-821b17`.
- Code monitor: `lab10/monitors.py` (hàm `pii_recipient_leak_rate`).
- Phiếu C mục C3.3, C8, C11, C12.

### Exit ticket

- Một điều học được: Việc thiết kế chỉ số giám sát (monitor) trong môi trường production không có nhãn đúng/sai (unlabeled) đòi hỏi phải tư duy dựa trên các thuộc tính của sự kiện (events, outbound payloads).
- Một điều còn chưa chắc: Ngưỡng cảnh báo tự động tối ưu cho monitor để tránh báo động giả khi lượng ticket tăng đột biến trong đợt sale.
