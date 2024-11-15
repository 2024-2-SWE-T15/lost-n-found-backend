
from fastapi import HTTPException


def getOpenID(response, provider: str) -> str:
  if provider == 'google':
    return response['sub']
  elif provider == 'kakao':
    return response['id']
  elif provider == 'naver':
    return response['response']['id']
  else:
    raise HTTPException(status_code=501, detail='Not implemented provider')
  
def getNickname(response, provider: str) -> str:
  if provider == 'google':
    return response['name']
  elif provider == 'kakao':
    return response['properties']['nickname']
  elif provider == 'naver':
    return response['response']['name']
  else:
    raise HTTPException(status_code=501, detail='Not implemented provider')

def getProfileImageURL(response, provider: str) -> str:
  if provider == 'google':
    return response['picture']
  elif provider == 'kakao':
    return response['properties']['profile_image']
  elif provider == 'naver':
    return response['response']['profile_image']
  else:
    raise HTTPException(status_code=501, detail='Not implemented provider')
  
def getEmailAddress(response, provider: str) -> str:
  if provider == 'google':
    return response['email']
  elif provider == 'kakao':
    return None
  elif provider == 'naver':
    return response['response']['email']

def convertHTTPException(e: Exception, provider: str) -> HTTPException:
  if provider == 'google':
    return HTTPException(status_code=e.response.status_code, detail=e.response.json()['error_description'])
  elif provider == 'kakao':
    return HTTPException(status_code=e.response.status_code, detail=e.response.json()['message'])
  elif provider == 'naver':
    return HTTPException(status_code=e.response.status_code, detail=e.response.json()['message'])
  else:
    raise HTTPException(status_code=501, detail='Not implemented provider')