from enum import Enum
from datetime import datetime, timedelta,timezone
from typing import Dict, Any, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext


SECRET_KEY = "tu_super_clave_secreta" # ¡Cambiar en producción!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

FAKE_USERS_DB = {
    "tony": {"username": "tony", "hashed_password": pwd_context.hash("ironman"), "role": Role.ADMIN},
    "rhodey": {"username": "rhodey", "hashed_password": pwd_context.hash("war-machine"), "role": Role.OPERATOR},
    "pepper": {"username": "pepper", "hashed_password": pwd_context.hash("rescue"), "role": Role.VIEWER},
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

def get_authorized_user(
        allowed_roles: List[Role]
) -> Any:

    def role_verifier(user_dict: Dict[str, Any] = Depends(get_current_user)):
        user_role = user_dict.get("role")

        if user_role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acción no permitida. Rol requerido: {', '.join([r.value for r in allowed_roles])}"
            )
        return user_dict

    return role_verifier