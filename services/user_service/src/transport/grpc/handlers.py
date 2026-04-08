from uuid import UUID

from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from src.application.dto.ban import BanUserRequest
from src.application.dto.blocks import BlockPairRequest
from src.application.dto.premium import ActivatePremiumRequest
from src.application.dto.referral import ApplyReferralCodeRequest
from src.application.dto.user_settings import UpdateUserSettingsRequest
from src.application.dto.user_status import UpdateUserStatusRequest
from src.application.services.blocks_service import BlocksService
from src.application.use_cases.activate_premium import ActivatePremiumUseCase
from src.application.use_cases.apply_referral_code import ApplyReferralCodeUseCase
from src.application.use_cases.ban_user import BanUserUseCase
from src.application.use_cases.block_user import BlockUserUseCase
from src.application.use_cases.check_premium import CheckPremiumUseCase
from src.application.use_cases.deactivate_premium import DeactivatePremiumUseCase
from src.application.use_cases.generate_referral_code import GenerateReferralCodeUseCase
from src.application.use_cases.get_user_settings import GetUserSettingsUseCase
from src.application.use_cases.get_user_status import GetUserStatusUseCase
from src.application.use_cases.unblock_user import UnblockUserUseCase
from src.application.use_cases.update_user_settings import UpdateUserSettingsUseCase
from src.application.use_cases.update_user_status import UpdateUserStatusUseCase
from src.domain.exceptions import ApplicationError
from src.domain.value_objects.user_status import UserStatus
from src.generated.user.v1 import user_pb2, user_pb2_grpc
from src.infrastructure.persistence.database import async_session_maker
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


def _uow() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(async_session_maker)


def _ts(dt) -> Timestamp:
    t = Timestamp()
    t.FromDatetime(dt)
    return t


class UserServiceHandler(user_pb2_grpc.UserServiceServicer):
    async def GetUserSettings(self, request, context):
        uc = GetUserSettingsUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.UserSettings(
            id=str(result.id),
            user_id=str(result.user_id),
            language=result.language,
            show_online_status=result.show_online_status,
            show_distance=result.show_distance,
            show_age=result.show_age,
            discoverable=result.discoverable,
            push_enabled=result.push_enabled,
            email_enabled=result.email_enabled,
        )

    async def UpdateUserSettings(self, request, context):
        fields = (
            "language",
            "show_online_status",
            "show_distance",
            "show_age",
            "discoverable",
            "push_enabled",
            "email_enabled",
        )
        dto = UpdateUserSettingsRequest(
            **{f: getattr(request, f) for f in fields if request.HasField(f)}
        )

        uc = UpdateUserSettingsUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id), dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.UserSettings(
            id=str(result.id),
            user_id=str(result.user_id),
            language=result.language,
            show_online_status=result.show_online_status,
            show_distance=result.show_distance,
            show_age=result.show_age,
            discoverable=result.discoverable,
            push_enabled=result.push_enabled,
            email_enabled=result.email_enabled,
        )

    async def GetUserStatus(self, request, context):
        uc = GetUserStatusUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.UserStatus(id=str(result.id), status=result.status.value)
        if result.ban_reason is not None:
            msg.ban_reason = result.ban_reason
        if result.banned_at is not None:
            msg.banned_at.CopyFrom(_ts(result.banned_at))
        if result.deleted_at is not None:
            msg.deleted_at.CopyFrom(_ts(result.deleted_at))
        return msg

    async def UpdateUserStatus(self, request, context):
        dto = UpdateUserStatusRequest(
            status=UserStatus(request.status),
            reason=request.reason if request.HasField("reason") else None,
        )

        uc = UpdateUserStatusUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id), dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.UserStatus(id=str(result.id), status=result.status.value)
        if result.ban_reason is not None:
            msg.ban_reason = result.ban_reason
        if result.banned_at is not None:
            msg.banned_at.CopyFrom(_ts(result.banned_at))
        if result.deleted_at is not None:
            msg.deleted_at.CopyFrom(_ts(result.deleted_at))
        return msg

    async def GenerateReferralCode(self, request, context):
        uc = GenerateReferralCodeUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.ReferralCode(user_id=str(result.user_id), code=result.code)

    async def ApplyReferralCode(self, request, context):
        dto = ApplyReferralCodeRequest(user_id=UUID(request.user_id), code=request.code)

        uc = ApplyReferralCodeUseCase(uow=_uow())
        try:
            result = await uc(dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.ReferralApplyResult(
            user_id=str(result.user_id),
            referrer_id=str(result.referrer_id),
            premium_days_granted=result.premium_days_granted,
            super_likes_granted=result.super_likes_granted,
        )

    # ---------- premium ----------
    async def CheckPremium(self, request, context):
        uc = CheckPremiumUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.PremiumStatus(id=str(result.id), is_premium=result.is_premium)
        if result.premium_until is not None:
            msg.premium_until.CopyFrom(_ts(result.premium_until))
        return msg

    async def ActivatePremium(self, request, context):
        dto = ActivatePremiumRequest(user_id=UUID(request.user_id), days=request.days)

        uc = ActivatePremiumUseCase(uow=_uow())
        try:
            result = await uc(dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.PremiumStatus(id=str(result.id), is_premium=result.is_premium)
        if result.premium_until is not None:
            msg.premium_until.CopyFrom(_ts(result.premium_until))
        return msg

    async def DeactivatePremium(self, request, context):
        uc = DeactivatePremiumUseCase(uow=_uow())
        try:
            result = await uc(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.PremiumStatus(id=str(result.id), is_premium=result.is_premium)
        if result.premium_until is not None:
            msg.premium_until.CopyFrom(_ts(result.premium_until))
        return msg

    # ---------- blocks ----------
    async def BlockUser(self, request, context):
        dto = BlockPairRequest(
            blocker_id=UUID(request.blocker_id),
            blocked_id=UUID(request.blocked_id),
        )

        uc = BlockUserUseCase(uow=_uow())
        try:
            result = await uc(dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.UserBlock(
            id=str(result.id),
            blocker_id=str(result.blocker_id),
            blocked_id=str(result.blocked_id),
        )

    async def UnblockUser(self, request, context):
        dto = BlockPairRequest(
            blocker_id=UUID(request.blocker_id),
            blocked_id=UUID(request.blocked_id),
        )

        uc = UnblockUserUseCase(uow=_uow())
        try:
            await uc(dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return Empty()

    async def IsBlocked(self, request, context):
        service = BlocksService(uow=_uow())
        try:
            value = await service.is_blocked(
                UUID(request.blocker_id), UUID(request.blocked_id)
            )
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.IsBlockedResponse(is_blocked=value)

    async def ListBlocked(self, request, context):
        service = BlocksService(uow=_uow())
        try:
            ids = await service.list_blocked_ids(UUID(request.user_id))
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        return user_pb2.ListBlockedResponse(blocked_ids=[str(i) for i in ids])

    # ---------- ban ----------
    async def BanUser(self, request, context):
        dto = BanUserRequest(user_id=UUID(request.user_id), reason=request.reason)

        uc = BanUserUseCase(uow=_uow())
        try:
            result = await uc(dto)
        except ApplicationError as e:
            await context.abort(e.grpc_code, e.detail)

        msg = user_pb2.UserStatus(id=str(result.id), status=result.status.value)
        if result.ban_reason is not None:
            msg.ban_reason = result.ban_reason
        if result.banned_at is not None:
            msg.banned_at.CopyFrom(_ts(result.banned_at))
        if result.deleted_at is not None:
            msg.deleted_at.CopyFrom(_ts(result.deleted_at))
        return msg
