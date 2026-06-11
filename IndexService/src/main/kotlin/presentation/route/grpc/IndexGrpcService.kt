package ru.sagenotes.indexservice.presentation.route.grpc

import ru.sagenotes.indexservice.domain.usecase.IndexUseCase
import ru.sagenotes.indexservice.grpc.IndexRequest
import ru.sagenotes.indexservice.grpc.IndexResponse
import ru.sagenotes.indexservice.grpc.IndexServiceGrpcKt
import ru.sagenotes.indexservice.presentation.route.grpc.utils.getCurrentUserId
import ru.sagenotes.indexservice.presentation.route.grpc.utils.grpcCall

class IndexGrpcService(
    private val indexUseCase: IndexUseCase
) : IndexServiceGrpcKt.IndexServiceCoroutineImplBase() {
    override suspend fun index(request: IndexRequest): IndexResponse = grpcCall {
        val userId = getCurrentUserId()

        indexUseCase(
            noteId = request.noteId,
            text = request.text,
            userId = userId
        )

        IndexResponse.newBuilder()
            .setSuccess(true)
            .setMessage("Text indexed successfully")
            .build()
    }
}