from fastapi import APIRouter

from . import search
from . import personal_id
from . import hashtag
from . import image
from . import recommand

router = APIRouter(tags=[])

router.include_router(search.router)
router.include_router(recommand.router)

post_router = APIRouter(prefix='/{post_id}', tags=[])

post_router.include_router(personal_id.router)
post_router.include_router(hashtag.router)
post_router.include_router(image.router)
