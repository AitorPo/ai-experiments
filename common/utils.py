"""
Utility functions shared across the application
"""
import base64
from fastapi import UploadFile, File, Form


class QuestionPayload:
    """Class to structure the incoming form data"""
    def __init__(self, question: str, image: UploadFile):
        self.question = question
        self.image = image
        
    def __str__(self):
        return f"QuestionPayload(question='{self.question}', image='{self.image.filename}')"


def parse_form_data(
    question: str = Form(..., description="The question to be answered"),
    image: UploadFile = File(..., description="Image file to analyze")
) -> QuestionPayload:
    """Dependency function to parse form data into a structured payload"""
    return QuestionPayload(question=question, image=image)


def encode_uploaded_image_to_base64(image_file: UploadFile) -> str:
    """Convert uploaded file to base64 string"""
    image_data = image_file.file.read()
    return base64.b64encode(image_data).decode("utf-8") 