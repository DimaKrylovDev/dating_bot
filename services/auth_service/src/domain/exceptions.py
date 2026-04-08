import grpc


class ApplicationError(Exception):
    grpc_code: grpc.StatusCode = grpc.StatusCode.INTERNAL
    message: str = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(self.detail)


class UserAlreadyExistsError(ApplicationError):
    grpc_code = grpc.StatusCode.ALREADY_EXISTS
    message = "user already exists"


class InvalidCredentialsError(ApplicationError):
    grpc_code = grpc.StatusCode.UNAUTHENTICATED
    message = "invalid credentials"


class SessionNotFoundError(ApplicationError):
    grpc_code = grpc.StatusCode.NOT_FOUND
    message = "session not found"


class InvalidRefreshTokenError(ApplicationError):
    grpc_code = grpc.StatusCode.UNAUTHENTICATED
    message = "invalid refresh token"


class SessionExpiredError(ApplicationError):
    grpc_code = grpc.StatusCode.UNAUTHENTICATED
    message = "session expired"
