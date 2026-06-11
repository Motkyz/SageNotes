package ru.sagenotes.notificationservice.presentation.consumer

import com.rabbitmq.client.ConnectionFactory
import com.rabbitmq.client.DeliverCallback
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import ru.sagenotes.notificationservice.domain.usecase.ProcessNotificationUseCase
import ru.sagenotes.notificationservice.presentation.mapper.toDomain
import ru.sagenotes.notificationservice.presentation.model.NotificationEnvelopePresentation
import java.nio.charset.StandardCharsets

class RabbitMqConsumer(
    private val factory: ConnectionFactory,
    private val processNotificationUseCase: ProcessNotificationUseCase
) {
    fun start() {
        val channel = factory.newConnection().createChannel()
        channel.queueDeclare("notification.queue", true, false, false, null)
        channel.basicQos(1)

        val deliverCallback = DeliverCallback { _, delivery ->
            val jsonStr = String(delivery.body, StandardCharsets.UTF_8)

            runBlocking {
                try {
                    val notificationEnvelope = Json.decodeFromString<NotificationEnvelopePresentation>(jsonStr)
                    processNotificationUseCase(notificationEnvelope.toDomain())
                    channel.basicAck(delivery.envelope.deliveryTag, false)
                } catch (e: Exception) {
                    channel.basicReject(delivery.envelope.deliveryTag, false)
                }
            }
        }

        channel.basicConsume(
            "notification.queue",
            false,
            deliverCallback
        ) { }
    }
}