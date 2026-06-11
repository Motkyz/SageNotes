package ru.sagenotes.notificationservice.data.repository

import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import com.mongodb.kotlin.client.coroutine.MongoDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.withContext
import ru.sagenotes.notificationservice.data.config.MongoConfig
import ru.sagenotes.notificationservice.data.mapper.toDomain
import ru.sagenotes.notificationservice.data.mapper.toDto
import ru.sagenotes.notificationservice.data.model.MongoNotificationDocument
import ru.sagenotes.notificationservice.data.model.exception.CustomExceptions
import ru.sagenotes.notificationservice.domain.model.NotificationEnvelope
import ru.sagenotes.notificationservice.domain.model.NotificationStatus
import ru.sagenotes.notificationservice.domain.repository.NotificationRepository

class NotificationRepositoryImpl(
    private val database: MongoDatabase,
    private val mongoConfig: MongoConfig
) : NotificationRepository {
    private val collection =
        database.getCollection<MongoNotificationDocument>(mongoConfig.database)

    override suspend fun saveIfAbsent(envelope: NotificationEnvelope): NotificationEnvelope =
        withContext(Dispatchers.IO) {
            val document = envelope.toDto()

            val exists = collection.find(Filters.eq("_id", document.eventId)).toList().isNotEmpty()
            if (exists) throw CustomExceptions.EventExistsException("Event already existed")

            collection.insertOne(document)

            envelope
        }

    override suspend fun getUnreadNotificationsByUserId(userId: String): List<NotificationEnvelope> =
        withContext(Dispatchers.IO) {
            collection.find(
                Filters.and(
                    Filters.eq("user_id", userId),
                    Filters.eq("status", NotificationStatus.UNREAD)
                )
            ).toList().map { it.toDomain() }
        }

    override suspend fun markAsDeleted(eventId: String) {
        withContext(Dispatchers.IO) {
            collection.updateOne(
                Filters.eq("_id", eventId),
                Updates.set("status", NotificationStatus.DELIVERED)
            )
        }
    }
}