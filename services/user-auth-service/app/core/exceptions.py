from typing import Any

from fastapi import HTTPException, status


class DomainException(HTTPException):
    def __init__(self, status_code: int, detail: str, context: dict[str, Any] | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.context = context or {}

class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
            context={"email": email}
        )

class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            context={}
        )

class EmailNotRegisteredException(DomainException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo no registrado",
            context={}
        )

class UserNotFoundException(DomainException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            context={"email": email}
        )

class UserNotVerifiedException(DomainException):
    def __init__(self, email: str = ""):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu correo electrónico antes de iniciar sesión. Revisa tu bandeja de entrada o solicita un nuevo enlace.",
            context={"email": email}
        )

class InvalidVerificationTokenException(DomainException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de verificación es inválido o ha expirado.",
            context={}
        )

