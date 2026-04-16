class DomainError(Exception):
    """Базовая доменная ошибка сервисного слоя."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass
