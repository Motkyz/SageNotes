package ru.sagenotes.notificationservice.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import ru.sagenotes.notificationservice.domain.model.NotificationStatus

@Serializable
data class MongoNotificationDocument(
    @SerialName("_id") val eventId: String,
    @SerialName("version") val version: String,
    @SerialName("event_type") val eventType: String,
    @SerialName("author_id") val authorId: String,
    @SerialName("user_id") val userId: String,
    @SerialName("entity_id") val entityId: String,
    @SerialName("entity_type") val entityType: String,
    @SerialName("status") val status: NotificationStatus,
    @SerialName("created_at") val createdAt: String,
    @SerialName("meta") val meta: MongoNotificationMeta,
    @SerialName("payload") val payload: String
)
