"""
Utility functions shared across the application
"""
import base64
from fastapi import UploadFile


def encode_uploaded_image_to_base64(image_file: UploadFile) -> str:
    """Convert uploaded file to base64 string"""
    image_data = image_file.file.read()
    return base64.b64encode(image_data).decode("utf-8") 