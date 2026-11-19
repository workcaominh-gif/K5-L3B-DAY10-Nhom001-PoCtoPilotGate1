"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc
"""
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    # Cổng 1 (Pre-guard): Ghim chính sách đang hiệu lực theo ngày ctx.as_of để chống concept drift
    pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if pol:
        return Verdict.allow(policy_id=pol["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")

    # Cổng 2 (Write-gate: Hoàn tiền): Chặn hoàn tiền sai, dựa trên quyền lợi tính từ DB tracking
    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order:
            parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            db_delay = H.db_delay_days(parcel, ctx.as_of)
            pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
            if pol:
                entitled = H.entitlement_vnd(pol, order, db_delay, parcel.get("delay_cause"))
                if action.get("amount_vnd", 0) > entitled:
                    if entitled == 0:
                        return Verdict.deny(f"Không đủ điều kiện hoàn tiền theo tracking DB ({db_delay} ngày)")
                    return Verdict.modify(f"Sửa tiền hoàn khớp quyền lợi tracking ({db_delay} ngày)", amount_vnd=entitled)

    # Cổng 3 (Write-gate: Phạt hãng): Chặn ghi lỗi hãng oan khi hãng không có lỗi theo tracking DB
    if tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order:
            parcel = next((p for p in order["parcels"] if p["parcel_id"] == action.get("parcel_id")), None) or H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            db_delay = H.db_delay_days(parcel, ctx.as_of)
            pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
            if pol and not H.carrier_at_fault(pol, parcel, db_delay):
                return Verdict.deny(f"Hãng không có lỗi theo tracking DB (trễ {db_delay} ngày, lý do {parcel.get('delay_cause')})")
            if action.get("delay_days") != db_delay:
                return Verdict.modify("Sửa số ngày trễ theo tracking DB", delay_days=db_delay)

    # Cổng 4 (Write-gate: Thông báo hãng): Lọc sạch thông tin PII trước khi gửi bên thứ ba
    if tool == "notify_carrier":
        payload = action.get("payload", {})
        blocked = set((ctx.gates or {}).get("legal", {}).get("pii_fields_blocked_to_third_party") or ["recipient_contact", "customer_note"])
        if any(k in payload for k in blocked):
            clean_payload = {k: v for k, v in payload.items() if k not in blocked}
            return Verdict.modify("Lọc bỏ trường PII trước khi gửi hãng", payload=clean_payload)

    return Verdict.allow()
