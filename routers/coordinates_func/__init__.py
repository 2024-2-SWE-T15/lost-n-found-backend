from fastapi import APIRouter

from .stronghold import router as stronghold_router

router = APIRouter()

router.include_router(stronghold_router)