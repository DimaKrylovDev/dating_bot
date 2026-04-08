import datetime

from fastapi import HTTPException
from jose import JWTError

from src.persistance.unit_of_work import SQLAlchemyUnitOfWork
from src.usecase.base import AuthBaseUsecase
from src.usecase.refresh.request import RefreshRequest
from src.usecase.refresh.response import RefreshResponse


class RefreshUsecase(AuthBaseUsecase):
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def execute(self, request: RefreshRequest) -> RefreshResponse:
        try:
            payload = self.decode_token(request.refresh_token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        session_id = payload.get("session_id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        async with self._uow as uow:
            session = await uow.sessions.get_by_id(session_id)
            if not session or not session.is_active:
                raise HTTPException(status_code=401, detail="Session expired")

            await uow.sessions.update(
                session.id,
                last_active_at=datetime.datetime.now(),
            )

            access_token = self.create_access_token(session.user_id)

            await uow.commit()

        return RefreshResponse(access_token=access_token)
