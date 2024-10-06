from fastapi import APIRouter

from . import search
from . import personal_id

router = APIRouter()

router.include_router(search.router)
router.include_router(personal_id.router)
