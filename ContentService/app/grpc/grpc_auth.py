import base64
from typing import Optional

import grpc
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from app.config import settingKeycloak


def rsa_public_key_from_jwk(jwk: dict) -> str:
    n = base64.urlsafe_b64decode(jwk['n'] + '==')
    e = base64.urlsafe_b64decode(jwk['e'] + '==')

    public_numbers = RSAPublicNumbers(
        int.from_bytes(e, 'big'),
        int.from_bytes(n, 'big')
    )
    public_key = public_numbers.public_key(default_backend())
    pem = public_key.public_bytes(
        Encoding.PEM,
        PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')


class GrpcAuthService:
    def __init__(self):
        self.jwks_url = settingKeycloak.jwks_url
        self.issuer = settingKeycloak.issuer
        self.audience = settingKeycloak.KEYCLOAK_AUDIENCE
        self.jwks = self._get_jwks()

    def _get_jwks(self) -> dict:
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Could not fetch JWKS from {self.jwks_url}: {e}")
            return {"keys": []}

    def _verify_token(self, token: str) -> dict:
        headers = jwt.get_unverified_headers(token)
        kid = headers.get('kid')

        if not kid:
            raise JWTError("No 'kid' in token header")

        key_data = None
        for key in self.jwks.get('keys', []):
            if key.get('kid') == kid:
                key_data = key
                break

        if not key_data:
            self.jwks = self._get_jwks()
            for key in self.jwks.get('keys', []):
                if key.get('kid') == kid:
                    key_data = key
                    break

            if not key_data:
                raise JWTError(f"Matching key (kid={kid}) not found in JWKS")

        public_key = rsa_public_key_from_jwk(key_data)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=self.audience,
            issuer=self.issuer,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
            }
        )
        return payload

    async def get_current_user_id(self, context: grpc.aio.ServicerContext) -> Optional[str]:
        metadata = dict(context.invocation_metadata())
        auth_header: Optional[str] = metadata.get("authorization")

        if not auth_header:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Missing authorization token"
            )
            return None

        if not auth_header.startswith("Bearer "):
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Invalid authentication scheme. Use Bearer token."
            )
            return None

        token = auth_header[7:]

        try:
            payload = self._verify_token(token)
            user_id = payload.get('sub')

            if not user_id:
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "User ID (sub) not found in token"
                )
                return None

            return str(user_id)

        except ExpiredSignatureError:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Token expired"
            )
            return None
        except JWTError as e:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                f"Invalid token: {str(e)}"
            )
            return None
        except Exception as e:
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                f"Authentication error: {str(e)}"
            )
            return None

grpc_auth_service = GrpcAuthService()