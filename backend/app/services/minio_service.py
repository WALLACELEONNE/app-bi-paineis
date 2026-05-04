import hashlib
import io
import structlog
from minio import Minio
from app.core.config import settings

logger = structlog.get_logger()

_minio_client: Minio | None = None


def get_minio() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        _ensure_bucket(_minio_client)
    return _minio_client


def _ensure_bucket(client: Minio):
    bucket = settings.MINIO_BUCKET
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        logger.info("minio_bucket_created", bucket=bucket)


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def upload_to_minio(file_content: bytes, filename: str, tenant_id: int) -> str:
    client = get_minio()
    storage_path = f"{tenant_id}/{filename}"
    client.put_object(
        settings.MINIO_BUCKET,
        storage_path,
        data=io.BytesIO(file_content),
        length=len(file_content),
        content_type="application/octet-stream",
    )
    return storage_path


def get_file_from_minio(storage_path: str) -> bytes:
    client = get_minio()
    response = client.get_object(settings.MINIO_BUCKET, storage_path)
    return response.read()
