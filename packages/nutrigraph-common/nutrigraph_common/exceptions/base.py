class NutriGraphException(Exception):
    """Excepción base para todos los errores de la plataforma NutriGraph."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class DomainException(NutriGraphException):
    """Excepciones de Lógica de Negocio (Ej. RecipeNotFound, InsufficientStock)."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)

class ResourceNotFoundException(NutriGraphException):
    """Recurso no encontrado (Ej. Usuario no existe en DB)."""
    def __init__(self, message: str = "Recurso no encontrado", details: dict = None):
        super().__init__(message, status_code=404, details=details)

class InfrastructureException(NutriGraphException):
    """Excepciones de Infraestructura (Ej. Caída de Neo4j, timeout HTTP)."""
    def __init__(self, message: str = "Error interno de infraestructura", details: dict = None):
        super().__init__(message, status_code=500, details=details)

class ValidationException(NutriGraphException):
    """Excepciones de Validación (Inputs incorrectos desde Kafka o cliente HTTP)."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)
