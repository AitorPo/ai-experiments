from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

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

@app.get("/age", operation_id="calculate_age", summary="Calculate age from birth year")
def calculate_age(birth_year: int):
    """Calculate current age from birth year."""
    from datetime import datetime
    current_year = datetime.now().year
    age = current_year - birth_year
    
    return {
        "birth_year": birth_year,
        "current_year": current_year,
        "age": age
    }

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

# Initialize MCP with the FastAPI app
mcp = FastApiMCP(app, name="Multi-Tool MCP", description="A collection of useful tools including BMI calculator, temperature converter, age calculator, and greeting generator")

# Mount the MCP tools
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8888, reload=True)