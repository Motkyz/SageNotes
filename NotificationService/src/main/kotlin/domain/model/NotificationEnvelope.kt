package ru.sagenotes.notificationservice.domain.model

import kotlinx.serialization.json.JsonElement
import java.nio.charset.StandardCharsets
import java.util.*

data class NotificationEnvelope(
    val version: String,
    val eventType: String,
    val authorId: String,
    val userId: String,
    val entityId: String,
    val entityType: String,
    val eventId: String = UUID.nameUUIDFromBytes(
        "$version:$entityId:$eventType:$authorId:$userId"
            .toByteArray(StandardCharsets.UTF_8)
    ).toString(),
    val status: NotificationStatus = NotificationStatus.UNREAD,
    val createdAt: String,
    val meta: NotificationMeta,
    val payload: JsonElement
)
