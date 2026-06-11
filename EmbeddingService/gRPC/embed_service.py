from sentence_transformers import SentenceTransformer
from gRPC.generate.embed_pb2 import EmbedResponse, Embedding
from gRPC.generate.embed_pb2_grpc import EmbedServiceServicer
import grpc

class EmbedGrpcService(EmbedServiceServicer):
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def GetEmbeddings(self, request, context):
        try:
            texts = [text for text in request.texts]

            if not texts:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Texts list cannot be empty"
                )
                return EmbedResponse()

            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True
            )

            proto_embeddings = [
                Embedding(values=emb.tolist())
                for emb in embeddings
            ]

            return EmbedResponse(embeddings=proto_embeddings)

        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Error generating embeddings: {str(e)}"
            )
            return EmbedResponse()