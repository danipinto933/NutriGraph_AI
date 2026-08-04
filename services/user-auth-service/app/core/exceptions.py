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
