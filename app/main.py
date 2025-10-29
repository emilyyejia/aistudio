import os
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from app import db
from app.schemas import UserCreate, UserOut, Token
from app.auth import hash_password, verify_password, create_access_token

app = FastAPI(title="FastAPI Neon Auth")


@app.on_event("startup")
async def startup():
    # load .env if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    if not (os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")):
        raise RuntimeError("Set NEON_DATABASE_URL or DATABASE_URL environment variable")
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.close()


@app.post("/signup", response_model=UserOut)
async def signup(payload: UserCreate):
    # check existing
    existing = await db.fetchrow("SELECT id,email,created_at FROM users WHERE email=$1", payload.email)
    if existing:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = hash_password(payload.password)
    row = await db.fetchrow(
        "INSERT INTO users (email,password_hash) VALUES ($1,$2) RETURNING id,email,created_at",
        payload.email,
        hashed,
    )
    return dict(row)


@app.post("/login", response_model=Token)
async def login(payload: UserCreate):
    row = await db.fetchrow("SELECT id,email,password_hash FROM users WHERE email=$1", payload.email)
    if not row:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(row["id"]), "email": row["email"]})
    return {"access_token": token, "token_type": "bearer"}
