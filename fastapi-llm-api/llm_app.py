import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, Depends
import logging
from pydantic import BaseModel
from common.models import QAAnalytics, QuestionRequest
from common.utils import encode_uploaded_image_to_base64, QuestionPayload, parse_form_data
from dotenv import load_dotenv
from openai import OpenAI


app = FastAPI()
load_dotenv()
client = OpenAI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="fastapi-llm-api/response.log", level=logging.INFO)


def llm_response(question: str):
    response = client.beta.chat.completions.parse(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Answer this question: {question}",
            },
        ],
        model="gpt-4o-mini",
        response_format=QAAnalytics,
    )
    return response


def log_response(logger: logging.Logger, response: QAAnalytics):
    logger.info(f"Question: {response.question}")
    logger.info(f"Answer: {response.answer}")
    logger.info(f"Thought: {response.thought}")
    logger.info(f"Topic: {response.topic}")
    
    
@app.post("/api/question", response_model=QAAnalytics)
def llm_qa_response(request: QuestionRequest):
    logger.info(f"Received question: {request.question}")
    # Get response from ollama
    response = llm_response(question=request.question)
    logger.info(f"Response: {response}")
    # Parse the response content
    qa_instance = response.choices[0].message.parsed
    
    log_response(logger, qa_instance)
    return qa_instance


if __name__ == "__main__":
    uvicorn.run("llm_app:app", host="0.0.0.0", port=8888, reload=True)
    