"""Billing for the synthetic tiny-saas example."""


def charge(amount_cents: int) -> dict:
    return {"ok": True, "amount_cents": amount_cents}
