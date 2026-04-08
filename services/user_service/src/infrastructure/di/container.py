from functools import lru_cache

from src.application.interfaces.unit_of_work import AbstractUnitOfWork
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
from src.infrastructure.persistence.database import async_session_maker
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


class Container:
    def __init__(self) -> None:
        self._session_maker = async_session_maker

    def uow(self) -> AbstractUnitOfWork:
        return SQLAlchemyUnitOfWork(self._session_maker)

    # settings
    def get_user_settings(self) -> GetUserSettingsUseCase:
        return GetUserSettingsUseCase(self.uow())

    def update_user_settings(self) -> UpdateUserSettingsUseCase:
        return UpdateUserSettingsUseCase(self.uow())

    # status
    def get_user_status(self) -> GetUserStatusUseCase:
        return GetUserStatusUseCase(self.uow())

    def update_user_status(self) -> UpdateUserStatusUseCase:
        return UpdateUserStatusUseCase(self.uow())

    # referral
    def generate_referral_code(self) -> GenerateReferralCodeUseCase:
        return GenerateReferralCodeUseCase(self.uow())

    def apply_referral_code(self) -> ApplyReferralCodeUseCase:
        return ApplyReferralCodeUseCase(self.uow())

    # premium
    def activate_premium(self) -> ActivatePremiumUseCase:
        return ActivatePremiumUseCase(self.uow())

    def deactivate_premium(self) -> DeactivatePremiumUseCase:
        return DeactivatePremiumUseCase(self.uow())

    def check_premium(self) -> CheckPremiumUseCase:
        return CheckPremiumUseCase(self.uow())

    # blocks
    def block_user(self) -> BlockUserUseCase:
        return BlockUserUseCase(self.uow())

    def unblock_user(self) -> UnblockUserUseCase:
        return UnblockUserUseCase(self.uow())

    def blocks_service(self) -> BlocksService:
        return BlocksService(self.uow())

    # ban
    def ban_user(self) -> BanUserUseCase:
        return BanUserUseCase(self.uow())


@lru_cache
def get_container() -> Container:
    return Container()
