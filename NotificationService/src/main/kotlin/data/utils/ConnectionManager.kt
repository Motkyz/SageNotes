package ru.sagenotes.notificationservice.data.utils

import io.ktor.server.websocket.*
import io.ktor.websocket.Frame
import kotlinx.coroutines.channels.ClosedSendChannelException
import kotlinx.serialization.json.Json
import ru.sagenotes.notificationservice.domain.model.NotificationEnvelope
import ru.sagenotes.notificationservice.presentation.mapper.toPresentation
import java.util.concurrent.ConcurrentHashMap

interface ConnectionManager {
    fun register(userId: String, session: DefaultWebSocketServerSession)
    fun unregister(userId: String, session: DefaultWebSocketServerSession)
    suspend fun send(userId: String, envelope: NotificationEnvelope): Boolean
}

class ConnectionManagerImpl : ConnectionManager {
    private val sessions = ConcurrentHashMap<String, MutableSet<DefaultWebSocketServerSession>>()

    override fun register(userId: String, session: DefaultWebSocketServerSession) {
        sessions.computeIfAbsent(userId) { ConcurrentHashMap.newKeySet() }.add(session)
    }

    override fun unregister(userId: String, session: DefaultWebSocketServerSession) {
        sessions[userId]?.remove(session)
        if (sessions[userId].isNullOrEmpty()) sessions.remove(userId)
    }

    override suspend fun send(
        userId: String,
        envelope: NotificationEnvelope
    ): Boolean {
        val userSessions = sessions[userId] ?: return false
        if (userSessions.isEmpty()) return false

        val jsonText = Json.encodeToString(envelope.toPresentation())
        var delivered = false

        for (session in userSessions) {
            try {
                session.send(Frame.Text(jsonText))
                delivered = true
            } catch (e: ClosedSendChannelException) {  }
        }

        return delivered
    }
}