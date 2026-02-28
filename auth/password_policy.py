import re
from fastapi import HTTPException, status
from datetime import datetime, timezone
from auth.security import verify_password
from datetime import datetime, timezone, timedelta


# PASSWORD_MAX_AGE_SECONDS = 240

PASSWORD_MAX_AGE_SECONDS = 60 * 60 * 24 * 90  # 90 days
RECENT_CHANGE_THRESHOLD_MINUTES = 10

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



def password_expired(user: dict) -> bool:
    last_change = user.get("last_pass_change")

    if last_change is None:
        return True

    now = datetime.now(timezone.utc)
    age_seconds = (now - last_change).total_seconds()

    return age_seconds > PASSWORD_MAX_AGE_SECONDS


def is_password_recently_changed(user: dict) -> bool:
    last_change = user.get("last_pass_change")

    if last_change is None:
        return False

    now = datetime.now(timezone.utc)

    if last_change.tzinfo is None:
        last_change = last_change.replace(tzinfo=timezone.utc)

    diff = now - last_change
    
    return diff < timedelta(minutes=RECENT_CHANGE_THRESHOLD_MINUTES)