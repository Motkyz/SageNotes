package ru.sagenotes.notificationservice.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import ru.sagenotes.notificationservice.domain.model.NotificationLevel

@Serializable
data class MongoNotificationMeta(
    @SerialName("title") val title: String,
    @SerialName("description") val description: String,
    @SerialName("level") val level: NotificationLevel
)
