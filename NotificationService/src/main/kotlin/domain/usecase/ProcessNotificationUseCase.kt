package ru.sagenotes.notificationservice.domain.usecase

import ru.sagenotes.notificationservice.data.utils.ConnectionManager
import ru.sagenotes.notificationservice.domain.model.NotificationEnvelope
import ru.sagenotes.notificationservice.domain.repository.NotificationRepository

interface ProcessNotificationUseCase {
    suspend operator fun invoke(envelope: NotificationEnvelope)
}

class ProcessNotificationUseCaseImpl(
    private val repository: NotificationRepository,
    private val connectionManager: ConnectionManager
) : ProcessNotificationUseCase {
    override suspend fun invoke(envelope: NotificationEnvelope) {
        val savedEnvelope = runCatching {
            repository.saveIfAbsent(envelope)
        }.getOrNull() ?: return

        val isDelivered = connectionManager.send(savedEnvelope.userId, savedEnvelope)

        if (isDelivered) {
            repository.markAsDeleted(savedEnvelope.eventId)
        }
    }
}