from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from dotenv import load_dotenv
import os

from constants import ALGORITHM

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/login",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Debug logging
        print(f"Auth middleware - Path: {request.url.path}")
        print(f"Auth middleware - Method: {request.method}")
        
        # Get token from Authorization header
        authorization = request.headers.get("Authorization")
        print(f"Auth middleware - Authorization header: {authorization}")
        
        if not authorization or not authorization.startswith("Bearer "):
            print(f"Auth middleware - Missing or invalid authorization header")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]
        print(f"Auth middleware - Token: {token}")

        try:
            # Verify token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            print(f"Auth middleware - Decoded username: {username}")
            print(f"Auth middleware - Token payload: {payload}")

            if not username:
                print(f"Auth middleware - No username in token payload")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token payload"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Add user info to request state
            request.state.user = {"username": username, "payload": payload}
            print(f"Auth middleware - Token verification successful")

        except jwt.ExpiredSignatureError as e:
            print(f"Auth middleware - Token expired: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError as e:
            print(f"Auth middleware - JWT error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        response = await call_next(request)
        return response
