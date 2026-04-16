from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.routers import customers, orders, products


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Online Store", version="1.0.0", lifespan=lifespan)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(_: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
async def validation_handler(_: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
