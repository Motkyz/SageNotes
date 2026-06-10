from fastapi import APIRouter, Depends, HTTPException, Request
from temporalio.client import Client

from app.api.dependencies import (get_note_use_case, get_create_note_use_case,
                                  get_update_note_use_case, get_delete_note_use_case, get_notes_by_user_id_use_case,
                                  get_temporal_client)
from app.auth import keycloak_auth, get_current_user_id, extract_token
from app.schemas.note_schemas import NoteResponse, NoteCreate, NoteUpdate
from app.use_case.notes.create_note import CreateNoteUseCase
from app.use_case.notes.delete_note import DeleteNoteUseCase
from app.use_case.notes.get_note import GetNoteUseCase
from app.use_case.notes.get_notes_by_user_id import GetNotesByUserIdUseCase
from app.use_case.notes.update_note import UpdateNoteUseCase
from app.utils.workflows import SaveNoteWorkflow

router = APIRouter(prefix="/notes",
                   tags=["notes"],
                   dependencies=[Depends(keycloak_auth)])


@router.get("/user", response_model=list[NoteResponse])
async def get_notes_by_user_id(
        request: Request,
        use_case: GetNotesByUserIdUseCase = Depends(get_notes_by_user_id_use_case)):

    user_id = get_current_user_id(request)
    notes = await use_case.execute(user_id = user_id)

    return notes

@router.get("/{note_id}")
async def get_note(
    request: Request,
    note_id: str,
    use_case: GetNoteUseCase = Depends(get_note_use_case)
):

    user_id = get_current_user_id(request)
    note = await use_case.execute(user_id=user_id, note_id=note_id)

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "data": note
    }

@router.post("", response_model=dict, status_code=201)
async def create_note(
    request: Request,
    data: NoteCreate,
    use_case: CreateNoteUseCase = Depends(get_create_note_use_case),
    temporal_client: Client = Depends(get_temporal_client)
):
    user_id = get_current_user_id(request)
    note_id = await use_case.execute(user_id=user_id, data=data)
    token = extract_token(request)

    files_payload = []

    await temporal_client.start_workflow(
        SaveNoteWorkflow.run,
        id=f"note-workflow-{note_id}",
        task_queue="content-task-queue",
        args=[note_id, data.content, files_payload, token]
    )

    return {"note_id": note_id}

@router.put("/{note_id}", response_model=dict, status_code=200)
async def update_note(
    request: Request,
    note_id: str,
    data: NoteUpdate,
    use_case: UpdateNoteUseCase = Depends(get_update_note_use_case)
):
    user_id = get_current_user_id(request)
    updated_note_id = await use_case.execute(user_id=user_id, note_id=note_id, data=data)

    if updated_note_id is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "note_id": updated_note_id
    }

@router.delete("/{note_id}", status_code=204)
async def delete_note(
    request: Request,
    note_id: str,
    use_case: DeleteNoteUseCase = Depends(get_delete_note_use_case)
):

    user_id = get_current_user_id(request)
    deleted = await use_case.execute(user_id=user_id, note_id=note_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )