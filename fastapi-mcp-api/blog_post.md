# Building AI-Ready APIs: How to Transform FastAPI Endpoints into MCP Tools

*Bridging the gap between traditional REST APIs and AI tool integration*

## Introduction

As AI assistants become increasingly sophisticated, the need for seamless integration between AI systems and backend services has never been more critical. Enter the **Model Context Protocol (MCP)** - a standardized way for AI applications to connect to external tools and data sources. But here's the challenge: most of us already have perfectly functional REST APIs. Do we need to rebuild everything from scratch?

The answer is a resounding **no**. In this post, I'll show you how to transform your existing FastAPI applications into MCP-compatible tool servers with just a few lines of code, creating APIs that work both as traditional HTTP endpoints and as AI-accessible tools.

## The Problem: AI Tools vs. REST APIs

Traditional REST APIs are great for human-driven applications, but AI assistants need something more structured. They need:
- **Discoverable schemas** for understanding available functions
- **Standardized communication protocols** for reliable integration
- **Rich metadata** about what each tool does and how to use it

This is where MCP shines. Instead of forcing AI systems to parse OpenAPI specs or make educated guesses about your endpoints, MCP provides a standardized protocol that AI assistants can understand natively.

## The Solution: FastAPI + MCP Integration

Let me show you how I built a multi-tool API that serves both traditional HTTP clients and AI assistants using the `fastapi-mcp` library.

### Setting Up the Foundation

First, let's create a basic FastAPI application with some utility endpoints:

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

app = FastAPI()

@app.get("/bmi", operation_id="calculate_bmi", summary="Calculate BMI based on weight and height")
def calculate_bmi(weight_kg: float, height_m: float):
    """Calculate Body Mass Index (BMI) from weight in kg and height in meters."""
    bmi = weight_kg / (height_m ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "weight_kg": weight_kg,
        "height_m": height_m
    }
```

Notice the key elements that make this MCP-ready:
- **`operation_id`**: Becomes the tool identifier in MCP
- **`summary`**: Provides a brief description for AI assistants
- **Docstring**: Offers detailed functionality explanation
- **Type hints**: Enable automatic parameter validation

### Building More Complex Tools

Let's add a temperature converter with error handling:

```python
@app.get("/temperature", operation_id="convert_temperature", summary="Convert temperature between Celsius and Fahrenheit")
def convert_temperature(temperature: float, from_unit: str = "celsius", to_unit: str = "fahrenheit"):
    """Convert temperature between Celsius and Fahrenheit."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit == "celsius" and to_unit == "fahrenheit":
        converted = (temperature * 9/5) + 32
    elif from_unit == "fahrenheit" and to_unit == "celsius":
        converted = (temperature - 32) * 5/9
    elif from_unit == to_unit:
        converted = temperature
    else:
        return {"error": "Supported units are 'celsius' and 'fahrenheit'"}
    
    return {
        "original_temperature": temperature,
        "original_unit": from_unit,
        "converted_temperature": round(converted, 2),
        "converted_unit": to_unit
    }
```

### Handling POST Requests with Pydantic Models

For more complex data structures, we can use Pydantic models:

```python
from pydantic import BaseModel

class GreetingRequest(BaseModel):
    name: str
    language: str = "english"

@app.post("/greeting", operation_id="create_greeting", summary="Create a personalized greeting")
def create_greeting(request: GreetingRequest):
    """Create a personalized greeting in different languages."""
    greetings = {
        "english": f"Hello, {request.name}! Welcome!",
        "spanish": f"¡Hola, {request.name}! ¡Bienvenido!",
        "french": f"Bonjour, {request.name}! Bienvenue!",
        "german": f"Hallo, {request.name}! Willkommen!",
        "italian": f"Ciao, {request.name}! Benvenuto!"
    }
    
    language = request.language.lower()
    greeting = greetings.get(language, greetings["english"])
    
    return {
        "name": request.name,
        "language": language,
        "greeting": greeting,
        "available_languages": list(greetings.keys())
    }
```

## The Magic: Enabling MCP Integration

Here's where the magic happens. With just three lines of code, we transform our FastAPI app into an MCP server:

```python
# Initialize MCP with the FastAPI app
mcp = FastApiMCP(
    app, 
    name="Multi-Tool MCP", 
    description="A collection of useful tools including BMI calculator, temperature converter, age calculator, and greeting generator"
)

# Mount the MCP tools
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8888, reload=True)
```

That's it! Your FastAPI endpoints are now accessible both as REST API endpoints and as MCP tools.

## Testing Your Dual-Purpose API

### Traditional REST API Usage

Your API works exactly as before:

```bash
# BMI calculation
curl "http://localhost:8888/bmi?weight_kg=70&height_m=1.75"

# Temperature conversion
curl "http://localhost:8888/temperature?temperature=25&from_unit=celsius&to_unit=fahrenheit"

# Greeting generation
curl -X POST "http://localhost:8888/greeting" \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "language": "spanish"}'
```

### MCP Tool Testing

You can test the MCP functionality with a simple Python client:

```python
import requests
import json

def test_greeting_variations():
    """Test the multilingual greeting endpoint."""
    base_url = "http://localhost:8888"
    
    test_cases = [
        {"name": "Alice", "language": "english"},
        {"name": "Carlos", "language": "spanish"},
        {"name": "Marie", "language": "french"},
        {"name": "Klaus", "language": "german"},
        {"name": "Yuki", "language": "japanese"}  # Falls back to English
    ]
    
    for case in test_cases:
        response = requests.post(f"{base_url}/greeting", 
                               json=case,
                               headers={"Content-Type": "application/json"})
        print(f"Input: {case}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
```

## Real-World AI Integration

When connected to an AI assistant, your tools become available with these capabilities:

```python
# AI assistants can now call these tools directly:
# - calculate_bmi(weight_kg=70, height_m=1.75)
# - convert_temperature(temperature=25, from_unit="celsius", to_unit="fahrenheit")
# - calculate_age(birth_year=1990)
# - create_greeting(name="Alice", language="spanish")
```

The AI assistant understands the tool signatures, parameter types, and return values automatically, enabling natural language interactions like:

- "Calculate my BMI if I'm 70kg and 1.75m tall"
- "Convert 25 degrees Celsius to Fahrenheit"
- "Create a Spanish greeting for Carlos"

## Architecture Benefits

This approach gives you several key advantages:

### 1. **Dual Compatibility**
Your API serves both traditional HTTP clients and AI assistants without any additional overhead.

### 2. **Zero Refactoring**
Existing FastAPI endpoints become MCP tools with minimal changes - just add metadata and mount the MCP layer.

### 3. **Type Safety**
Pydantic models ensure both REST and MCP clients get proper validation and error handling.

### 4. **Automatic Documentation**
FastAPI's built-in documentation (Swagger/OpenAPI) continues to work alongside MCP tool descriptions.

## Performance and Scalability Considerations

The MCP integration adds minimal overhead to your existing FastAPI application:

```python
# Performance characteristics:
# - Lightweight tool registration
# - Stateless operations (perfect for scaling)
# - Async support for high concurrency
# - No additional database or storage requirements
```

## Extending the System

Adding new tools is incredibly straightforward:

```python
@app.get("/finance/compound", operation_id="calculate_compound_interest", 
         summary="Calculate compound interest")
def calculate_compound_interest(principal: float, rate: float, 
                              time: int, frequency: int = 12):
    """Calculate compound interest given principal, rate, time, and frequency."""
    amount = principal * (1 + rate/frequency) ** (frequency * time)
    interest = amount - principal
    
    return {
        "principal": principal,
        "interest_rate": rate,
        "time_years": time,
        "compound_frequency": frequency,
        "final_amount": round(amount, 2),
        "interest_earned": round(interest, 2)
    }
```

The tool automatically becomes available to both REST and MCP clients.

## Conclusion

The integration of FastAPI with MCP represents a significant step forward in building AI-ready backend services. Instead of choosing between traditional REST APIs and AI tool integration, we can have both with minimal effort.

This approach allows us to:
- **Leverage existing FastAPI expertise** without learning entirely new frameworks
- **Gradually adopt AI integration** without massive refactoring
- **Maintain backward compatibility** with existing clients
- **Future-proof our APIs** for the AI-driven development landscape

As AI assistants become more prevalent in development workflows, having APIs that can seamlessly integrate with these tools will become increasingly valuable. The FastAPI + MCP combination provides an elegant solution that bridges the gap between traditional web development and the emerging AI ecosystem.

The full code for this project is minimal yet powerful - under 100 lines of Python that demonstrate how modern backend development can embrace AI integration without sacrificing the robustness and familiarity of established frameworks.

Whether you're building internal tools, microservices, or customer-facing APIs, consider how MCP integration could make your services more accessible to the growing ecosystem of AI-powered development tools. The future of backend development is not just about serving human users - it's about creating services that both humans and AI assistants can use effectively.

---

*Ready to get started? The complete source code and setup instructions are available in the project repository. Try it out and see how easy it is to make your FastAPI applications AI-ready!* 