package ru.sagenotes.notificationservice.presentation.route.grpc

import io.grpc.Status
import io.grpc.StatusException
import kotlinx.serialization.json.Json
import ru.sagenotes.notificationservice.domain.model.NotificationEnvelope
import ru.sagenotes.notificationservice.domain.model.NotificationLevel
import ru.sagenotes.notificationservice.domain.model.NotificationMeta
import ru.sagenotes.notificationservice.domain.model.NotificationStatus
import ru.sagenotes.notificationservice.domain.usecase.ProcessNotificationUseCase
import ru.sagenotes.notificationservice.grpc.NotificationServiceGrpcKt
import ru.sagenotes.notificationservice.grpc.SendNotificationRequest
import ru.sagenotes.notificationservice.grpc.SendNotificationResponse
import ru.sagenotes.notificationservice.grpc.NotificationLevel as GrpcNotificationLevel
import ru.sagenotes.notificationservice.grpc.NotificationStatus as GrpcNotificationStatus
import ru.sagenotes.notificationservice.presentation.route.grpc.utils.getCurrentUserId
import ru.sagenotes.notificationservice.presentation.route.grpc.utils.grpcCall

class NotificationGrpcService(
    private val processNotificationUseCase: ProcessNotificationUseCase
) : NotificationServiceGrpcKt.NotificationServiceCoroutineImplBase() {
    override suspend fun sendNotification(request: SendNotificationRequest): SendNotificationResponse = grpcCall {
        if (request.userId.isBlank()) {
            throw StatusException(Status.INVALID_ARGUMENT.withDescription("userId is required"))
        }
        if (request.version.isBlank()) {
            throw StatusException(Status.INVALID_ARGUMENT.withDescription("version is required"))
        }

        val authorId = getCurrentUserId()

        val payload = Json.parseToJsonElement(request.payload)

        val envelope = NotificationEnvelope(
            version = request.version,
            eventType = request.eventType,
            authorId = authorId,
            userId = request.userId,
            entityId = request.entityId,
            entityType = request.entityType,
            status = request.status.toDomain(),
            createdAt = request.createdAt,
            meta = NotificationMeta(
                title = request.meta.title,
                description = request.meta.description,
                level = request.meta.level.toDomain()
            ),
            payload = payload
        )

        processNotificationUseCase(envelope)

        SendNotificationResponse.newBuilder()
            .setSuccess(true)
            .setMessage("Notification sent successfully")
            .build()
    }

    private fun GrpcNotificationLevel.toDomain(): NotificationLevel =
        when (this) {
            GrpcNotificationLevel.INFO -> NotificationLevel.INFO
            GrpcNotificationLevel.WARNING -> NotificationLevel.WARNING
            GrpcNotificationLevel.ERROR -> NotificationLevel.ERROR
            GrpcNotificationLevel.CRITICAL -> NotificationLevel.CRITICAL
            GrpcNotificationLevel.UNRECOGNIZED -> NotificationLevel.INFO
        }

    private fun GrpcNotificationStatus.toDomain(): NotificationStatus =
        when (this) {
            GrpcNotificationStatus.UNREAD -> NotificationStatus.UNREAD
            GrpcNotificationStatus.DELIVERED -> NotificationStatus.DELIVERED
            GrpcNotificationStatus.READ -> NotificationStatus.READ
            GrpcNotificationStatus.UNRECOGNIZED -> NotificationStatus.UNREAD
        }
}