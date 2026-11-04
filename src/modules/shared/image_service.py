"""Processamento de imagens na própria API (Atividade 7).

Redimensiona até 800px, corrige orientação e grava WebP para entrega rápida.
"""

from __future__ import annotations

import io
import os
import uuid
from pathlib import Path

from PIL import Image, ImageOps

from src.modules.shared.errors import AppError

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def uploads_root() -> Path:
    return Path(os.getenv("UPLOAD_DIR", Path.cwd() / "uploads")).resolve()


def optimize_image(buffer: bytes, folder: str) -> str:
    if not buffer:
        raise AppError("Nenhuma imagem enviada", 400)
    if len(buffer) > MAX_IMAGE_BYTES:
        raise AppError("Imagem acima do limite de 5 MB", 413)

    try:
        image = Image.open(io.BytesIO(buffer))
        image.load()
    except Exception as exc:
        raise AppError("Arquivo de imagem inválido", 400) from exc

    image = ImageOps.exif_transpose(image)
    image.thumbnail((800, 800), Image.Resampling.BILINEAR)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    directory = uploads_root() / folder
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.webp"
    file_path = directory / filename
    image.save(file_path, format="WEBP", quality=80, method=0)

    return f"/uploads/{folder}/{filename}"
