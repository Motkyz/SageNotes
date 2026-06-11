import grpc
from temporalio.client import Client

from app.db import async_session
from app.grpc.generated.note import note_pb2, note_pb2_grpc
from app.grpc.grpc_auth import grpc_auth_service
from app.repositories.note_repository import NoteRepository
from app.schemas.note_schemas import NoteCreate, NoteUpdate
from app.services.S3_service import s3_service
from app.use_case.notes.create_note import CreateNoteUseCase
from app.use_case.notes.delete_note import DeleteNoteUseCase
from app.use_case.notes.get_note import GetNoteUseCase
from app.use_case.notes.get_notes_by_user_id import GetNotesByUserIdUseCase
from app.use_case.notes.update_note import UpdateNoteUseCase
from app.utils.workflows import SaveNoteWorkflow


class NoteGrpcService(
    note_pb2_grpc.NoteServiceServicer
):
    def __init__(self, temporal_client: Client):
        repository = NoteRepository(session_factory=async_session)
        self.get_note_use_case = GetNoteUseCase(repository)
        self.get_notes_by_user_id_use_case = GetNotesByUserIdUseCase(repository)
        self.create_note_use_case = CreateNoteUseCase(repository)
        self.update_note_use_case = UpdateNoteUseCase(repository)
        self.delete_note_use_case = DeleteNoteUseCase(repository)
        self.temporal_client = temporal_client

    def _tag_to_proto(self, tag) -> note_pb2.Tag:
        return note_pb2.Tag(
            id=str(tag.id),
            title=tag.title or "",
            color=tag.color or "",
            user_id=str(tag.user_id)
        )

    async def _file_to_proto(self, file) -> note_pb2.File:
        return note_pb2.File(
            id=str(file.id),
            name=file.name or "",
            url= await s3_service.generate_presigned_url(file.key),
            extension=file.extension or "",
            mime_type=file.mime_type or "",
            size=file.size or 0
        )

    async def _note_to_proto(self, note):
        if note is None:
            return None

        note_message = note_pb2.Note(
            id=str(note.id),
            title=note.title or "",
            content=note.content or "",
            user_id=str(note.user_id),
            created_at=note.created_at,
            updated_at=note.updated_at
        )

        if hasattr(note, 'tags') and note.tags:
            for tag in note.tags:
                note_message.tags.append(self._tag_to_proto(tag))

            # Добавляем файлы (конвертируем модели в proto)
        if hasattr(note, 'files') and note.files:
            for file in note.files:
                note_message.files.append(await self._file_to_proto(file))

        return note_message

    async def GetNote(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return note_pb2.GetNoteResponse()

        note = await self.get_note_use_case.execute(
            user_id=str(user_id),
            note_id=str(request.note_id)
        )

        if note is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Note not found"
            )
            return note_pb2.GetNoteResponse()

        return note_pb2.GetNoteResponse(note=await self._note_to_proto(note))


    async def GetUserNotes(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return note_pb2.GetUserNotesResponse()

        notes = await self.get_notes_by_user_id_use_case.execute(
            user_id=str(user_id)
        )

        proto_notes = [await self._note_to_proto(note) for note in notes]

        return note_pb2.GetUserNotesResponse(notes=proto_notes)


    async def CreateNote(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)
        if user_id is None:
            return note_pb2.CreateNoteResponse()

        note_data = NoteCreate(
            title=request.title,
            content=request.content,
            tags=list(request.tags),
            user_id=user_id
        )

        note_id = await self.create_note_use_case.execute(
            user_id=str(user_id),
            data=note_data
        )

        token = await grpc_auth_service.extract_token(context)

        files_payload = []

        await self.temporal_client.start_workflow(
            SaveNoteWorkflow.run,
            id=f"note-workflow-{note_id}",
            task_queue="content-task-queue",
            args=[note_id, note_data.content, files_payload, token, "grpc"]
        )

        return note_pb2.CreateNoteResponse(note_id=str(note_id))

    async def UpdateNote(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return note_pb2.UpdateNoteResponse()

        note_data = NoteUpdate()

        if request.HasField('title'):
            note_data.title = request.title
        if request.HasField('content'):
            note_data.content = request.content
        if request.tags:
            note_data.tags = list(request.tags)

        updated_note_id = await self.update_note_use_case.execute(
            user_id=str(user_id),
            note_id=str(request.note_id),
            data=note_data
        )

        if updated_note_id is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Note not found"
            )
            return note_pb2.UpdateNoteResponse()

        return note_pb2.UpdateNoteResponse(note_id=str(updated_note_id))

    async def DeleteNote(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return note_pb2.DeleteNoteResponse(success=False)

        deleted = await self.delete_note_use_case.execute(
            user_id=str(user_id),
            note_id=str(request.note_id)
        )

        if not deleted:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Note not found"
            )
            return note_pb2.DeleteNoteResponse(success=False)

        return note_pb2.DeleteNoteResponse(success=True)