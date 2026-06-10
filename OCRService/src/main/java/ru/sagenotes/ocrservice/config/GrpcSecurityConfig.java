package ru.sagenotes.ocrservice.config;

import io.grpc.*;
import lombok.RequiredArgsConstructor;
import net.devh.boot.grpc.server.interceptor.GrpcGlobalServerInterceptor;
import net.devh.boot.grpc.server.security.authentication.BearerAuthenticationReader;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.security.oauth2.server.resource.authentication.BearerTokenAuthenticationToken;

@Configuration
@RequiredArgsConstructor
public class GrpcSecurityConfig {

    private final JwtDecoder jwtDecoder;

    @GrpcGlobalServerInterceptor
    public ServerInterceptor grpcServerSecurityInterceptor() {
        BearerAuthenticationReader reader = new BearerAuthenticationReader(BearerTokenAuthenticationToken::new);

        return new ServerInterceptor() {
            @Override
            public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
                    ServerCall<ReqT, RespT> call,
                    Metadata headers,
                    ServerCallHandler<ReqT, RespT> next) {

                BearerTokenAuthenticationToken authRequest = (BearerTokenAuthenticationToken) reader.readAuthentication(call, headers);

                if (authRequest == null) {
                    call.close(Status.UNAUTHENTICATED.withDescription("Missing Token"), new Metadata());
                    return new ServerCall.Listener<>() {};
                }

                try {
                    Jwt jwt = jwtDecoder.decode(authRequest.getToken());

                    JwtAuthenticationToken authentication = new JwtAuthenticationToken(jwt, null);
                    authentication.setAuthenticated(true);

                    SecurityContext context = SecurityContextHolder.createEmptyContext();
                    context.setAuthentication(authentication);

                    SecurityContextHolder.setContext(context);

                    ServerCall.Listener<ReqT> originalListener = next.startCall(call, headers);

                    return new ForwardingServerCallListener.SimpleForwardingServerCallListener<ReqT>(originalListener) {
                        @Override
                        public void onHalfClose() {
                            SecurityContextHolder.setContext(context);
                            try {
                                super.onHalfClose();
                            } finally {
                                SecurityContextHolder.clearContext();
                            }
                        }

                        @Override
                        public void onMessage(ReqT message) {
                            SecurityContextHolder.setContext(context);
                            try {
                                super.onMessage(message);
                            } finally {
                                SecurityContextHolder.clearContext();
                            }
                        }
                    };

                } catch (OAuth2AuthenticationException e) {
                    call.close(Status.UNAUTHENTICATED.withDescription("Invalid or Expired Token: " + e.getMessage()), new Metadata());
                    return new ServerCall.Listener<>() {};
                } finally {
                    SecurityContextHolder.clearContext();
                }
            }
        };
    }
}