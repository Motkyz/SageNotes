plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(ktorLibs.plugins.ktor)
    alias(libs.plugins.kotlin.serialization)
    id("com.google.protobuf") version "0.9.4"
}

group = "ru.sagenotes.authservice"
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

    implementation("io.github.oshai:kotlin-logging-jvm:8.0.01")

    val koin = "4.1.1"
    implementation("io.insert-koin:koin-ktor:$koin")

    implementation("io.grpc:grpc-netty:1.59.0")
    implementation("io.grpc:grpc-protobuf:1.59.0")
    implementation("io.grpc:grpc-stub:1.59.0")
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")

    implementation("io.ktor:ktor-server-metrics-micrometer:3.5.0")
    implementation("io.micrometer:micrometer-registry-prometheus:1.10.3")

    testImplementation(kotlin("test"))
    testImplementation(ktorLibs.server.testHost)
}

ktor {
    fatJar {
        archiveFileName.set("app-fat.jar")
    }
}
