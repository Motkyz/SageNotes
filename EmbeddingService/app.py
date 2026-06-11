import threading
import asyncio
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import uvicorn
import grpc
from concurrent import futures

from gRPC.embed_service import EmbedGrpcService
from gRPC.generate.embed_pb2_grpc import add_EmbedServiceServicer_to_server

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

class EmbedRequest(BaseModel):
    texts: list[str]

class EmbedResponse(BaseModel):
    embeddings: list[list[float]]

@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    embeddings = model.encode(request.texts, normalize_embeddings=True)
    return EmbedResponse(embeddings=embeddings.tolist())


def run_grpc():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    add_EmbedServiceServicer_to_server(
        EmbedGrpcService(),
        server
    )

    server.add_insecure_port("[::]:9090")
    server.start()

    print("gRPC server started on port 9090")

    server.wait_for_termination()


def run_http():
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    grpc_thread = threading.Thread(target=run_grpc, daemon=True,)
    grpc_thread.start()
    run_http()