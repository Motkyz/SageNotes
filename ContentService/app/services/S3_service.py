import os
from uuid import uuid7

from botocore.exceptions import ClientError
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from app.config import s3_client, settingS3


class S3Service:
    def __init__(self):
        self.client = s3_client
        self.bucket = settingS3.S3_BUCKET

    def _upload(self, file_obj, key: str):
        self.client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=self.bucket,
            Key=key,
        )

    def _delete(self, key: str):
        self.client.delete_object(
            Bucket=self.bucket,
            Key=key,
        )

    async def upload_file(self, note_id: str, file: UploadFile):
        file_name = os.path.splitext(file.filename)[0]
        extension = os.path.splitext(file.filename)[1]
        unique_uuid = uuid7()
        key = f"{note_id}/{file_name}_{unique_uuid}.{extension}"

        try:
            await run_in_threadpool(
                self._upload,
                file.file,
                key,
            )
            return key

        except ClientError as e:
            raise RuntimeError(
                f"Error uploading file '{file.filename}' to S3: {e}"
            )

    async def generate_presigned_url(self, key: str):
        url = s3_client.generate_presigned_url(ClientMethod='get_object',
                                               Params={
                                                   "Bucket": self.bucket,
                                                   "Key": key,
                                               },
                                               ExpiresIn=900)
        return url

    async def delete_file(self, key: str) -> bool:
        try:
            await run_in_threadpool(
                self._delete,
                key,
            )
            return True

        except ClientError as e:
            raise RuntimeError(
                f"Error deleting file '{key}' from S3: {e}"
            )



s3_service = S3Service()