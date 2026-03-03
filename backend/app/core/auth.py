import httpx
from fastapi import HTTPException, status, Request, Depends
from clerk_backend_api.security import AuthenticateRequestOptions
from app.core.config import settings
from app.core.clerk import clerk


class AuthUser:
    def __init__(self, id: str, org_id: str, org_permissions: list):
        self.id = id
        self.org_id = org_id
        self.org_permissions = org_permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.org_permissions

    @property
    def can_view(self) -> bool:
        return self.has_permission("org:tasks:view")

    @property
    def can_edit(self) -> bool:
        return self.has_permission("org:tasks:edit")

    @property
    def can_delete(self) -> bool:
        return self.has_permission("org:tasks:delete")

    @property
    def can_create(self) -> bool:
        return self.has_permission("org:tasks:create")


# ----------- FIXED: async function to await body -----------
async def connvert_to_httpx_request(fastapi_request: Request) -> httpx.Request:
    body_bytes = await fastapi_request.body()  # await is required
    return httpx.Request(
        method=fastapi_request.method,
        url=str(fastapi_request.url),
        headers=fastapi_request.headers.raw,
        content=body_bytes
    )

async def get_current_user(fastapi_request: Request) -> AuthUser:
    # ✅ MUST await this
    httpx_request = await connvert_to_httpx_request(fastapi_request)

    options = AuthenticateRequestOptions(
        authorized_parties=[settings.FRONTEND_URL]
    )

    try:
        # ✅ NO await here
        auth_response = clerk.authenticate_request(httpx_request, options)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    claims = auth_response.payload
    user_id = claims.get("sub")
    org_id = claims.get("org_id")
    org_permissions = claims.get("org_permissions") or []

    if not user_id:
        raise HTTPException(status_code=401, detail="No user")
    if not org_id:
        raise HTTPException(status_code=400, detail="No org")

    return AuthUser(
        id=user_id,
        org_id=org_id,
        org_permissions=org_permissions
    )


# ---------------- Permission Dependencies ----------------

def require_view(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_view:
        raise HTTPException(status_code=403, detail="View permission required")
    return user


def require_create(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_create:
        raise HTTPException(status_code=403, detail="Create permission required")
    return user


def require_edit(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_edit:
        raise HTTPException(status_code=403, detail="Edit permission required")
    return user


def require_delete(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_delete:
        raise HTTPException(status_code=403, detail="Delete permission required")
    return user