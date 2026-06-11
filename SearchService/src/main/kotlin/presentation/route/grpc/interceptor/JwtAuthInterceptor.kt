package ru.sagenotes.searchservice.presentation.route.grpc.interceptor

import com.auth0.jwk.JwkProvider
import com.auth0.jwk.JwkProviderBuilder
import com.auth0.jwt.JWT
import com.auth0.jwt.algorithms.Algorithm
import io.grpc.*
import ru.sagenotes.searchservice.data.config.JwtConfig
import java.net.URL
import java.security.interfaces.RSAPublicKey

class JwtAuthInterceptor(
    private val jwtConfig: JwtConfig
) : ServerInterceptor {
    val jwkProvider: JwkProvider = JwkProviderBuilder(URL(jwtConfig.certsUrl)).build()

    companion object {
        val USER_ID_CONTEXT_KEY: Context.Key<String> = Context.key("userId")
        private const val BEARER_PREFIX = "Bearer "
        private val AUTHORIZATION_METADATA_KEY = Metadata.Key.of("authorization", Metadata.ASCII_STRING_MARSHALLER)
    }

    override fun <ReqT, RespT> interceptCall(
        call: ServerCall<ReqT, RespT>,
        headers: Metadata,
        next: ServerCallHandler<ReqT, RespT>
    ): ServerCall.Listener<ReqT> {
        val authHeader = headers[AUTHORIZATION_METADATA_KEY]

        if (authHeader == null || !authHeader.startsWith(BEARER_PREFIX)) {
            call.close(
                Status.UNAUTHENTICATED.withDescription("Missing or invalid authorization header"),
                headers
            )
            return object : ServerCall.Listener<ReqT>() {}
        }

        val token = authHeader.substring(BEARER_PREFIX.length)

        return try {
            val userId = validateToken(token)
            val context = Context.current().withValue(USER_ID_CONTEXT_KEY, userId)
            Contexts.interceptCall(context, call, headers, next)
        } catch (e: Exception) {
            call.close(
                Status.UNAUTHENTICATED.withDescription("Invalid token: ${e.message}"),
                headers
            )
            object : ServerCall.Listener<ReqT>() {}
        }
    }

    private fun validateToken(token: String): String {
        val decodedJWT = JWT.decode(token)

        val jwk = jwkProvider.get(decodedJWT.keyId)
        val publicKey = jwk.publicKey as RSAPublicKey

        val algorithm = Algorithm.RSA256(publicKey, null)
        val verifier = JWT.require(algorithm)
            .withAudience(jwtConfig.audience)
            .build()

        val verifiedJWT = verifier.verify(token)

        val userId = verifiedJWT.getClaim("sub")?.asString()

        if (userId.isNullOrBlank()) {
            throw IllegalArgumentException("User ID not found in token")
        }

        return userId
    }
}