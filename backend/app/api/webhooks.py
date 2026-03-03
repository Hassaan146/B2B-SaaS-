import json
from fastapi import APIRouter, Request, HTTPException, status
from svix.webhooks import Webhook, WebhookVerificationError
from app.core.config import settings
from app.core.clerk import clerk

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

PRO_TIER_SLUG = "pro_tier"
FREE_TIER_LIMIT = settings.FREE_TIER_LIMIT
UNLIMITED_LIMIT = 1000000


def set_org_member_limit(org_id: str, limit: int):
    clerk.organizations.update(
        organization_id=org_id,
        max_allowed_memberships=limit
    )


def has_active_pro_plan(items: list) -> bool:
    return any(
        item.get("plan", {}).get("slug") == PRO_TIER_SLUG
        and item.get("status") == "active"
        for item in items
    )


@router.post("/clerk")
async def clerk_webhook(request: Request):
    payload = await request.body()
    headers = dict(request.headers)

    if settings.CLERK_WEBHOOK_SECRET:
        try:
            wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
            event = wh.verify(payload, headers)
        except WebhookVerificationError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid signature")
    else:
        event = json.loads(payload)

    event_type = event.get("type")
    data = event.get("data", {})

    if event_type in ["subscription.created", "subscription.updated"]:
        org_id = data.get("payer", {}).get("organization_id")
        if org_id:
            limit = (UNLIMITED_LIMIT if has_active_pro_plan(data.get("items", []))
                     else FREE_TIER_LIMIT)
            set_org_member_limit(org_id, limit)
    elif event_type in ["subscription.deleted", "subscription.cancelled"]:
        org_id = data.get("payer", {}).get("organization_id")
        if org_id:
            set_org_member_limit(org_id, FREE_TIER_LIMIT)

    return {"received": True}