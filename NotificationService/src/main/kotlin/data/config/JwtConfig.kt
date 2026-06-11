package ru.sagenotes.notificationservice.data.config

data class JwtConfig(
    private val issuer: String,
    private val certs: String,
    private val scheme: String = "http",
    val audience: String,
    val realm: String
) {
    val certsUrl = "$scheme://$issuer/$certs"

    companion object {
        fun fromEnv() = JwtConfig(
            issuer = requireNotNull(System.getenv("KEYCLOAK_ISSUER")) { "KEYCLOAK_ISSUER is required" },
            certs = requireNotNull(System.getenv("KEYCLOAK_CERTS")) { "KEYCLOAK_CERTS is required" },
            audience = requireNotNull(System.getenv("KEYCLOAK_AUDIENCE")) { "KEYCLOAK_AUDIENCE is required" },
            realm = requireNotNull(System.getenv("REALM")) { "REALM is required" }
        )
    }
}