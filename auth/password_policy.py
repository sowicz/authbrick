import re
from fastapi import HTTPException, status
from auth.security import verify_password


def validate_password_strength(password: str):
    if len(password) < 8 or len(password) > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8-24 characters long",
        )

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain uppercase letter",
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain a digit",
        )

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain special character",
        )


def validate_password_not_reused(new_password: str, current_hash: str):
    if verify_password(new_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
