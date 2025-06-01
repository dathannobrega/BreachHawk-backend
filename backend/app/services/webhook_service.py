import httpx
from db.models.webhook import Webhook

async def dispatch_hooks(leak, db, user_id: int):
    hooks = db.query(Webhook).filter_by(user_id=user_id, enabled=True).all()
    for hook in hooks:
        try:
            await httpx.post(hook.url, json={
                "company": leak.company,
                "source_url": leak.source_url,
                "found_at": str(leak.found_at),
            }, timeout=5)
        except Exception as e:
            print(f"[!] Falha ao enviar hook: {e}")
