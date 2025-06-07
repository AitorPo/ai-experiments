from pydantic import BaseModel, Field
import base64
from ollama import chat
from fastapi import FastAPI, File, UploadFile, Form, Depends
import logging
import uvicorn

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="response.log", level=logging.INFO)


class QABase(BaseModel):
    question: str = Field(description="The question to be answered")
    answer: str = Field(description="The answer to the question")


class QAAnalytics(QABase):
    thought: str = Field(description="The thought process of the model")
    topic: str = Field(description="The topic of the question")


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


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def encode_uploaded_image_to_base64(image_file: UploadFile) -> str:
    """Convert uploaded file to base64 string"""
    image_data = image_file.file.read()
    return base64.b64encode(image_data).decode("utf-8")


def ollama_llm_response(question: str, encode_image: str):
    response = chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Answer this question: {question}",
                "images": [encode_image],
            },
        ],
        model="gemma3:latest",
        format=QAAnalytics.model_json_schema(),
    )
    return response
    
    
def log_response(logger: logging.Logger, response: QAAnalytics):
    logger.info(f"Question: {response.question}")
    logger.info(f"Answer: {response.answer}")
    logger.info(f"Thought: {response.thought}")
    logger.info(f"Topic: {response.topic}")
    
    
@app.post("/api/question", response_model=QABase)
def llm_qa_response(payload: QuestionPayload = Depends(parse_form_data)):
    logger.info(f"Received payload: {payload}")
    
    # Convert uploaded image to base64
    encoded_image = encode_uploaded_image_to_base64(payload.image)
    
    # Get response from ollama
    response = ollama_llm_response(payload.question, encoded_image)
    
    # Parse the response content
    qa_instance = QAAnalytics.model_validate_json(response['message']['content'])
    
    log_response(logger, qa_instance)
    return qa_instance

    
if __name__ == "__main__":
    uvicorn.run("ollama_app:app", host="0.0.0.0", port=8888, reload=True)
