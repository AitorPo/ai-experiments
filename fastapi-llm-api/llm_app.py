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
import json
from typing import Dict, List, Any, Optional
from mcp_integration import mcp_registry, execute_mcp_tool_call


app = FastAPI()
load_dotenv()
client = OpenAI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="fastapi-llm-api/response.log", level=logging.INFO)


# Get MCP tools from the registry
def get_mcp_tools():
    """Get all available MCP tools"""
    return mcp_registry.get_tool_definitions()


def llm_response(question: str, use_tools: bool = True):
    """Enhanced LLM response with MCP tools support"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to various tools. Use the appropriate tools when needed to answer questions comprehensively."},
        {
            "role": "user",
            "content": f"Answer this question: {question}",
        },
    ]
    
    # First call with tools enabled
    if use_tools:
        mcp_tools = get_mcp_tools()
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            tools=mcp_tools,
            tool_choice="auto"
        )
        
        # Check if the model wants to use tools
        if response.choices[0].message.tool_calls:
            logger.info("Using tools")
            # Execute tool calls
            messages.append(response.choices[0].message)
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_result = execute_mcp_tool_call(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            
            # Get final response with tool results
            final_response = client.beta.chat.completions.parse(
                messages=messages,
                model="gpt-4o-mini",
                response_format=QAAnalytics
            )
            return final_response
        else:
            # No tools used, parse the response directly
            logger.info("Not using tools")
            messages.append(response.choices[0].message)
            final_response = client.beta.chat.completions.parse(
                messages=messages,
                model="gpt-4o-mini",
                response_format=QAAnalytics
            )
            return final_response
    else:
        # Original behavior without tools
        logger.info("Original behavior without tools")
        response = client.beta.chat.completions.parse(
            messages=messages,
            model="gpt-4o-mini",
            response_format=QAAnalytics
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
    # Get response with MCP tools support
    response = llm_response(question=request.question, use_tools=True)
    # Parse the response content
    qa_instance = response.choices[0].message.parsed
    
    log_response(logger, qa_instance)
    return qa_instance


@app.post("/api/question_no_tools", response_model=QAAnalytics)
def llm_qa_response_no_tools(request: QuestionRequest):
    """Endpoint for responses without MCP tools (legacy behavior)"""
    logger.info(f"Received question (no tools): {request.question}")
    # Get response without tools
    response = llm_response(question=request.question, use_tools=False)
    # Parse the response content
    qa_instance = response.choices[0].message.parsed
    
    log_response(logger, qa_instance)
    return qa_instance


@app.get("/api/mcp/tools")
def get_available_mcp_tools():
    """Get list of available MCP tools"""
    tools = get_mcp_tools()
    return {
        "available_tools": len(tools),
        "tools": [
            {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "parameters": list(tool["function"]["parameters"]["properties"].keys())
            }
            for tool in tools
        ]
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_tools_available": len(get_mcp_tools()),
        "service": "FastAPI LLM with MCP Tools"
    }


if __name__ == "__main__":
    uvicorn.run("llm_app:app", host="0.0.0.0", port=8888, reload=True)
    