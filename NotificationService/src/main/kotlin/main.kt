package ru.sagenotes.notificationservice

import io.github.oshai.kotlinlogging.KotlinLogging
import io.grpc.ServerBuilder
import io.ktor.server.application.*
import io.ktor.server.websocket.*
import org.koin.ktor.ext.inject
import org.koin.ktor.plugin.Koin
import ru.sagenotes.notificationservice.data.di.appModule
import ru.sagenotes.notificationservice.presentation.consumer.RabbitMqConsumer
import ru.sagenotes.notificationservice.presentation.route.grpc.NotificationGrpcService
import ru.sagenotes.notificationservice.presentation.route.grpc.interceptor.JwtAuthInterceptor
import ru.sagenotes.notificationservice.presentation.route.resfull.configureNotificationRouting
import java.io.IOException
import kotlin.time.Duration.Companion.seconds

fun main(args: Array<String>) {
    io.ktor.server.netty.EngineMain.main(args)
}

val logger = KotlinLogging.logger {}

fun Application.module() {
    install(WebSockets) {
        pingPeriod = 30.seconds
        timeout = 15.seconds
    }

    install(Koin) {
        modules(
            appModule
        )
    }

    configureSerialization()
    configureSecurity()

    configureNotificationRouting()

    configureGrpcServer()

    val rabbitMqConsumer: RabbitMqConsumer by inject()
    rabbitMqConsumer.start()
}

fun Application.configureGrpcServer() {
    val notificationGrpcService: NotificationGrpcService by inject()
    val jwtAuthInterceptor: JwtAuthInterceptor by inject()

    Thread {
        try {
            val grpcServer = ServerBuilder
                .forPort(9090)
                .maxInboundMessageSize(1 * 1024 * 1024)
                .maxInboundMetadataSize(1 * 1024 * 1024)
                .intercept(jwtAuthInterceptor)
                .addService(notificationGrpcService)
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
