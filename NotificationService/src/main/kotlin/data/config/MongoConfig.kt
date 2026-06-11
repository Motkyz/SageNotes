package ru.sagenotes.notificationservice.data.config

data class MongoConfig(
    private val mongoHost: String,
    private val mongoPort: Int = 27017,
    private val mongoUsername: String,
    private val mongoPassword: String,
    val database: String
) {
    val connectionUri = "mongodb://$mongoUsername:$mongoPassword@$mongoHost:$mongoPort/notifications?authSource=admin"

    companion object {
        fun fromEnv() = MongoConfig(
            mongoHost = requireNotNull(System.getenv("MONGO_HOST")) { "MONGO_HOST is required" },
            mongoUsername = requireNotNull(System.getenv("MONGO_USERNAME")) { "MONGO_USERNAME is required" },
            mongoPassword = requireNotNull(System.getenv("MONGO_PASSWORD")) { "MONGO_PASSWORD is required" },
            database = requireNotNull(System.getenv("MONGO_DATABASE")) { "MONGO_DATABASE is required" }
        )
    }
}