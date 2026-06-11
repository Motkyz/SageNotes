package ru.sagenotes.notificationservice.data.di

import com.mongodb.kotlin.client.coroutine.MongoClient
import com.rabbitmq.client.ConnectionFactory
import org.koin.core.module.dsl.singleOf
import org.koin.dsl.bind
import org.koin.dsl.module
import ru.sagenotes.notificationservice.data.config.JwtConfig
import ru.sagenotes.notificationservice.data.config.MongoConfig
import ru.sagenotes.notificationservice.data.config.RabbitConfig
import ru.sagenotes.notificationservice.data.repository.NotificationRepositoryImpl
import ru.sagenotes.notificationservice.data.utils.ConnectionManager
import ru.sagenotes.notificationservice.data.utils.ConnectionManagerImpl
import ru.sagenotes.notificationservice.domain.repository.NotificationRepository
import ru.sagenotes.notificationservice.domain.usecase.ProcessNotificationUseCase
import ru.sagenotes.notificationservice.domain.usecase.ProcessNotificationUseCaseImpl
import ru.sagenotes.notificationservice.presentation.consumer.RabbitMqConsumer
import ru.sagenotes.notificationservice.presentation.route.grpc.NotificationGrpcService
import ru.sagenotes.notificationservice.presentation.route.grpc.interceptor.JwtAuthInterceptor

val configModule = module {
    single { JwtConfig.fromEnv() }
    single { MongoConfig.fromEnv() }
    single { RabbitConfig.fromEnv() }
}
val networkModule = module {
    single {
        val config = get<MongoConfig>()
        MongoClient.create(config.connectionUri)
    }

    single {
        val config = get<MongoConfig>()

        val mongoDatabase = config.database
        get<MongoClient>().getDatabase(mongoDatabase)
    }

    single {
        val config = get<RabbitConfig>()

        ConnectionFactory().apply {
            host = config.host
            port = config.port
            username = config.username
            password = config.password
            isAutomaticRecoveryEnabled = true
        }
    }

    singleOf(::ConnectionManagerImpl) bind ConnectionManager::class
}

val repositoryModule = module {
    singleOf(::NotificationRepositoryImpl) bind NotificationRepository::class
}

val useCaseModule = module {
    singleOf(::ProcessNotificationUseCaseImpl) bind ProcessNotificationUseCase::class
}

val consumerModule = module {
    singleOf(::RabbitMqConsumer)
}

val grpcModule = module {
    singleOf(::JwtAuthInterceptor)
    singleOf(::NotificationGrpcService)
}

val appModule = module {
    includes(
        networkModule,
        configModule,
        repositoryModule,
        useCaseModule,
        consumerModule,
        grpcModule
    )
}