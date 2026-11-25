"""
Authentication API Endpoints (Phase 7).

Provides user registration, password verification, JWT issuance,
and authenticated profile retrieval.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from ...auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_claims,
)
from backend.app.db.database import DatabaseService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Unique student or institutional email")
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    name: str = Field(..., min_length=2, description="Full name")
    institution: Optional[str] = Field(default="Engineering Institute", description="College / University")
    role: Optional[str] = Field(default="Student Developer", description="Program / Role")


class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest):
    """Register a new student developer and return a signed JWT token."""
    existing = await DatabaseService.get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    hashed_pw = hash_password(req.password)
    user = await DatabaseService.create_user({
        "email": req.email,
        "hashed_password": hashed_pw,
        "name": req.name,
        "institution": req.institution,
        "role": req.role,
    })

    token = create_access_token({"sub": user["id"], "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login", response_model=AuthResponse)
async def login(req: UserLoginRequest):
    """Authenticate with email and password, returning a signed JWT token."""
    user = await DatabaseService.get_user_by_email(req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user["id"], "email": user["email"]})
    user_profile = {k: v for k, v in user.items() if k != "hashed_password"}
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_profile,
    }


@router.get("/me")
async def get_current_user_profile(claims: Dict[str, Any] = Depends(get_current_user_claims)):
    """Retrieve profile for the currently authenticated user."""
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims.")

    user = await DatabaseService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")

    return {k: v for k, v in user.items() if k != "hashed_password"}
