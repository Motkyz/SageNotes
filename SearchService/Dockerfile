FROM gradle:9.1.0-jdk21-alpine AS builder

RUN apk add --no-cache gcompat

WORKDIR /home/gradle/project
COPY . .
RUN gradle shadowJar --no-daemon || gradle build --no-daemon

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /home/gradle/project/build/libs/app-fat.jar /app/libs/

CMD java -XX:MaxRAMPercentage=70 \
         -XX:MinRAMPercentage=50 \
         -XX:InitialRAMPercentage=30 \
         -XX:+UseG1GC \
         -XX:+UseStringDeduplication \
         -XX:+ExitOnOutOfMemoryError \
         -Djava.security.egd=file:/dev/./urandom \
         -jar /app/libs/*.jar