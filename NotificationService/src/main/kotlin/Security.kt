package ru.sagenotes.notificationservice

import com.auth0.jwk.UrlJwkProvider
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.auth.Authentication
import io.ktor.server.auth.jwt.JWTPrincipal
import io.ktor.server.auth.jwt.jwt
import org.koin.ktor.ext.inject
import ru.sagenotes.notificationservice.data.config.JwtConfig
import java.net.URL
import kotlin.getValue

fun Application.configureSecurity() {
    val config by inject<JwtConfig>()

    install(Authentication) {
        jwt("auth-jwt") {
            realm = config.realm
            verifier(
                UrlJwkProvider(URL(config.certsUrl))
            )

            validate { credential ->
                if (credential.payload.audience.contains(config.audience)) {
                    JWTPrincipal(credential.payload)
                } else {
                    null
                }
            }
        }
    }
}