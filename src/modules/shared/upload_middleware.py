"""Recebe upload multipart em memória, no papel do Multer da atividade."""

from flask import jsonify, request

from src.modules.shared.errors import AppError
from src.modules.shared.image_service import ALLOWED_CONTENT_TYPES, MAX_IMAGE_BYTES


def read_image_file(field_name: str = "image") -> bytes:
    file = request.files.get(field_name)
    if file is None or not file.filename:
        raise AppError("Nenhuma imagem enviada", 400)

    content_type = (file.mimetype or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise AppError("Formato de imagem não permitido", 400)

    buffer = file.read()
    if not buffer:
        raise AppError("Nenhuma imagem enviada", 400)
    if len(buffer) > MAX_IMAGE_BYTES:
        raise AppError("Imagem acima do limite de 5 MB", 413)
    return buffer


def payload_too_large(_error):
    return jsonify({"error": "Imagem acima do limite de 5 MB"}), 413
