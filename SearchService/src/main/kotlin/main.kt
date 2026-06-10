package ru.sagenotes.searchservice

import io.github.oshai.kotlinlogging.KotlinLogging
import io.grpc.ServerBuilder
import io.ktor.server.application.*
import org.koin.ktor.ext.inject
import org.koin.ktor.plugin.Koin
import ru.sagenotes.searchservice.data.di.appModule
import ru.sagenotes.searchservice.presentation.plugins.configureStatusPagePlugin
import ru.sagenotes.searchservice.presentation.route.grpc.SearchGrpcService
import ru.sagenotes.searchservice.presentation.route.grpc.interceptor.JwtAuthInterceptor
import ru.sagenotes.searchservice.presentation.route.resful.configureSearchRouting
import java.io.IOException

fun main(args: Array<String>) {
    io.ktor.server.netty.EngineMain.main(args)
}

val logger = KotlinLogging.logger {}

fun Application.module() {
    install(Koin) {
        modules(
            appModule
        )
    }

    configureSerialization()
    configureStatusPagePlugin()
    configureSecurity()
    configureSearchRouting()

    configureGrpcServer()
}

fun Application.configureGrpcServer() {
    val searchGrpcService: SearchGrpcService by inject()
    val jwtAuthInterceptor: JwtAuthInterceptor by inject()

    Thread {
        try {
            val grpcServer = ServerBuilder
                .forPort(9090)
                .maxInboundMessageSize(1 * 1024 * 1024)
                .maxInboundMetadataSize(1 * 1024 * 1024)
                .intercept(jwtAuthInterceptor)
                .addService(searchGrpcService)
                .build()
                .start()

            logger.info { "grpc server started, listening on port 9090" }

            environment.monitor.subscribe(ApplicationStopping) {
                logger.info { "grpc server stopping" }
                grpcServer.shutdown()
                grpcServer.awaitTermination()
                logger.info { "grpc server stopped" }
            }

            grpcServer.awaitTermination()
        } catch (e: IOException) {
            logger.error(e) { "grpc server failed: ${e.message}" }
            e.printStackTrace()
        }
    }.start()

    logger.info { "grpc thread started" }
}
