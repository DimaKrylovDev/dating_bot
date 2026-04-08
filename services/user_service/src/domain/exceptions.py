import grpc


class ApplicationError(Exception):
    grpc_code: grpc.StatusCode = grpc.StatusCode.INTERNAL
    message: str = "application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(self.detail)


class UserNotFoundError(ApplicationError):
    grpc_code = grpc.StatusCode.NOT_FOUND
    message = "user not found"


class UserSettingsNotFoundError(ApplicationError):
    grpc_code = grpc.StatusCode.NOT_FOUND
    message = "user settings not found"


class ReferralCodeAlreadyAssignedError(ApplicationError):
    grpc_code = grpc.StatusCode.ALREADY_EXISTS
    message = "referral code already assigned"


class ReferralCodeNotFoundError(ApplicationError):
    grpc_code = grpc.StatusCode.NOT_FOUND
    message = "referral code not found"


class SelfReferralError(ApplicationError):
    grpc_code = grpc.StatusCode.INVALID_ARGUMENT
    message = "cannot refer self"


class AlreadyReferredError(ApplicationError):
    grpc_code = grpc.StatusCode.FAILED_PRECONDITION
    message = "user already referred"


class CannotBlockSelfError(ApplicationError):
    grpc_code = grpc.StatusCode.INVALID_ARGUMENT
    message = "cannot block self"


class UserAlreadyBlockedError(ApplicationError):
    grpc_code = grpc.StatusCode.ALREADY_EXISTS
    message = "user already blocked"
