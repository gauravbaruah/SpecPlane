"""Transactional mail for the synthetic tiny-saas example."""


def send(to: str, body: str) -> dict:
    return {"ok": True, "to": to, "body": body}
