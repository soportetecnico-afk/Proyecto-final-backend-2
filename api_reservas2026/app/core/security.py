"""Funciones para generar y verificar hashes de contraseñas con scrypt."""
import hashlib
import hmac
import secrets


_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_KEY_LENGTH = 64


def hash_password(password: str) -> str:
    """Devuelve un hash scrypt con sal aleatoria; nunca guarda texto plano."""
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_KEY_LENGTH,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${derived_key.hex()}"


def verify_password(password: str, encoded_hash: str | None) -> bool:
    """Compara una contraseña con su hash almacenado."""
    if not password or not encoded_hash:
        return False

    try:
        algorithm, n, r, p, salt_hex, key_hex = encoded_hash.split("$")
        if algorithm != "scrypt":
            return False
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        calculated_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected_key),
        )
        return hmac.compare_digest(calculated_key, expected_key)
    except (ValueError, TypeError):
        return False


# Autenticación de API mediante tokens firmados HMAC-SHA256.
# En producción define AUTH_SECRET_KEY en el entorno/.env y mantenla estable.
import base64
import json
import os
import time

_AUTH_SECRET = os.getenv("AUTH_SECRET_KEY") or os.getenv("SECRET_KEY")
if not _AUTH_SECRET:
    # Respaldo de desarrollo: funciona mientras el proceso siga activo.
    # Al reiniciar FastAPI, los tokens anteriores dejan de ser válidos.
    _AUTH_SECRET = secrets.token_urlsafe(48)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def crear_token_acceso(usuario: dict, duracion_segundos: int = 8 * 60 * 60) -> str:
    ahora = int(time.time())
    encabezado = {"alg": "HS256", "typ": "JWT"}
    carga = {
        "sub": str(usuario["id_usuario"]),
        "id_rol": int(usuario["id_rol"]),
        "iat": ahora,
        "exp": ahora + duracion_segundos,
    }
    parte1 = _b64url(json.dumps(encabezado, separators=(",", ":")).encode())
    parte2 = _b64url(json.dumps(carga, separators=(",", ":")).encode())
    mensaje = f"{parte1}.{parte2}".encode("ascii")
    firma = hmac.new(_AUTH_SECRET.encode("utf-8"), mensaje, hashlib.sha256).digest()
    return f"{parte1}.{parte2}.{_b64url(firma)}"


def verificar_token_acceso(token: str) -> dict | None:
    try:
        parte1, parte2, firma_recibida = token.split(".")
        mensaje = f"{parte1}.{parte2}".encode("ascii")
        firma_esperada = _b64url(
            hmac.new(_AUTH_SECRET.encode("utf-8"), mensaje, hashlib.sha256).digest()
        )
        if not hmac.compare_digest(firma_recibida, firma_esperada):
            return None
        padding = "=" * (-len(parte2) % 4)
        carga = json.loads(base64.urlsafe_b64decode(parte2 + padding))
        if int(carga.get("exp", 0)) <= int(time.time()):
            return None
        if int(carga.get("sub", 0)) <= 0 or int(carga.get("id_rol", 0)) not in (1, 3, 5):
            return None
        return carga
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
