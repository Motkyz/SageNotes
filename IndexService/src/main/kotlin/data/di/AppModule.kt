package ru.sagenotes.indexservice.data.di

import co.elastic.clients.elasticsearch.ElasticsearchClient
import co.elastic.clients.json.jackson.JacksonJsonpMapper
import co.elastic.clients.transport.rest_client.RestClientTransport
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import org.apache.http.HttpHost
import org.apache.http.auth.AuthScope
import org.apache.http.auth.UsernamePasswordCredentials
import org.apache.http.impl.client.BasicCredentialsProvider
import org.elasticsearch.client.RestClient
import org.koin.core.module.dsl.singleOf
import org.koin.dsl.bind
import org.koin.dsl.module
import ru.sagenotes.indexservice.data.config.ElasticsearchConfig
import ru.sagenotes.indexservice.data.config.JwtConfig
import ru.sagenotes.indexservice.data.config.QdrantConfig
import ru.sagenotes.indexservice.data.repository.IndexRepositoryImpl
import ru.sagenotes.indexservice.data.service.ElasticsearchService
import ru.sagenotes.indexservice.data.service.ElasticsearchServiceImpl
import ru.sagenotes.indexservice.data.service.EmbeddingService
import ru.sagenotes.indexservice.data.service.EmbeddingServiceImpl
import ru.sagenotes.indexservice.data.utils.Chunker
import ru.sagenotes.indexservice.data.utils.ChunkerImpl
import ru.sagenotes.indexservice.domain.repository.IndexRepository
import ru.sagenotes.indexservice.domain.usecase.IndexUseCase
import ru.sagenotes.indexservice.domain.usecase.IndexUseCaseImpl
import ru.sagenotes.indexservice.presentation.route.grpc.IndexGrpcService
import ru.sagenotes.indexservice.presentation.route.grpc.interceptor.JwtAuthInterceptor

val networkModule = module {
    single {
        HttpClient(CIO) {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }
    }
}

val configModule = module {
    single { JwtConfig.fromEnv() }
    single { ElasticsearchConfig.fromEnv() }
    single { QdrantConfig.fromEnv() }
}

val serviceModule = module {
    single {
        val config = get<ElasticsearchConfig>()

        val credentials = UsernamePasswordCredentials(config.username, config.password)
        val credentialsProvider = BasicCredentialsProvider().apply {
            setCredentials(AuthScope.ANY, credentials)
        }

        val restClient = RestClient.builder(HttpHost(
            config.host,
            config.port,
            config.scheme
        ))
            .setHttpClientConfigCallback { httpAsyncClientBuilder ->
                httpAsyncClientBuilder.setDefaultCredentialsProvider(credentialsProvider)
            }
            .build()

        val transport = RestClientTransport(restClient, JacksonJsonpMapper())
        ElasticsearchClient(transport)
    }

    singleOf(::EmbeddingServiceImpl) bind EmbeddingService::class
    singleOf(::ElasticsearchServiceImpl) bind ElasticsearchService::class
}

val repositoryModule = module {
    singleOf(::ChunkerImpl) bind Chunker::class
    singleOf(::IndexRepositoryImpl) bind IndexRepository::class
}

val useCaseModule = module {
    singleOf(::IndexUseCaseImpl) bind IndexUseCase::class
}

val grpcModule = module {
    singleOf(::JwtAuthInterceptor)
    singleOf(::IndexGrpcService)
}

val appModule = module {
    includes(
        networkModule,
        configModule,
        serviceModule,
        repositoryModule,
        useCaseModule,
        grpcModule,
    )
}