package ru.sagenotes.notificationservice.presentation.route.resfull

import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.auth.authenticate
import io.ktor.server.auth.jwt.JWTPrincipal
import io.ktor.server.auth.principal
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import io.ktor.server.websocket.webSocket
import io.ktor.websocket.CloseReason
import io.ktor.websocket.close
import org.koin.ktor.ext.inject
import ru.sagenotes.notificationservice.data.utils.ConnectionManager
import ru.sagenotes.notificationservice.domain.usecase.ProcessNotificationUseCase
import ru.sagenotes.notificationservice.presentation.mapper.toDomain
import ru.sagenotes.notificationservice.presentation.model.NotificationEnvelopePresentation

fun Application.configureNotificationRouting() {
    val connectionManager: ConnectionManager by inject()
    val processNotificationUseCase: ProcessNotificationUseCase by inject()

    routing {
        authenticate("auth-jwt") {
            webSocket("/notification/ws") {
                try {
                    val userId = call.principal<JWTPrincipal>()?.payload?.getClaim("sub")?.asString()
                        ?: run {
                            close(CloseReason(CloseReason.Codes.VIOLATED_POLICY, "Unauthorized"))
                            return@webSocket
                        }

                    connectionManager.register(userId, this)
                    try {
                        for (frame in incoming) {  }
                    } finally {
                        connectionManager.unregister(userId, this)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    close(CloseReason(CloseReason.Codes.INTERNAL_ERROR, e.message ?: "Unknown error"))
                }
            }

            post("/notification/send") {
                try {
                    val adminId = call.principal<JWTPrincipal>()?.payload?.getClaim("sub")?.asString()
                        ?: return@post call.respond(HttpStatusCode.Unauthorized)
                    val request = call.receive<NotificationEnvelopePresentation>()

                    val newEnvelope = request.copy(authorId = adminId).toDomain()

                    processNotificationUseCase(newEnvelope)
                    call.respond(HttpStatusCode.Created)
                } catch (e: Exception) {
                    e.printStackTrace()
                    call.respond(HttpStatusCode.BadRequest, e.message ?: "Unknown error")
                }
            }
        }
    }
}