from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (get_note_use_case, get_notes_use_case, get_create_note_use_case,
                                  get_update_note_use_case,get_delete_note_use_case)
from app.schemas.note_schemas import NoteResponse, NoteCreate, NoteUpdate
from app.use_case.notes.create_note import CreateNoteUseCase
from app.use_case.notes.delete_note import DeleteNoteUseCase
from app.use_case.notes.get_note import GetNoteUseCase
from app.use_case.notes.get_notes import GetNotesUseCase
from app.use_case.notes.update_note import UpdateNoteUseCase

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("", response_model=list[NoteResponse])
async def get_notes(use_case: GetNotesUseCase = Depends(get_notes_use_case)):

    notes = await use_case.execute()

    return notes

@router.get("/{note_id}")
async def get_note(
    note_id: str,
    use_case: GetNoteUseCase = Depends(get_note_use_case)
):

    note = await use_case.execute(note_id)

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
    data: NoteCreate,
    use_case: CreateNoteUseCase = Depends(get_create_note_use_case)
):

    note_id = await use_case.execute(data)

    return {
        "note_id": note_id
    }

@router.put("/{note_id}", response_model=dict, status_code=200)
async def update_note(
    note_id: str,
    data: NoteUpdate,
    use_case: UpdateNoteUseCase = Depends(get_update_note_use_case)
):

    updated_note_id = await use_case.execute(note_id, data)

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
    note_id: str,
    use_case: DeleteNoteUseCase = Depends(get_delete_note_use_case)
):

    deleted = await use_case.execute(note_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )