from fastapi import APIRouter 

from api.api_v1.endpoints.api_routes import router

v1_router = APIRouter()

v1_router.include_router(
    router,
    # prefix="test_cases",
    # tags=["test_cases"]
)