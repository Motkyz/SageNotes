plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(ktorLibs.plugins.ktor)
    alias(libs.plugins.kotlin.serialization)
}

group = "ru.sagenotes.searchservice"
version = "1.0.0-SNAPSHOT"

application {
    mainClass = "io.ktor.server.netty.EngineMain"
}

kotlin {
    jvmToolchain(21)
}
dependencies {
    implementation(ktorLibs.serialization.kotlinx.json)
    implementation(ktorLibs.server.config.yaml)
    implementation(ktorLibs.server.contentNegotiation)
    implementation(ktorLibs.server.core)
    implementation(ktorLibs.server.netty)
    implementation(libs.logback.classic)
    implementation(libs.ucasoft.ktorSimpleCache)
    implementation(libs.ucasoft.ktorSimpleRedisCache)

    implementation(ktorLibs.client.core)
    implementation(ktorLibs.client.cio)
    implementation(ktorLibs.client.contentNegotiation)

    implementation(ktorLibs.server.statusPages)

    implementation(ktorLibs.server.auth)
    implementation(ktorLibs.server.auth.jwt)

    implementation("redis.clients:jedis:7.5.2")

    val koin = "4.1.1"
    implementation("io.insert-koin:koin-ktor:$koin")

    implementation("co.elastic.clients:elasticsearch-java:8.11.1")
    implementation("org.elasticsearch.client:elasticsearch-rest-client:8.11.1")

    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0")

    testImplementation(kotlin("test"))
    testImplementation(ktorLibs.server.testHost)
}

ktor {
    fatJar {
        archiveFileName.set("app-fat.jar")
    }
}
