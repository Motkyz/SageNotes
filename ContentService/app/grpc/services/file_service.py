import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from app.db import async_session
from app.grpc.generated.file import file_pb2_grpc, file_pb2
from app.grpc.grpc_auth import grpc_auth_service
from app.repositories.file_repository import FileRepository
from app.repositories.note_repository import NoteRepository
from app.services.S3_service import s3_service
from app.use_case.files.delete_file import DeleteFileUseCase
from app.use_case.files.get_url_file import GetUrlFileUseCase


class FileGrpcService(file_pb2_grpc.FileServiceServicer):
    def __init__(self):
        self.note_repository = NoteRepository(session_factory=async_session)
        self.file_repository = FileRepository(session_factory=async_session)

        self.delete_file_use_case = DeleteFileUseCase(
            repository_for_notes=self.note_repository,
            repository_for_files=self.file_repository
        )

        self.get_url_file_use_case = GetUrlFileUseCase(
            repository_for_notes=self.note_repository,
            repository_for_files=self.file_repository
        )

    async def _file_to_proto(self, file, url: str = None) -> file_pb2.File:
        created_at = Timestamp()
        if file.created_at:
            created_at.FromDatetime(file.created_at)

        return file_pb2.File(
            id=str(file.id),
            name=file.name or "",
            url=url or "",
            extension=file.extension or "",
            mime_type=file.mime_type or "",
            size=file.size or 0,
            note_id=str(file.note_id),
            user_id=str(file.user_id),
            created_at=created_at
        )


    async def DeleteFile(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "User not authenticated"
            )
            return file_pb2.DeleteFileResponse(success=False)

        result = await self.delete_file_use_case.execute(
            file_id=str(request.file_id),
            user_id=str(user_id)
        )

        if not result:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "File not found or could not be deleted"
            )
            return file_pb2.DeleteFileResponse(success=False)

        return file_pb2.DeleteFileResponse(success=True)

    async def GetFileUrl(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "User not authenticated"
            )
            return file_pb2.GetFileUrlResponse()

        url = await self.get_url_file_use_case.execute(
            file_id=str(request.file_id),
            user_id=str(user_id)
        )

        if url is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "File not found"
            )
            return file_pb2.GetFileUrlResponse()

        return file_pb2.GetFileUrlResponse(url=url)

    async def GetNoteFiles(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "User not authenticated"
            )
            return file_pb2.GetNoteFilesResponse()

        # Получаем файлы заметки из репозитория
        file_repository = FileRepository(session_factory=async_session)
        files = await file_repository.get_files_by_note_id(
            note_id=str(request.note_id),
            user_id=str(user_id)
        )

        proto_files = []
        for file in files:
            url = await s3_service.generate_presigned_url(file.key)
            proto_files.append(await self._file_to_proto(file, url))

        return file_pb2.GetNoteFilesResponse(files=proto_files)