from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

@app.get("/bmi", operation_id="calculate_bmi", summary="this tool is used to calculate bmi based on weigth and height"))
def calculate_bmi(weight_kg: float, height_m: float):
    return {"bmi": weight_kg / (height_m ** 2)}

mcp = FastApiMCP(app, name="BMI MCP", description="Simple application to calculate BMI")
mcp.mount()