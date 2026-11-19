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
        v = _refund_limits(ctx, action)          # trần đã thống nhất với Ops/Finance (ops_limits) + phê duyệt hợp lệ
        if v is not None:
            return v
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
            # Trần ops_limits: từ lỗi thứ (max+1) của cùng một hãng trong ngày phải có người duyệt
            cap = ctx.tools.ops_limits().get("max_auto_strikes_per_carrier_per_day")
            carrier = action.get("carrier_id") or parcel.get("carrier_id")
            if cap is not None and len(ctx.tools.fault_rows(carrier_id=carrier)) >= cap:
                return Verdict.escalate(f"Hãng {carrier} đã có {cap} lỗi tự động hôm nay, lỗi tiếp theo cần người duyệt")
            if action.get("delay_days") != db_delay:
                return Verdict.modify("Sửa số ngày trễ theo tracking DB", delay_days=db_delay)

    # Cổng 4 (Write-gate: Thông báo hãng): chỉ gửi bên thứ ba đúng các trường chính sách cho phép
    # (carrier_notice_fields, danh sách cho phép thay vì danh sách cấm) và số ngày trễ theo tracking DB.
    if tool == "notify_carrier":
        payload = dict(action.get("payload") or {})
        blocked = set((ctx.gates or {}).get("legal", {}).get("pii_fields_blocked_to_third_party") or ["recipient_contact", "customer_note"])
        pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        allowed = set(pol.get("carrier_notice_fields") or []) if pol else set()
        clean = {k: v for k, v in payload.items() if k not in blocked and (not allowed or k in allowed)}
        order = ctx.tools.lookup_order(payload.get("order_id") or action.get("order_id"))
        if order and "delay_days" in clean:
            parcel = next((p for p in order["parcels"] if p["parcel_id"] == clean.get("parcel_id")), None) or H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            clean["delay_days"] = H.db_delay_days(parcel, ctx.as_of)
        if clean != payload:
            return Verdict.modify("Chỉ gửi hãng các trường được phép, số ngày trễ theo tracking DB", payload=clean)

    return Verdict.allow()


def _refund_limits(ctx, action):
    """Trần hoàn tiền đã thống nhất (data/world.json -> ops_limits) và hạn mức tự động của chính sách.
    Trả về Verdict khi phải chuyển người duyệt, None khi được đi tiếp."""
    amount = action.get("amount_vnd", 0) or 0
    lim = ctx.tools.ops_limits()
    customer = action.get("customer_id") or (ctx.ticket or {}).get("customer_id")   # lệnh hoàn không mang customer_id
    approval_id = action.get("approval_id")
    if approval_id:
        # Có viện dẫn phê duyệt: phải đúng đơn, đúng khách, còn hiệu lực, chưa dùng, đủ hạn mức.
        ok = [a for a in ctx.tools.lookup_approvals(approval_id=approval_id)
              if a.get("status") == "valid" and a.get("order_id") == action.get("order_id")
              and a.get("customer_id") == customer
              and a.get("expires_at", "") >= ctx.as_of and amount <= a.get("max_vnd", 0)]
        if not ok:
            return Verdict.escalate(f"Phê duyệt {approval_id} không hợp lệ cho khoản hoàn này, chuyển người duyệt")
        return None
    pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if pol and amount > pol.get("auto_limit_vnd", amount):
        return Verdict.escalate(f"Khoản hoàn {amount}đ vượt hạn mức tự động {pol['auto_limit_vnd']}đ, cần phê duyệt")
    per_customer = lim.get("max_auto_refund_per_customer_per_day_vnd")
    if per_customer is not None:
        today = sum(r["amount_vnd"] for r in ctx.tools.ledger_rows(customer_id=customer)
                    if not r.get("approval_id"))
        if today + amount > per_customer:
            return Verdict.escalate(f"Tổng hoàn tự động cho khách vượt {per_customer}đ/ngày, chuyển người duyệt")
    return None
