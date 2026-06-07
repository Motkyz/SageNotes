from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import Depends

from app.api.dependencies import get_upload_file_use_case, get_url_file_use_case, get_delete_file_use_case
from app.use_case.files.delete_file import DeleteFileUseCase
from app.use_case.files.get_url_file import GetUrlFileUseCase
from app.use_case.files.upload_file import UploadFileUseCase

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/{note_id}", response_model=dict, status_code=201)
async def upload_file(
    note_id: str,
    file: UploadFile = File(...),
    use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
):
    uploaded_file = await use_case.execute(
        note_id=note_id,
        file=file,
    )

    return {
        "data": uploaded_file
    }

@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: str,
    use_case: DeleteFileUseCase = Depends(get_delete_file_use_case),
):
    result = await use_case.execute(file_id=file_id)
    if not result:
        raise HTTPException(
            status_code=500,
            detail="File not deleted"
        )


@router.get("/get_url/{file_id}", response_model=dict, status_code=200)
async def get_url(
    file_id: str,
    use_case: GetUrlFileUseCase = Depends(get_url_file_use_case),
):
    result = await use_case.execute(file_id=file_id)
    return {
        "url": result
    }
