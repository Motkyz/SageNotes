from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (get_tag_use_case, get_tags_use_case, get_create_tag_use_case,
                                  get_update_tag_use_case, get_delete_tag_use_case)
from app.schemas.tag_schemas import TagResponse, TagCreate, TagUpdate
from app.use_case.tags.create_tag import CreateTagUseCase
from app.use_case.tags.delete_tag import DeleteTagUseCase
from app.use_case.tags.get_tag import GetTagUseCase
from app.use_case.tags.get_tags import GetTagsUseCase
from app.use_case.tags.update_tag import UpdateTagUseCase

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("", response_model=list[TagResponse])
async def get_tags(
    use_case: GetTagsUseCase = Depends(get_tags_use_case)
):
    tags = await use_case.execute()
    return tags

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    use_case: GetTagUseCase = Depends(get_tag_use_case)
):
    tag = await use_case.execute(tag_id)

    if tag is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    return tag

@router.post("", response_model=dict, status_code=201)
async def create_tag(
    data: TagCreate,
    use_case: CreateTagUseCase = Depends(get_create_tag_use_case)
):
    tag = await use_case.execute(data)
    tag_id = tag.id

    return {
        "tag_id": tag_id
    }

@router.put("/{tag_id}", response_model=dict, status_code=200)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    use_case: UpdateTagUseCase = Depends(get_update_tag_use_case)
):

    updated_tag = await use_case.execute(tag_id, data)

    if updated_tag is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    tag_id = updated_tag.id

    return {
        "tag_id": tag_id
    }

@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    use_case: DeleteTagUseCase = Depends(get_delete_tag_use_case)
):

    deleted = await use_case.execute(tag_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    return None