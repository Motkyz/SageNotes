package ru.sagenotes.searchservice.presentation.plugins

import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.response.respond
import ru.sagenotes.searchservice.presentation.model.ErrorResponse

fun Application.configureStatusPagePlugin() {
    install(StatusPages) {
        exception<Exception> { call, cause ->
            val message = cause.message ?: "Unknown error"
            cause.printStackTrace()
            call.respond(HttpStatusCode.InternalServerError, ErrorResponse(message))
        }
    }
}