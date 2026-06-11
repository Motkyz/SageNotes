package ru.sagenotes.notificationservice.data.config

data class RabbitConfig(
    val host: String,
    val port: Int = 5672,
    val username: String,
    val password: String,
) {
    companion object {
        fun fromEnv() = RabbitConfig(
            host = requireNotNull(System.getenv("RABBITMQ_HOST")) { "RABBITMQ_HOST is required" },
            username = requireNotNull(System.getenv("RABBITMQ_USERNAME")) { "RABBITMQ_USERNAME is required" },
            password = requireNotNull(System.getenv("RABBITMQ_PASSWORD")) { "RABBITMQ_PASSWORD is required" }
        )
    }
}
