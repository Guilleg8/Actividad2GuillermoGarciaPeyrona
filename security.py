# security.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

# --- Configuración JWT y Seguridad ---
SECRET_KEY = "tu_super_clave_secreta" # ¡Cambiar en producción!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Roles definidos [cite: 44]
class Role(str, Enum):
    ADMIN = "admin" # Acceso completo [cite: 45]
    OPERATOR = "operator" # Procesamiento de eventos [cite: 46]
    VIEWER = "viewer" # Solo lectura [cite: 47]

# Base de datos de usuarios simulada
FAKE_USERS_DB = {
    "tony": {"username": "tony", "hashed_password": pwd_context.hash("ironman"), "role": Role.ADMIN},
    "rhodey": {"username": "rhodey", "hashed_password": pwd_context.hash("war-machine"), "role": Role.OPERATOR},
    "pepper": {"username": "pepper", "hashed_password": pwd_context.hash("rescue"), "role": Role.VIEWER},
}

# --- Funciones de JWT y Autenticación ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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

# --- Dependencia de Autorización (Roles) ---

# security.py (CORRECTED)
# security.py

# ... (tus otras importaciones y código) ...

def get_authorized_user(
        allowed_roles: List[Role]
) -> Any:
    """
    Fábrica de dependencias que crea y devuelve la función 'role_verifier' (el callable)
    que FastAPI ejecutará para autenticar y autorizar.
    """

    # Función interna que verifica el rol después de la autenticación
    def role_verifier(user_dict: Dict[str, Any] = Depends(get_current_user)):
        # user_dict es el resultado *resuelto* de get_current_user (el diccionario)
        user_role = user_dict.get("role")

        if user_role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acción no permitida. Rol requerido: {', '.join([r.value for r in allowed_roles])}"
            )
        return user_dict  # Devolver el objeto de usuario

    # ¡LA CLAVE! Devolver la función callable 'role_verifier'
    return role_verifier  # <-- ¡CORREGIDO! Devolvemos la función, no Depends(funcion)