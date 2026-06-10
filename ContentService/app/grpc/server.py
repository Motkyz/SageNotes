from grpc import aio

from app.grpc.generated import note_pb2_grpc
from app.grpc.services.note_service import NoteGrpcService


async def start_grpc_server():
    server = aio.server()

    note_pb2_grpc.add_NoteServiceServicer_to_server(
        NoteGrpcService(),
        server
    )

    server.add_insecure_port("[::]:9090")

    await server.start()

    print("gRPC server started on port 9090")

    await server.wait_for_termination()