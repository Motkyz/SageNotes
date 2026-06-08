package ru.sagenotes.searchservice.data.di

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
import redis.clients.jedis.DefaultJedisClientConfig
import redis.clients.jedis.HostAndPort
import redis.clients.jedis.RedisClient
import ru.sagenotes.searchservice.data.config.ElasticsearchConfig
import ru.sagenotes.searchservice.data.config.JwtConfig
import ru.sagenotes.searchservice.data.config.QdrantConfig
import ru.sagenotes.searchservice.data.config.RedisConfig
import ru.sagenotes.searchservice.data.repository.CachedSearchRepositoryImpl
import ru.sagenotes.searchservice.data.repository.SearchRepositoryImpl
import ru.sagenotes.searchservice.data.service.ElasticsearchService
import ru.sagenotes.searchservice.data.service.ElasticsearchServiceImpl
import ru.sagenotes.searchservice.data.service.QdrantService
import ru.sagenotes.searchservice.data.service.QdrantServiceImpl
import ru.sagenotes.searchservice.domain.repository.SearchRepository
import ru.sagenotes.searchservice.domain.usecase.SearchUseCase
import ru.sagenotes.searchservice.domain.usecase.SearchUseCaseImpl

val networkModule = module {
    single {
        Json {
            ignoreUnknownKeys = true
        }
    }

    single {
        HttpClient(CIO) {
            install(ContentNegotiation) {
                json(get<Json>())
            }
        }
    }
}

val configModule = module {
    single { JwtConfig.fromEnv() }
    single { ElasticsearchConfig.fromEnv() }
    single { QdrantConfig.fromEnv() }
    single { RedisConfig.fromEnv() }
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

    singleOf(::ElasticsearchServiceImpl) bind ElasticsearchService::class
    singleOf(::QdrantServiceImpl) bind QdrantService::class
}

val repositoryModule = module {
    single<RedisClient> {
        val config = get<RedisConfig>()

        val clientConfig = DefaultJedisClientConfig.builder()
            .timeoutMillis(5000)
            .apply {
                password(config.password)
            }
            .build()

        RedisClient.builder()
            .hostAndPort(HostAndPort(config.host, config.port))
            .clientConfig(clientConfig)
            .build()
    }

    singleOf(::SearchRepositoryImpl)

    single<SearchRepository> {
        CachedSearchRepositoryImpl(
            delegate = get<SearchRepositoryImpl>(),
            redisClient = get(),
            json = get()
        )
    }
}

val useCaseModule = module {
    singleOf(::SearchUseCaseImpl) bind SearchUseCase::class
}

val appModule = module {
    includes(
        networkModule,
        configModule,
        serviceModule,
        repositoryModule,
        useCaseModule
    )
}