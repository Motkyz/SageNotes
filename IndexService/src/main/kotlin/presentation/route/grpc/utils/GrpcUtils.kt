package ru.sagenotes.indexservice.presentation.route.grpc.utils

import io.grpc.Status
import io.grpc.StatusException

suspend fun <T> grpcCall(block: suspend () -> T): T {
    return try {
        block()
    } catch (e: Exception) {
        throw toGrpcException(e)
    }
}

fun toGrpcException(e: Exception): StatusException {
    val status = when (e) {
        is StatusException -> return e

        else -> Status.INTERNAL.withDescription(e.message ?: "Unknown error")
    }
    return status.asException()
}