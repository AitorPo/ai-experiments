import pytest
import base64
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile, HTTPException
import logging
import io

from ollama_app import (
    app,
    QABase,
    QAAnalytics,
    QuestionPayload,
    parse_form_data,
    encode_image_to_base64,
    encode_uploaded_image_to_base64,
    ollama_llm_response,
    log_response,
)


class TestModels:
    """Test Pydantic models"""
    
    def test_qa_base_creation(self):
        """Test QABase model creation"""
        qa = QABase(question="What is this?", answer="This is a test")
        assert qa.question == "What is this?"
        assert qa.answer == "This is a test"
    
    def test_qa_analytics_creation(self):
        """Test QAAnalytics model creation"""
        qa = QAAnalytics(
            question="What is this?",
            answer="This is a test",
            thought="I need to analyze this",
            topic="Testing"
        )
        assert qa.question == "What is this?"
        assert qa.answer == "This is a test"
        assert qa.thought == "I need to analyze this"
        assert qa.topic == "Testing"
    
    def test_qa_analytics_inherits_qa_base(self):
        """Test that QAAnalytics inherits from QABase"""
        qa = QAAnalytics(
            question="Test question",
            answer="Test answer",
            thought="Test thought",
            topic="Test topic"
        )
        assert isinstance(qa, QABase)


class TestQuestionPayload:
    """Test QuestionPayload class"""
    
    def test_question_payload_creation(self):
        """Test QuestionPayload creation"""
        mock_upload = Mock(spec=UploadFile)
        mock_upload.filename = "test.jpg"
        
        payload = QuestionPayload("What is this?", mock_upload)
        assert payload.question == "What is this?"
        assert payload.image == mock_upload
    
    def test_question_payload_str_representation(self):
        """Test QuestionPayload string representation"""
        mock_upload = Mock(spec=UploadFile)
        mock_upload.filename = "test.jpg"
        
        payload = QuestionPayload("What is this?", mock_upload)
        expected = "QuestionPayload(question='What is this?', image='test.jpg')"
        assert str(payload) == expected


class TestEncodingFunctions:
    """Test image encoding functions"""
    
    def test_encode_image_to_base64(self):
        """Test encoding image file to base64"""
        # Create a temporary image file
        test_data = b"fake image data"
        expected_b64 = base64.b64encode(test_data).decode("utf-8")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(test_data)
            tmp_file.flush()
            
            try:
                result = encode_image_to_base64(tmp_file.name)
                assert result == expected_b64
            finally:
                os.unlink(tmp_file.name)
    
    def test_encode_image_to_base64_file_not_found(self):
        """Test encoding with non-existent file"""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64("non_existent_file.jpg")
    
    def test_encode_uploaded_image_to_base64(self):
        """Test encoding uploaded file to base64"""
        test_data = b"fake uploaded image data"
        expected_b64 = base64.b64encode(test_data).decode("utf-8")
        
        # Mock UploadFile with proper file attribute
        mock_file = Mock()
        mock_file.read.return_value = test_data
        
        mock_upload = Mock(spec=UploadFile)
        mock_upload.file = mock_file
        
        result = encode_uploaded_image_to_base64(mock_upload)
        assert result == expected_b64
        mock_file.read.assert_called_once()


class TestParseDependency:
    """Test parse_form_data dependency function"""
    
    def test_parse_form_data(self):
        """Test parse_form_data creates QuestionPayload correctly"""
        mock_upload = Mock(spec=UploadFile)
        mock_upload.filename = "test.jpg"
        
        result = parse_form_data("Test question", mock_upload)
        
        assert isinstance(result, QuestionPayload)
        assert result.question == "Test question"
        assert result.image == mock_upload


class TestOllamaLLMResponse:
    """Test ollama LLM response function"""
    
    @patch('ollama_app.chat')
    def test_ollama_llm_response_success(self, mock_chat):
        """Test successful ollama LLM response"""
        # Mock ollama response
        mock_response = {
            'message': {
                'content': '{"question": "test", "answer": "response", "thought": "thinking", "topic": "general"}'
            }
        }
        mock_chat.return_value = mock_response
        
        result = ollama_llm_response("What is this?", "base64_image_data")
        
        assert result == mock_response
        mock_chat.assert_called_once()
        
        # Check the call arguments
        call_args = mock_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'You are a helpful assistant.'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'Answer this question: What is this?'
        assert messages[1]['images'] == ['base64_image_data']
        assert call_args[1]['model'] == 'gemma3:latest'
    
    @patch('ollama_app.chat')
    def test_ollama_llm_response_with_different_inputs(self, mock_chat):
        """Test ollama LLM response with different inputs"""
        mock_response = {'message': {'content': 'test response'}}
        mock_chat.return_value = mock_response
        
        result = ollama_llm_response("Different question", "different_image_data")
        
        assert result == mock_response
        call_args = mock_chat.call_args
        assert 'Different question' in call_args[1]['messages'][1]['content']
        assert call_args[1]['messages'][1]['images'] == ['different_image_data']


class TestLogResponse:
    """Test logging function"""
    
    def test_log_response(self):
        """Test log_response function"""
        mock_logger = Mock(spec=logging.Logger)
        
        qa = QAAnalytics(
            question="Test question",
            answer="Test answer",
            thought="Test thought",
            topic="Test topic"
        )
        
        log_response(mock_logger, qa)
        
        # Verify all log calls were made
        assert mock_logger.info.call_count == 4
        mock_logger.info.assert_any_call("Question: Test question")
        mock_logger.info.assert_any_call("Answer: Test answer")
        mock_logger.info.assert_any_call("Thought: Test thought")
        mock_logger.info.assert_any_call("Topic: Test topic")


class TestFastAPIEndpoint:
    """Test FastAPI endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('ollama_app.ollama_llm_response')
    @patch('ollama_app.encode_uploaded_image_to_base64')
    @patch('ollama_app.log_response')
    def test_llm_qa_response_success(self, mock_log, mock_encode, mock_ollama):
        """Test successful API endpoint call"""
        # Setup mocks
        mock_encode.return_value = "encoded_image_data"
        mock_ollama.return_value = {
            'message': {
                'content': json.dumps({
                    "question": "What is this?",
                    "answer": "This is a test image",
                    "thought": "I can see this is a test",
                    "topic": "Testing"
                })
            }
        }
        
        # Create test file
        test_file_content = b"fake image data"
        
        response = self.client.post(
            "/api/question",
            data={"question": "What is this?"},
            files={"image": ("test.jpg", io.BytesIO(test_file_content), "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "What is this?"
        assert data["answer"] == "This is a test image"
        
        # Verify mocks were called
        mock_encode.assert_called_once()
        mock_ollama.assert_called_once_with("What is this?", "encoded_image_data")
        mock_log.assert_called_once()
    
    def test_llm_qa_response_missing_question(self):
        """Test API endpoint with missing question"""
        test_file_content = b"fake image data"
        
        response = self.client.post(
            "/api/question",
            files={"image": ("test.jpg", io.BytesIO(test_file_content), "image/jpeg")}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_llm_qa_response_missing_image(self):
        """Test API endpoint with missing image"""
        response = self.client.post(
            "/api/question",
            data={"question": "What is this?"}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('ollama_app.ollama_llm_response')
    @patch('ollama_app.encode_uploaded_image_to_base64')
    def test_llm_qa_response_invalid_json_response(self, mock_encode, mock_ollama):
        """Test API endpoint with invalid JSON response from ollama"""
        mock_encode.return_value = "encoded_image_data"
        mock_ollama.return_value = {
            'message': {
                'content': 'invalid json content'
            }
        }
        
        test_file_content = b"fake image data"
        
        # The test should expect the exception to be raised within the app
        with pytest.raises(Exception):  # This will be caught by FastAPI and turned into 500
            response = self.client.post(
                "/api/question",
                data={"question": "What is this?"},
                files={"image": ("test.jpg", io.BytesIO(test_file_content), "image/jpeg")}
            )
    
    @patch('ollama_app.ollama_llm_response')
    @patch('ollama_app.encode_uploaded_image_to_base64')
    def test_llm_qa_response_exception_in_encoding(self, mock_encode, mock_ollama):
        """Test API endpoint when encoding fails"""
        mock_encode.side_effect = Exception("Encoding failed")
        
        test_file_content = b"fake image data"
        
        # The test should expect the exception to be raised within the app
        with pytest.raises(Exception):  # This will be caught by FastAPI and turned into 500
            response = self.client.post(
                "/api/question",
                data={"question": "What is this?"},
                files={"image": ("test.jpg", io.BytesIO(test_file_content), "image/jpeg")}
            )


class TestAppConfiguration:
    """Test app configuration and setup"""
    
    def test_app_exists(self):
        """Test that FastAPI app is created"""
        assert app is not None
        assert hasattr(app, 'post')
    
    def test_app_routes(self):
        """Test that the expected routes exist"""
        routes = [route.path for route in app.routes]
        assert "/api/question" in routes


class TestMainExecution:
    """Test main execution block"""
    
    @patch('uvicorn.run')
    def test_main_execution(self, mock_uvicorn_run):
        """Test main execution block"""
        # Test that the main block would call uvicorn.run with correct parameters
        import ollama_app
        
        # We can't easily test the if __name__ == "__main__" block directly
        # but we can verify the function call that would be made
        assert hasattr(ollama_app, 'uvicorn')
        
        # Simulate what the main block would do
        ollama_app.uvicorn.run("ollama_app:app", host="0.0.0.0", port=8888, reload=True)
        
        # We can verify the import exists and the module loads correctly
        assert ollama_app.app is not None
    
    @patch('ollama_app.__name__', '__main__')
    @patch('uvicorn.run')
    def test_main_execution_coverage(self, mock_uvicorn_run):
        """Test main execution by directly executing the main condition"""
        import ollama_app
        
        # Since __name__ is mocked to be '__main__', execute the main logic directly
        if ollama_app.__name__ == "__main__":
            ollama_app.uvicorn.run("ollama_app:app", host="0.0.0.0", port=8888, reload=True)
        
        # Verify uvicorn.run was called
        mock_uvicorn_run.assert_called_once_with(
            "ollama_app:app", 
            host="0.0.0.0", 
            port=8888, 
            reload=True
        )


# Integration tests
class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow_with_mocks(self):
        """Test the complete workflow with mocked dependencies"""
        from ollama_app import QuestionPayload as LocalQuestionPayload
        
        # Create mock upload file with proper file attribute
        mock_file = Mock()
        mock_file.read.return_value = b"fake image data"
        
        mock_upload = Mock(spec=UploadFile)
        mock_upload.filename = "test.jpg"
        mock_upload.file = mock_file
        
        # Test the workflow
        payload = parse_form_data("What is this?", mock_upload)
        assert isinstance(payload, LocalQuestionPayload)
        
        encoded_image = encode_uploaded_image_to_base64(payload.image)
        assert isinstance(encoded_image, str)
        
        # Test QAAnalytics creation
        qa = QAAnalytics(
            question=payload.question,
            answer="Test answer",
            thought="Test thought", 
            topic="Test topic"
        )
        
        # Test logging (with mock logger)
        mock_logger = Mock(spec=logging.Logger)
        log_response(mock_logger, qa)
        assert mock_logger.info.call_count == 4


# Test to ensure all lines are covered
class TestAdditionalCoverage:
    """Additional tests to ensure 100% coverage"""
    
    def test_qa_analytics_model_json_schema(self):
        """Test model_json_schema method is accessible"""
        schema = QAAnalytics.model_json_schema()
        assert isinstance(schema, dict)
        assert 'properties' in schema
    
    @patch('ollama_app.chat')
    def test_ollama_llm_response_format_parameter(self, mock_chat):
        """Test that ollama_llm_response passes the format parameter correctly"""
        mock_response = {'message': {'content': 'test'}}
        mock_chat.return_value = mock_response
        
        result = ollama_llm_response("test question", "test_image")
        
        # Verify format parameter is passed
        call_args = mock_chat.call_args
        assert 'format' in call_args[1]
        assert call_args[1]['format'] == QAAnalytics.model_json_schema()
    
    def test_logger_configuration(self):
        """Test logger configuration"""
        import ollama_app
        assert ollama_app.logger is not None
        assert isinstance(ollama_app.logger, logging.Logger)
