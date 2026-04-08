import grpc

from src.generated.user.v1 import user_pb2_grpc
from src.transport.grpc.handlers import UserServiceHandler


async def serve(host: str = "0.0.0.0", port: int = 50051) -> None:
    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceHandler(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()
