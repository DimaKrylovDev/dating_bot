import uuid

from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class BlocksService:
    """Вспомогательные операции над блокировками (read-only хелперы)."""

    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def is_blocked(self, blocker_id: uuid.UUID, blocked_id: uuid.UUID) -> bool:
        async with self._uow as uow:
            return await uow.user_blocks.is_blocked(blocker_id, blocked_id)

    async def list_blocked_ids(self, blocker_id: uuid.UUID) -> list[uuid.UUID]:
        async with self._uow as uow:
            return await uow.user_blocks.list_blocked_ids(blocker_id)
