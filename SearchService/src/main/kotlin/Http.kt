package ru.sagenotes.searchservice

import io.ktor.server.application.*
import com.ucasoft.ktor.simpleCache.SimpleCache
import com.ucasoft.ktor.simpleRedisCache.*
import kotlin.time.Duration.Companion.seconds

fun Application.configureHttp() {
    install(SimpleCache) {
        redisCache {
            invalidateAt = 10.seconds
            host = "localhost"
            port = 6379
        }
    }
}
