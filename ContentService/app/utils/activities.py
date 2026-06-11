import grpc
import httpx
from temporalio import activity

from app.grpc.generated.ocr import ocr_pb2, ocr_pb2_grpc
from app.grpc.generated.index import index_pb2, index_pb2_grpc
from app.schemas.index_schemas import IndexRequest
from app.schemas.ocr_schemas import OcrResponseListDTO, OcrRequest


@activity.defn(name="process_ocr_activity")
async def process_ocr_activity(ocr_request: OcrRequest, token: str) -> str:

    if not ocr_request.files:
        return ""

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                "http://ocr-service:8080/ocr/upload",
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
                "http://index-service:8080/index",
                json=index_request,
                headers=headers
            )
            response.raise_for_status()
            return "Indexed successfully"
        except httpx.HTTPStatusError as e:
            activity.logger.error(f"Index Service error: {e.response.text}")
            raise e


@activity.defn(name="process_ocr_grpc_activity")
async def process_ocr_grpc_activity(ocr_request: OcrRequest, token: str) -> str:
    async with grpc.aio.insecure_channel("ocr-service:9090") as channel:
        stub = ocr_pb2_grpc.OcrGrpcServiceStub(channel)
        files = [ocr_pb2.OcrFileRequest(fid=f.fid, file_url=f.file_url) for f in ocr_request.files]
        request = ocr_pb2.ProcessOcrRequest(note_id=ocr_request.note_id, files=files)

        metadata = (("authorization", f"Bearer {token}"),)
        try:
            response = await stub.ProcessOcr(request, metadata=metadata)
            return "\n".join([f.text for f in response.files if f.text])
        except grpc.RpcError as e:
            activity.logger.error(f"gRPC OCR error: {e.code()} - {e.details()}")
            raise e


@activity.defn(name="index_document_grpc_activity")
async def index_document_grpc_activity(index_request: IndexRequest, token: str) -> str:
    async with grpc.aio.insecure_channel("index-service:9090") as channel:
        stub = index_pb2_grpc.IndexServiceStub(channel)
        request = index_pb2.IndexRequest(note_id=index_request.note_id, text=index_request.text)

        metadata = (("authorization", f"Bearer {token}"),)
        try:
            response = await stub.Index(request, metadata=metadata)
            print("grpc index started")
            return "Indexed successfully"
        except grpc.RpcError as e:
            activity.logger.error(f"gRPC Index error: {e.code()} - {e.details()}")
            raise e