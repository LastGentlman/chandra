from dotenv import find_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings
import torch
import os


class Settings(BaseSettings):
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMAGE_DPI: int = 192
    MIN_PDF_IMAGE_DIM: int = 1024
    MIN_IMAGE_DIM: int = 1536
    MODEL_CHECKPOINT: str = "datalab-to/chandra"
    TORCH_DEVICE: str | None = None
    MAX_OUTPUT_TOKENS: int = 12384
    TORCH_ATTN: str | None = None
    BBOX_SCALE: int = 1024

    # vLLM server settings
    VLLM_API_KEY: str = "EMPTY"
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_MODEL_NAME: str = "chandra"
    VLLM_GPUS: str = "0"
    MAX_VLLM_RETRIES: int = 6

    # API authentication settings
    CHANDRA_API_KEY: str | None = None
    CHANDRA_REQUIRE_API_KEY: bool = False

    # API security hardening
    CHANDRA_ALLOWED_ORIGINS: str = "*"
    MAX_UPLOAD_MB: int = 25
    MAX_IMAGE_PIXELS: int = 80_000_000
    ALLOWED_FILE_EXTENSIONS: tuple[str, ...] = (
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".bmp",
        ".webp",
        ".heic",
        ".heif",
    )
    ALLOWED_FILE_MIME_TYPES: tuple[str, ...] = (
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/tiff",
        "image/bmp",
        "image/webp",
        "image/heic",
        "image/heif",
    )

    @computed_field
    @property
    def TORCH_DTYPE(self) -> torch.dtype:
        return torch.bfloat16

    @computed_field
    @property
    def MAX_UPLOAD_BYTES(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    class Config:
        env_file = find_dotenv("local.env")
        extra = "ignore"


settings = Settings()
