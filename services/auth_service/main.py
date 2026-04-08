import asyncio

from src.transport.grpc.server import serve


if __name__ == "__main__":
    asyncio.run(serve())
