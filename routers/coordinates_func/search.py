from fastapi import APIRouter


router = APIRouter(prefix='/search', tags=['LostNFound-Search'])

@router.post('/')
async def searchCoordinates():
  pass