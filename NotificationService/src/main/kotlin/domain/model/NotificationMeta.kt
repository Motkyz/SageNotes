package ru.sagenotes.notificationservice.domain.model

data class NotificationMeta(
    val title: String,
    val description: String,
    val level: NotificationLevel
)
