package ru.sagenotes.notificationservice.presentation.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement
import ru.sagenotes.notificationservice.domain.model.NotificationStatus

@Serializable
data class NotificationEnvelopePresentation(
    @SerialName("version") val version: String,
    @SerialName("event_type") val eventType: String,
    @SerialName("author_id") val authorId: String = "",
    @SerialName("user_id") val userId: String,
    @SerialName("entity_id") val entityId: String,
    @SerialName("entity_type") val entityType: String,
    @SerialName("status") val status: NotificationStatus = NotificationStatus.UNREAD,
    @SerialName("created_at") val createdAt: String,
    @SerialName("meta") val meta: NotificationMetaPresentation,
    @SerialName("payload") val payload: JsonElement
)