package ru.sagenotes.notificationservice.presentation.route.grpc.utils

import io.grpc.Status
import io.grpc.StatusException
import ru.sagenotes.notificationservice.presentation.route.grpc.interceptor.JwtAuthInterceptor

fun getCurrentUserId(): String {
    return JwtAuthInterceptor.USER_ID_CONTEXT_KEY.get()
        ?: throw StatusException(
            Status.UNAUTHENTICATED.withDescription("User not authenticated")
        )
}