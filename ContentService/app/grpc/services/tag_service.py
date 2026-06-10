import grpc

from app.db import async_session
from app.grpc.generated.tag import tag_pb2, tag_pb2_grpc
from app.grpc.grpc_auth import grpc_auth_service
from app.repositories.tag_repository import TagRepository
from app.schemas.tag_schemas import TagCreate, TagUpdate
from app.use_case.tags.create_tag import CreateTagUseCase
from app.use_case.tags.delete_tag import DeleteTagUseCase
from app.use_case.tags.get_tag import GetTagUseCase
from app.use_case.tags.get_tags_by_user_id import GetTagsByUserIdUseCase
from app.use_case.tags.update_tag import UpdateTagUseCase


class TagGrpcService(
    tag_pb2_grpc.TagServiceServicer
):
    def __init__(self):
        repository = TagRepository(session_factory=async_session)
        self.get_tag_use_case = GetTagUseCase(repository)
        self.get_tags_by_user_id_use_case = GetTagsByUserIdUseCase(repository)
        self.create_tag_use_case = CreateTagUseCase(repository)
        self.update_tag_use_case = UpdateTagUseCase(repository)
        self.delete_tag_use_case = DeleteTagUseCase(repository)

    def _tag_to_proto(self, tag) -> tag_pb2.Tag:
        return tag_pb2.Tag(
            id=str(tag.id),
            title=tag.title or "",
            color=tag.color or "",
            user_id=str(tag.user_id),
        )

    async def GetTag(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return tag_pb2.GetTagResponse()

        tag = await self.get_tag_use_case.execute(
            user_id=str(user_id),
            tag_id=str(request.tag_id)
        )

        if tag is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found"
            )
            return tag_pb2.GetTagResponse()

        return tag_pb2.GetTagResponse(tag=self._tag_to_proto(tag))

    async def GetUserTags(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return tag_pb2.GetUserTagsResponse()

        tags = await self.get_tags_by_user_id_use_case.execute(user_id=str(user_id))

        proto_tags = [self._tag_to_proto(tag) for tag in tags]

        return tag_pb2.GetUserTagsResponse(tags=proto_tags)

    async def CreateTag(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return tag_pb2.CreateTagResponse()

        tag_data = TagCreate(
            title=request.title,
            color=request.color,
            user_id=user_id
        )

        tag = await self.create_tag_use_case.execute(
            user_id=str(user_id),
            data=tag_data
        )

        return tag_pb2.CreateTagResponse(tag_id=str(tag.id))

    async def UpdateTag(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return tag_pb2.UpdateTagResponse()

        tag_data = TagUpdate()

        if request.HasField('title'):
            tag_data.title = request.title
        if request.HasField('color'):
            tag_data.color = request.color

        updated_tag = await self.update_tag_use_case.execute(
            user_id=str(user_id),
            tag_id=str(request.tag_id),
            data=tag_data
        )

        if updated_tag is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found"
            )
            return tag_pb2.UpdateTagResponse()

        return tag_pb2.UpdateTagResponse(tag_id=str(updated_tag.id))

    async def DeleteTag(self, request, context):
        user_id = await grpc_auth_service.get_current_user_id(context)

        if user_id is None:
            return tag_pb2.DeleteTagResponse(success=False)

        deleted = await self.delete_tag_use_case.execute(
            user_id=str(user_id),
            tag_id=str(request.tag_id)
        )

        if not deleted:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found"
            )
            return tag_pb2.DeleteTagResponse(success=False)

        return tag_pb2.DeleteTagResponse(success=True)