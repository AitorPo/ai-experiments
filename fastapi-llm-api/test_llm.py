import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import logging

# Add the parent directory to the path to import common modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the OpenAI client before importing llm_app to avoid API key requirement
with patch('openai.OpenAI'):
    from llm_app import app, llm_response, log_response
    from common.models import QAAnalytics, QuestionRequest


class TestLLMApp:
    """Test suite for the LLM FastAPI application."""
    
    def setup_method(self):
        """Set up test client and mock data."""
        self.client = TestClient(app)
        
        # Mock QAAnalytics response
        self.mock_qa_analytics = QAAnalytics(
            question="What is the capital of France?",
            answer="The capital of France is Paris.",
            thought="This is a straightforward geography question.",
            topic="Geography"
        )
        
        # Mock OpenAI response structure
        self.mock_openai_response = Mock()
        self.mock_openai_response.choices = [Mock()]
        self.mock_openai_response.choices[0].message = Mock()
        self.mock_openai_response.choices[0].message.parsed = self.mock_qa_analytics

    @patch('llm_app.client')
    def test_llm_response_success(self, mock_openai_client):
        """Test successful LLM response generation."""
        # Arrange
        mock_openai_client.beta.chat.completions.parse.return_value = self.mock_openai_response
        test_question = "What is the capital of France?"
        
        # Act
        result = llm_response(test_question)
        
        # Assert
        assert result == self.mock_openai_response
        mock_openai_client.beta.chat.completions.parse.assert_called_once_with(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Answer this question: {test_question}"}
            ],
            model="gpt-4o-mini",
            response_format=QAAnalytics
        )

    @patch('llm_app.client')
    def test_llm_response_with_different_question(self, mock_openai_client):
        """Test LLM response with a different question."""
        # Arrange
        mock_openai_client.beta.chat.completions.parse.return_value = self.mock_openai_response
        test_question = "What is 2 + 2?"
        
        # Act
        result = llm_response(test_question)
        
        # Assert
        assert result == self.mock_openai_response
        mock_openai_client.beta.chat.completions.parse.assert_called_once_with(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Answer this question: {test_question}"}
            ],
            model="gpt-4o-mini",
            response_format=QAAnalytics
        )

    def test_log_response(self):
        """Test the log_response function."""
        # Arrange
        mock_logger = Mock(spec=logging.Logger)
        
        # Act
        log_response(mock_logger, self.mock_qa_analytics)
        
        # Assert
        expected_calls = [
            (("Question: What is the capital of France?",), {}),
            (("Answer: The capital of France is Paris.",), {}),
            (("Thought: This is a straightforward geography question.",), {}),
            (("Topic: Geography",), {})
        ]
        
        assert mock_logger.info.call_count == 4
        actual_calls = [call for call in mock_logger.info.call_args_list]
        for i, expected_call in enumerate(expected_calls):
            assert actual_calls[i] == expected_call

    @patch('llm_app.log_response')
    @patch('llm_app.llm_response')
    @patch('llm_app.logger')
    def test_llm_qa_response_endpoint_success(self, mock_logger, mock_llm_response, mock_log_response):
        """Test successful API endpoint call."""
        # Arrange
        mock_llm_response.return_value = self.mock_openai_response
        test_request = {"question": "What is the capital of France?"}
        
        # Act
        response = self.client.post("/api/question", json=test_request)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["question"] == "What is the capital of France?"
        assert response_data["answer"] == "The capital of France is Paris."
        assert response_data["thought"] == "This is a straightforward geography question."
        assert response_data["topic"] == "Geography"
        
        # Verify function calls
        mock_logger.info.assert_any_call("Received question: What is the capital of France?")
        mock_llm_response.assert_called_once_with(question="What is the capital of France?")
        mock_log_response.assert_called_once_with(mock_logger, self.mock_qa_analytics)

    def test_llm_qa_response_endpoint_invalid_request(self):
        """Test API endpoint with invalid request data."""
        # Arrange
        invalid_request = {"invalid_field": "test"}
        
        # Act
        response = self.client.post("/api/question", json=invalid_request)
        
        # Assert
        assert response.status_code == 422  # Validation error

    def test_llm_qa_response_endpoint_empty_request(self):
        """Test API endpoint with empty request."""
        # Act
        response = self.client.post("/api/question", json={})
        
        # Assert
        assert response.status_code == 422  # Validation error

    @patch('llm_app.log_response')
    @patch('llm_app.llm_response')
    @patch('llm_app.logger')
    def test_llm_qa_response_endpoint_with_empty_question(self, mock_logger, mock_llm_response, mock_log_response):
        """Test API endpoint with empty question string."""
        # Arrange
        mock_llm_response.return_value = self.mock_openai_response
        test_request = {"question": ""}
        
        # Act
        response = self.client.post("/api/question", json=test_request)
        
        # Assert
        assert response.status_code == 200
        mock_llm_response.assert_called_once_with(question="")

    @patch('llm_app.log_response')
    @patch('llm_app.llm_response')
    @patch('llm_app.logger')
    def test_llm_qa_response_endpoint_logs_response_object(self, mock_logger, mock_llm_response, mock_log_response):
        """Test that the endpoint logs the raw response object."""
        # Arrange
        mock_llm_response.return_value = self.mock_openai_response
        test_request = {"question": "Test question?"}
        
        # Act
        response = self.client.post("/api/question", json=test_request)
        
        # Assert
        assert response.status_code == 200
        mock_logger.info.assert_any_call(f"Response: {self.mock_openai_response}")

    def test_app_instance(self):
        """Test that the FastAPI app instance is created properly."""
        assert app is not None
        assert hasattr(app, 'post')

    def test_main_block_structure(self):
        """Test the main block structure and imports."""
        # Test that all necessary modules and functions are available
        import llm_app
        assert hasattr(llm_app, 'uvicorn')
        assert hasattr(llm_app, 'FastAPI')
        assert hasattr(llm_app, 'logging')
        assert hasattr(llm_app, 'OpenAI')
        
        # Test that the app is properly configured
        assert llm_app.app is not None
        assert isinstance(llm_app.app, llm_app.FastAPI)
        
        # Note: The if __name__ == "__main__" block (line 58) is difficult to test
        # in unit tests as it's evaluated at import time. In practice, 97% coverage
        # is excellent and the main block is typically tested through integration tests.

    def test_fastapi_app_routes(self):
        """Test that the FastAPI app has the expected routes."""
        routes = [route.path for route in app.routes]
        assert "/api/question" in routes

    @patch('llm_app.client')
    def test_llm_response_handles_openai_exception(self, mock_openai_client):
        """Test that llm_response handles OpenAI API exceptions."""
        # Arrange
        from openai import OpenAIError
        mock_openai_client.beta.chat.completions.parse.side_effect = OpenAIError("API Error")
        
        # Act & Assert
        with pytest.raises(OpenAIError):
            llm_response("test question")

    def test_log_response_with_empty_strings(self):
        """Test log_response with empty string values in QAAnalytics."""
        # Arrange
        mock_logger = Mock(spec=logging.Logger)
        qa_analytics_with_empty = QAAnalytics(
            question="",
            answer="",
            thought="",
            topic=""
        )
        
        # Act
        log_response(mock_logger, qa_analytics_with_empty)
        
        # Assert
        assert mock_logger.info.call_count == 4
        mock_logger.info.assert_any_call("Question: ")
        mock_logger.info.assert_any_call("Answer: ")
        mock_logger.info.assert_any_call("Thought: ")
        mock_logger.info.assert_any_call("Topic: ")


if __name__ == "__main__":
    pytest.main([__file__])
