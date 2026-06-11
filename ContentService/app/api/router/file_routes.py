from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi import Depends
from temporalio.client import Client

from app.api.dependencies import get_upload_file_use_case, get_url_file_use_case, get_delete_file_use_case, \
    get_temporal_client, get_note_use_case
from app.auth import get_current_user_id, keycloak_auth, extract_token
from app.use_case.files.delete_file import DeleteFileUseCase
from app.use_case.files.get_url_file import GetUrlFileUseCase
from app.use_case.files.upload_file import UploadFileUseCase
from app.use_case.notes.get_note import GetNoteUseCase

from app.utils.workflows import SaveNoteWorkflow

router = APIRouter(prefix="/files",
                   tags=["files"],
                   dependencies=[Depends(keycloak_auth)])


@router.post("/{note_id}", response_model=dict, status_code=201)
async def upload_file(
        request: Request,
        note_id: str,
        file: UploadFile = File(...),
        upload_use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
        url_use_case: GetUrlFileUseCase = Depends(get_url_file_use_case),
        note_use_case: GetNoteUseCase = Depends(get_note_use_case),
        temporal_client: Client = Depends(get_temporal_client)
):
    user_id = get_current_user_id(request)
    token = extract_token(request)

    uploaded_file = await upload_use_case.execute(
        note_id=note_id,
        file=file,
        user_id=user_id,
    )

    file_id = uploaded_file.id

    if not file_id:
        raise HTTPException(status_code=500, detail="Failed to parse uploaded file ID")

    file_url = await url_use_case.execute(file_id=file_id, user_id=user_id)

    files_payload = [
        {
            "fid": str(file_id),
            "file_url": file_url
        }
    ]

    note = await note_use_case.execute(user_id=user_id, note_id=note_id)
    await temporal_client.start_workflow(
        "SaveNoteWorkflow",
        args=[note_id, note.content, files_payload, token, "grpc"],
        id=f"note-workflow-{note_id}-{file_id}",
        task_queue="content-task-queue"
    )

    return {
        "data": uploaded_file
    }

@router.delete("/{file_id}", status_code=204)
async def delete_file(
    request: Request,
    file_id: str,
    use_case: DeleteFileUseCase = Depends(get_delete_file_use_case),
):
    user_id = get_current_user_id(request)
    result = await use_case.execute(file_id=file_id, user_id=user_id)
    if not result:
        raise HTTPException(
            status_code=500,
            detail="File not deleted"
        )


@router.get("/get_url/{file_id}", response_model=dict, status_code=200)
async def get_url(
    request: Request,
    file_id: str,
    use_case: GetUrlFileUseCase = Depends(get_url_file_use_case),
):
    user_id = get_current_user_id(request)
    result = await use_case.execute(file_id=file_id, user_id=user_id)
    return {
        "url": result
    }
