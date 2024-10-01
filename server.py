import os
import jwt
import json
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from routers.dependencies import getCurrentUser
from routers import authenticator

load_dotenv("./config/.env")

app = FastAPI()

@app.middleware("http")
async def checkHeader(request, call_next):
  if request.headers:
    import requests
    import rsa
    import base64
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa
    from cryptography.hazmat.primitives import serialization
    token = request.headers.get('Authorization')
    print(token)
    jwks_uri = 'https://www.googleapis.com/oauth2/v3/certs'
    r = requests.get('https://www.googleapis.com/oauth2/v3/certs')
    parsed = json.loads(r.text)['keys']
    print(parsed)
    for p in parsed:
      print(p["n"], p["e"])
      n_int = int.from_bytes(base64.urlsafe_b64decode(p["n"] + '=='), byteorder='big')
      e_int = int.from_bytes(base64.urlsafe_b64decode(p["e"] + '=='), byteorder='big')

      public_key = crypto_rsa.RSAPublicNumbers(e_int, n_int).public_key(default_backend())

      public_pem = public_key.public_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PublicFormat.SubjectPublicKeyInfo
      ).decode('utf-8')
      try:
        tokenData = jwt.decode(token, public_pem, algorithms=["RS256"])
        print(tokenData)
        data = {key: value for key, value in tokenData.items() if key not in {"exp", "scopes"}}
        print(data)
      except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print("jwtError")
  
  response = await call_next(request)
  return response
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET'))
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(authenticator.router)

from fastapi.responses import RedirectResponse
import requests
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = f"https://caring-sadly-marmoset.ngrok-free.app/auth/google"

@app.get("/")
async def root():
  return {"message": "Hello World"}



if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT')), reload=True)