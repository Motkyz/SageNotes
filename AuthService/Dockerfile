FROM gradle:9.1.0-jdk21-alpine AS builder

RUN apk add --no-cache gcompat

WORKDIR /home/gradle/project

COPY build.gradle.kts settings.gradle.kts gradle.properties ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

COPY src/main/kotlin/presentation/proto ./src/main/kotlin/presentation/proto
RUN gradle generateProto --no-daemon || true

COPY src ./src
RUN gradle buildFatJar --no-daemon --parallel --build-cache

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /home/gradle/project/build/libs/app-fat.jar /app/app.jar

CMD java -XX:MaxRAMPercentage=70 \
         -XX:MinRAMPercentage=50 \
         -XX:InitialRAMPercentage=30 \
         -XX:+UseG1GC \
         -XX:+UseStringDeduplication \
         -XX:+ExitOnOutOfMemoryError \
         -Djava.security.egd=file:/dev/./urandom \
         -jar /app/*.jar