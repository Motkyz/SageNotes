from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import requests
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64

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


class KeycloakJWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
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

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token"
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use Bearer token."
            )

        token = credentials.credentials
        payload = self._verify_token(token)

        request.state.user = payload
        return payload

    def _verify_token(self, token: str) -> dict:
        try:
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

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )


def get_current_user_id(request: Request) -> str:
    user_id = getattr(request.state, 'user', {}).get('sub')

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    print(user_id)
    return str(user_id)


keycloak_auth = KeycloakJWTBearer()