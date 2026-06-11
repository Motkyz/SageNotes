import requests
from temporalio.client import Client
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.presentation.dependencies import get_optional_user_id
from app.presentation.schemas import SummarizeRequest, SummarizeResponse, TokenRequest, TokenResponse

router = APIRouter(prefix="/summary", tags=["summary"])
security = HTTPBearer(auto_error=False)

TASK_QUEUE = "summarization-task-queue"


@router.post("/auth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest) -> TokenResponse:
    """Получить JWT-токен из Keycloak."""
    username = request.username or settings.keycloak_admin
    password = request.password or settings.keycloak_admin_password
    client_id = request.client_id or "admin-cli"

    response = requests.post(
        f"{settings.keycloak_server_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
        data={
            "client_id": client_id,
            "username": username,
            "password": password,
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        return TokenResponse(access_token="", error=response.text)

    data = response.json()
    return TokenResponse(access_token=data.get("access_token", ""))


@router.post("/", response_model=SummarizeResponse)
async def summarize_note(
    request: SummarizeRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    user_id: str = Depends(get_optional_user_id),
) -> SummarizeResponse:
    """Запуск Saga через Temporal."""
    client = await Client.connect("temporal:7233", namespace="default")

    result = await client.execute_workflow(
        "SummarizationWorkflow",
        args=[request.note_id, request.text, user_id],
        id=f"summary-{request.note_id}",
        task_queue=TASK_QUEUE,
    )

    return SummarizeResponse(note_id=result["note_id"], summary=result["summary"])