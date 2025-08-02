# FastAPI MCP API - Multi-Tool Collection

## Overview

This project is a **FastAPI-based Model Context Protocol (MCP) server** that exposes a collection of useful utility tools through both REST API endpoints and MCP protocol. The application leverages the `fastapi-mcp` library to automatically transform FastAPI endpoints into MCP tools that can be consumed by AI assistants, coding tools, and other MCP-compatible clients.

## What is MCP (Model Context Protocol)?

The Model Context Protocol is a standardized way for AI applications to connect to external data sources and tools. It allows AI assistants like Claude, ChatGPT, or other language models to access and interact with external services, databases, and APIs in a secure and structured manner.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   FastAPI App    │    │   Utility       │
│  (AI Assistant) │◄──►│  with MCP Layer  │◄──►│   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

The application serves dual purposes:
1. **REST API Server**: Traditional HTTP endpoints accessible via standard web requests
2. **MCP Server**: Tools exposed through the Model Context Protocol for AI integration

## Features

### 🏥 BMI Calculator
- **Endpoint**: `GET /bmi`
- **Purpose**: Calculate Body Mass Index from weight and height
- **Parameters**:
  - `weight_kg` (float): Weight in kilograms
  - `height_m` (float): Height in meters
- **Returns**: BMI value, category (Underweight/Normal/Overweight/Obese), and input values

### 🌡️ Temperature Converter
- **Endpoint**: `GET /temperature`
- **Purpose**: Convert temperatures between Celsius and Fahrenheit
- **Parameters**:
  - `temperature` (float): Temperature value to convert
  - `from_unit` (str, optional): Source unit ("celsius" or "fahrenheit", defaults to "celsius")
  - `to_unit` (str, optional): Target unit ("celsius" or "fahrenheit", defaults to "fahrenheit")
- **Returns**: Original and converted temperature values with units

### 📅 Age Calculator
- **Endpoint**: `GET /age`
- **Purpose**: Calculate current age from birth year
- **Parameters**:
  - `birth_year` (int): Year of birth
- **Returns**: Birth year, current year, and calculated age

### 👋 Multilingual Greeting Generator
- **Endpoint**: `POST /greeting`
- **Purpose**: Generate personalized greetings in multiple languages
- **Parameters** (JSON body):
  - `name` (str): Person's name
  - `language` (str, optional): Language for greeting (defaults to "english")
- **Supported Languages**: English, Spanish, French, German, Italian
- **Returns**: Personalized greeting with language information

## Technical Stack

- **Framework**: FastAPI (Python web framework)
- **MCP Integration**: `fastapi-mcp` library
- **Data Validation**: Pydantic models
- **Server**: Uvicorn ASGI server
- **Testing**: Custom HTTP client using `requests`

## Project Structure

```
fastapi-mcp-api/
├── app.py              # Main application with FastAPI endpoints and MCP setup
├── test_client.py      # Test client for API validation
└── README.md          # This documentation file
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
```bash
pip install fastapi uvicorn fastapi-mcp pydantic requests
```

### Running the Application

1. **Start the server**:
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:8888` with auto-reload enabled.

2. **Access the API documentation**:
   - Interactive docs: `http://localhost:8888/docs`
   - ReDoc: `http://localhost:8888/redoc`

## Usage Examples

### REST API Usage

#### BMI Calculation
```bash
curl "http://localhost:8888/bmi?weight_kg=70&height_m=1.75"
```

#### Temperature Conversion
```bash
curl "http://localhost:8888/temperature?temperature=25&from_unit=celsius&to_unit=fahrenheit"
```

#### Age Calculation
```bash
curl "http://localhost:8888/age?birth_year=1990"
```

#### Greeting Generation
```bash
curl -X POST "http://localhost:8888/greeting" \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "language": "spanish"}'
```

### MCP Tool Usage

When connected as an MCP server, these endpoints become available as tools:
- `calculate_bmi`: BMI calculation tool
- `convert_temperature`: Temperature conversion tool
- `calculate_age`: Age calculation tool
- `create_greeting`: Greeting generation tool

## Testing

Run the test client to validate all endpoints:

```bash
python test_client.py
```

The test client demonstrates usage of the greeting endpoint with various languages and edge cases.

## MCP Integration Details

### How It Works

1. **FastAPI Endpoints**: Standard REST API endpoints are defined using FastAPI decorators
2. **MCP Wrapper**: The `FastApiMCP` class wraps the FastAPI application
3. **Automatic Tool Generation**: Each endpoint is automatically converted to an MCP tool
4. **Metadata Preservation**: Operation IDs, summaries, and docstrings become tool descriptions

### MCP Server Configuration

```python
# Initialize MCP with the FastAPI app
mcp = FastApiMCP(
    app, 
    name="Multi-Tool MCP", 
    description="A collection of useful tools including BMI calculator, temperature converter, age calculator, and greeting generator"
)

# Mount the MCP tools
mcp.mount()
```

### Tool Descriptions

Each FastAPI endpoint includes:
- `operation_id`: Unique identifier for the MCP tool
- `summary`: Brief description of the tool's purpose
- `docstring`: Detailed explanation of functionality

## Error Handling

The application includes robust error handling:
- **Temperature Converter**: Validates supported units and provides error messages
- **Greeting Generator**: Falls back to English for unsupported languages
- **Input Validation**: Pydantic models ensure type safety and validation

## Extensibility

To add new tools:

1. **Create a FastAPI endpoint**:
   ```python
   @app.get("/new-tool", operation_id="new_tool", summary="Description")
   def new_tool(param: str):
       """Detailed description of the tool."""
       return {"result": "processed"}
   ```

2. **The tool automatically becomes available** through MCP without additional configuration

## Use Cases

### For Developers
- Quick utility calculations during development
- Template for building MCP-enabled services
- Learning FastAPI and MCP integration

### For AI Applications
- Providing AI assistants with calculation capabilities
- Extending language models with utility functions
- Building conversational interfaces with practical tools

### For Integration
- Microservice for common calculations
- Component in larger AI workflows
- Educational tool for MCP protocol understanding

## Performance Considerations

- **Lightweight Operations**: All tools perform simple calculations with minimal computational overhead
- **Stateless Design**: No database or persistent storage requirements
- **Auto-reload**: Development mode includes automatic reloading for rapid iteration
- **Async Support**: FastAPI's async capabilities enable high concurrent request handling

## Security Notes

- **Input Validation**: All inputs are validated using Pydantic models
- **No External Dependencies**: Tools don't make external API calls or access sensitive data
- **Stateless Operations**: No user data persistence or session management

## Future Enhancements

Potential expansions for this project:
- Additional calculation tools (finance, geometry, statistics)
- Database integration for persistent data
- Authentication and rate limiting
- WebSocket support for real-time interactions
- Docker containerization
- Comprehensive test suite with pytest
- Logging and monitoring integration

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Add new tools following the existing pattern
4. Include appropriate tests
5. Submit a pull request

## License

This project is designed as an educational and practical example of FastAPI and MCP integration. Feel free to use and modify according to your needs. 