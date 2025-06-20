import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama import chat
from fastapi import FastAPI, Depends
import logging
import uvicorn
from common.models import QABase, QAAnalytics
from common.utils import encode_uploaded_image_to_base64, QuestionPayload, parse_form_data

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="fastapi-ollama-api/response.log", level=logging.INFO)


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
