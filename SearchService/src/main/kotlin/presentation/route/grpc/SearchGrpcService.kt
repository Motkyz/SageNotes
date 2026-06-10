package ru.sagenotes.searchservice.presentation.route.grpc

import ru.sagenotes.searchservice.domain.model.SearchSource
import ru.sagenotes.searchservice.domain.usecase.SearchUseCase
import ru.sagenotes.searchservice.grpc.SearchRequest
import ru.sagenotes.searchservice.grpc.SearchResponse
import ru.sagenotes.searchservice.grpc.SearchResult
import ru.sagenotes.searchservice.grpc.SearchServiceGrpcKt
import ru.sagenotes.searchservice.grpc.SearchSource as GrpcSearchSource
import ru.sagenotes.searchservice.presentation.route.grpc.utils.getCurrentUserId
import ru.sagenotes.searchservice.presentation.route.grpc.utils.grpcCall

class SearchGrpcService(
    private val searchUseCase: SearchUseCase
) : SearchServiceGrpcKt.SearchServiceCoroutineImplBase() {
    override suspend fun search(request: SearchRequest): SearchResponse = grpcCall {
        val userId = getCurrentUserId()
        val limit = if (request.hasLimit()) request.limit else 10

        val results = searchUseCase(
            query = request.query,
            userId = userId,
            limit = limit
        )

        SearchResponse.newBuilder()
            .addAllResults(
                results.map { result ->
                    SearchResult.newBuilder()
                        .setNoteId(result.noteId)
                        .setText(result.text)
                        .setScore(result.score)
                        .setSource(mapToGrpcSource(result.source))
                        .build()
                }
            ).build()
    }

    private fun mapToGrpcSource(searchSource: SearchSource): GrpcSearchSource {
        return when (searchSource) {
            SearchSource.ELASTICSEARCH -> GrpcSearchSource.ELASTICSEARCH
            SearchSource.QDRANT -> GrpcSearchSource.QDRANT
            SearchSource.HYBRID -> GrpcSearchSource.HYBRID
        }
    }
}