import httpx
from temporalio import activity

from app.schemas.ocr_schemas import OcrResponseListDTO

INDEX_SERVICE_URL = "http://index-service:8080/index"
OCR_SERVICE_URL = "http://ocr-service:8080/ocr/upload"


@activity.defn(name="process_ocr_activity")
async def process_ocr_activity(ocr_request: dict, token: str) -> str:

    if not ocr_request.get("files"):
        return ""

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                OCR_SERVICE_URL,
                json=ocr_request,
                headers=headers
            )
            response.raise_for_status()

            response_data = OcrResponseListDTO(**response.json())

            combined_text = "\n".join([f.text for f in response_data.files if f.text])
            return combined_text

        except httpx.HTTPStatusError as e:
            activity.logger.error(f"OCR Service returned status error: {e.response.text}")
            raise e
        except httpx.RequestError as e:
            activity.logger.error(f"Network error talking to OCR Service: {e}")
            raise e


@activity.defn(name="index_document_activity")
async def index_document_activity(index_request: dict, token: str) -> str:

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                INDEX_SERVICE_URL,
                json=index_request,
                headers=headers
            )
            response.raise_for_status()
            return "Indexed successfully"
        except httpx.HTTPStatusError as e:
            activity.logger.error(f"Index Service error: {e.response.text}")
            raise e