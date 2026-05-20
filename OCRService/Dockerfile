FROM gradle:9.5.1-jdk26-alpine AS builder
WORKDIR /home/gradle/project
COPY . .
RUN gradle bootJar --no-daemon || gradle build --no-daemon

FROM eclipse-temurin:26-jre-alpine
WORKDIR /app
COPY --from=builder /home/gradle/project/build/libs/*.jar app.jar

CMD java -XX:MaxRAMPercentage=70 \
         -XX:MinRAMPercentage=50 \
         -XX:InitialRAMPercentage=30 \
         -XX:+UseG1GC \
         -XX:+UseStringDeduplication \
         -XX:+ExitOnOutOfMemoryError \
         -Djava.security.egd=file:/dev/./urandom \
         -jar app.jar