package ru.sagenotes.searchservice.presentation.route.resful

import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.auth.authenticate
import io.ktor.server.auth.jwt.JWTPrincipal
import io.ktor.server.auth.principal
import io.ktor.server.response.respond
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import org.koin.ktor.ext.inject
import ru.sagenotes.searchservice.domain.usecase.SearchUseCase
import ru.sagenotes.searchservice.presentation.mapper.toPresentation

fun Application.configureSearchRouting() {
    val searchUseCase: SearchUseCase by inject()
    routing {
        authenticate("auth-jwt") {
            post("/search") {
                val query = call.request.queryParameters["q"]
                    ?: return@post call.respond(HttpStatusCode.BadRequest, "Query parameter 'q' is required")
                val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 10

                val userId = call.principal<JWTPrincipal>()?.payload?.getClaim("sub")?.asString()
                    ?: return@post call.respond(HttpStatusCode.Unauthorized)

                val response = searchUseCase(query, userId, limit).map { it.toPresentation() }

                call.respond(HttpStatusCode.OK, response)
            }
        }
    }
}