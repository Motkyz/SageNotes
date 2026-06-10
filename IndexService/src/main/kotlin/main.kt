package ru.sagenotes.indexservice

import io.github.oshai.kotlinlogging.KotlinLogging
import io.grpc.ServerBuilder
import io.ktor.server.application.*
import org.koin.ktor.ext.inject
import org.koin.ktor.plugin.Koin
import ru.sagenotes.indexservice.data.di.appModule
import ru.sagenotes.indexservice.presentation.plugins.configureStatusPagePlugin
import ru.sagenotes.indexservice.presentation.route.grpc.IndexGrpcService
import ru.sagenotes.indexservice.presentation.route.grpc.interceptor.JwtAuthInterceptor
import ru.sagenotes.indexservice.presentation.route.restful.configureIndexRouting
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
    configureIndexRouting()

    configureGrpcServer()
}

fun Application.configureGrpcServer() {
    val indexGrpcService: IndexGrpcService by inject()
    val jwtAuthInterceptor: JwtAuthInterceptor by inject()

    Thread {
        try {
            val grpcServer = ServerBuilder
                .forPort(9090)
                .maxInboundMessageSize(1 * 1024 * 1024)
                .maxInboundMetadataSize(1 * 1024 * 1024)
                .intercept(jwtAuthInterceptor)
                .addService(indexGrpcService)
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
