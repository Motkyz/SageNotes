package ru.sagenotes.searchservice.data.config

data class RedisConfig(
    val host: String,
    val port: Int = 6379,
    val password: String,
) {
    companion object {
        fun fromEnv() = RedisConfig(
            host = requireNotNull(System.getenv("REDIS_HOST")) { "REDIS_HOST id required" },
            password = requireNotNull(System.getenv("REDIS_PASSWORD")) { "REDIS_PASSWORD is required" }
        )
    }
}