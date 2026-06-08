package ru.sagenotes.searchservice.data.repository

import kotlinx.serialization.json.Json
import redis.clients.jedis.RedisClient
import redis.clients.jedis.params.SetParams
import ru.sagenotes.searchservice.domain.model.SearchResult
import ru.sagenotes.searchservice.domain.repository.SearchRepository

class CachedSearchRepositoryImpl(
    private val delegate: SearchRepository,
    private val redisClient: RedisClient,
    private val json: Json
) : SearchRepository {
    private val cacheTtlSeconds = 600L
    override suspend fun search(
        query: String,
        userId: String,
        limit: Int
    ): List<SearchResult> {
        val cacheKey = "search:user:$userId:q:$query:limit:$limit"

        val cachedJson = runCatching {
            redisClient.get(cacheKey)
        }.getOrNull()

        if (!cachedJson.isNullOrBlank()) {
            return runCatching {
                json.decodeFromString<List<SearchResult>>(cachedJson)
            }.getOrDefault(emptyList())
        }

        val freshResults = delegate.search(query, userId, limit)

        if (freshResults.isNotEmpty()) {
            runCatching {
                val jsonString = json.encodeToString(freshResults)

                redisClient.set(
                    cacheKey,
                    jsonString,
                    SetParams.setParams().ex(cacheTtlSeconds)
                )
            }
        }

        return freshResults
    }
}