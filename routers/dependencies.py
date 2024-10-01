import os
from datetime import timedelta
from dotenv import load_dotenv

from fastapi import Request
from fastapi_login import LoginManager

from google.auth.transport import requests as google_requests
from google.oauth2.id_token import verify_oauth2_token

load_dotenv('config/.env')

async def getCurrentUser(request: Request):
  token = request.headers.get('Authorization')
  print(token)
  try:
    idinfo = verify_oauth2_token(token, google_requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
    print("idinfo:", idinfo)
    return idinfo
  except Exception as e:
    print(str(e))
    print("unverified token")
    return None


# async def verify_token(request: Request):
#     auth_header = request.headers.get("Authorization")
#     if not auth_header:
#         raise HTTPException(status_code=401, detail="Authorization header is missing")

#     token_type, _, token = auth_header.partition(" ")
#     if token_type.lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid token type")

#     # Google 토큰 검증
#     try:
#         id_info = id_token.verify_oauth2_token(token, google_requests.Request(), os.getenv("GOOGLE_CLIENT_ID"))
#         return {"status": "success", "user_info": id_info}
#     except ValueError:
#         raise HTTPException(status_code=401, detail="Invalid Google token")

#     # Kakao 토큰 검증
#     kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(kakao_user_info_url, headers=headers)
#     if response.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid Kakao token")
#     kakao_user_info = response.json()

#     # Naver 토큰 검증
#     naver_user_info_url = "https://openapi.naver.com/v1/nid/me"
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(naver_user_info_url, headers=headers)
#     if response.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid Naver token")
#     naver_user_info = response.json()