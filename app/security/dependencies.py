from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.user_repository import UserRepository
from app.security.jwt import verify_access_token
from app.repositories.hospital_repository import HospitalRepository


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    # Extract JWT
    token = credentials.credentials

    # Verify JWT
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Get user ID from JWT
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Find user in database
    user = UserRepository.get_by_id(db, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return user

def get_current_hospital(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    # Extract JWT
    token = credentials.credentials

    # Verify JWT
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    
    # Verify that this is a hospital token
    role = payload.get("role")

    if role != "HOSPITAL":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital access required."
        )

    # Get hospital ID from JWT
    hospital_id = payload.get("hospital_id")

    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid hospital token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Find hospital in database
    hospital = HospitalRepository.get_by_id(
        db,
        int(hospital_id)
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hospital no longer exists."
        )

    # Check hospital status
    if hospital.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital account is not active."
        )

    return hospital