"""
API v1 router – registers all sub-routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.expenses import router as expenses_router
from app.api.v1.endpoints.budgets import router as budgets_router
from app.api.v1.endpoints.analytics import router as analytics_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(expenses_router)
router.include_router(budgets_router)
router.include_router(analytics_router)
