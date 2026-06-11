package ru.sagenotes.notificationservice.domain.repository

import ru.sagenotes.notificationservice.domain.model.NotificationEnvelope

interface NotificationRepository {
    suspend fun saveIfAbsent(envelope: NotificationEnvelope): NotificationEnvelope
    suspend fun getUnreadNotificationsByUserId(userId: String): List<NotificationEnvelope>
    suspend fun markAsDeleted(eventId: String)
}