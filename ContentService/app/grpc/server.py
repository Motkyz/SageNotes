from grpc import aio

from app.grpc.generated import note_pb2_grpc, tag_pb2_grpc
from app.grpc.services.note_service import NoteGrpcService
from app.grpc.services.tag_service import TagGrpcService


async def start_grpc_server():
    server = aio.server()

    note_pb2_grpc.add_NoteServiceServicer_to_server(
        NoteGrpcService(),
        server
    )

    tag_pb2_grpc.add_TagServiceServicer_to_server(
        TagGrpcService(),
        server
    )

    server.add_insecure_port("[::]:9090")

    await server.start()

    print("gRPC server started on port 9090")

    await server.wait_for_termination()