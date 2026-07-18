from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse

router = APIRouter(tags=["System"])


def not_implemented(module: str) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "success": False,
            "error_code": "NOT_IMPLEMENTED",
            "message": f"{module} API contract is registered and ready for implementation.",
        },
    )


@router.get("/auth/me")
async def auth_me() -> ORJSONResponse:
    return not_implemented("Auth")


@router.get("/users/me")
async def users_me() -> ORJSONResponse:
    return not_implemented("Users")


@router.get("/conversations")
async def conversations() -> ORJSONResponse:
    return not_implemented("Conversations")


@router.get("/documents")
async def documents() -> ORJSONResponse:
    return not_implemented("Documents")


@router.get("/dashboard/overview")
async def dashboard() -> ORJSONResponse:
    return not_implemented("Dashboard")


@router.get("/notifications")
async def notifications() -> ORJSONResponse:
    return not_implemented("Notifications")


@router.get("/search")
async def search() -> ORJSONResponse:
    return not_implemented("Search")


@router.get("/settings/me")
async def settings() -> ORJSONResponse:
    return not_implemented("Settings")


@router.get("/admin/dashboard")
async def admin() -> ORJSONResponse:
    return not_implemented("Admin")
