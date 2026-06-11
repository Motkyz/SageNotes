plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(ktorLibs.plugins.ktor)
    alias(libs.plugins.kotlin.serialization)
    id("com.google.protobuf") version "0.9.4"
}

group = "ru.sagenotes.indexservice"
version = "1.0.0-SNAPSHOT"

application {
    mainClass = "io.ktor.server.netty.EngineMain"
}

kotlin {
    jvmToolchain(21)
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.1"
    }

    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.59.0"
        }

        create("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar"
        }
    }

    generateProtoTasks {
        all().forEach {
            it.plugins {
                create("grpc")
                create("grpckt")
            }
        }
    }
}

sourceSets {
    main {
        proto {
            srcDir("src/main/kotlin/presentation/proto")
        }
        kotlin {
            srcDirs(
                "src/main/kotlin",
                "build/generated/source/proto/main/kotlin",
                "build/generated/source/proto/main/grpc",
                "build/generated/source/proto/main/grpckt"
            )
        }
    }
}

dependencies {
    implementation(ktorLibs.serialization.kotlinx.json)
    implementation(ktorLibs.server.config.yaml)
    implementation(ktorLibs.server.contentNegotiation)
    implementation(ktorLibs.server.core)
    implementation(ktorLibs.server.netty)
    implementation(libs.logback.classic)
    implementation(ktorLibs.client.cio)
    implementation(ktorLibs.client.contentNegotiation)

    implementation(ktorLibs.server.statusPages)

    implementation(ktorLibs.server.auth)
    implementation(ktorLibs.server.auth.jwt)

    implementation("io.github.oshai:kotlin-logging-jvm:8.0.01")

    implementation("com.microsoft.onnxruntime:onnxruntime:1.16.3")
    implementation("co.elastic.clients:elasticsearch-java:8.11.0")

    implementation("io.qdrant:client:1.7.0")

    val koin = "4.1.1"
    implementation("io.insert-koin:koin-ktor:$koin")

    implementation("io.grpc:grpc-netty:1.59.0")
    implementation("io.grpc:grpc-protobuf:1.59.0")
    implementation("io.grpc:grpc-stub:1.59.0")
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")

    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.2")
    implementation("com.fasterxml.jackson.core:jackson-core:2.17.2")
    implementation("com.fasterxml.jackson.core:jackson-annotations:2.17.2")

    testImplementation(kotlin("test"))
    testImplementation(ktorLibs.server.testHost)
}

ktor {
    fatJar {
        archiveFileName.set("app-fat.jar")
    }
}
