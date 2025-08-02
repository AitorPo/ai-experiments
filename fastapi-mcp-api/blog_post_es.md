# Construyendo APIs Listas para IA: Cómo Transformar Endpoints de FastAPI en Herramientas MCP

*Cerrando la brecha entre APIs REST tradicionales e integración de herramientas de IA*

## Introducción

A medida que los asistentes de IA se vuelven cada vez más sofisticados, la necesidad de integración fluida entre sistemas de IA y servicios backend nunca ha sido más crítica. Aquí entra el **Protocolo de Contexto de Modelo (MCP)** - una forma estandarizada para que las aplicaciones de IA se conecten a fuentes de datos y herramientas externas. Pero aquí está el desafío: la mayoría de nosotros ya tenemos APIs REST perfectamente funcionales. ¿Necesitamos reconstruir todo desde cero?

La respuesta es un rotundo **no**. En este post, te mostraré cómo transformar tus aplicaciones FastAPI existentes en servidores de herramientas compatibles con MCP con solo unas pocas líneas de código, creando APIs que funcionan tanto como endpoints HTTP tradicionales como herramientas accesibles para IA.

## El Problema: Herramientas de IA vs. APIs REST

Las APIs REST tradicionales son excelentes para aplicaciones dirigidas por humanos, pero los asistentes de IA necesitan algo más estructurado. Necesitan:
- **Esquemas descubribles** para entender las funciones disponibles
- **Protocolos de comunicación estandarizados** para integración confiable
- **Metadatos ricos** sobre qué hace cada herramienta y cómo usarla

Aquí es donde MCP brilla. En lugar de forzar a los sistemas de IA a analizar especificaciones OpenAPI o hacer conjeturas educadas sobre tus endpoints, MCP proporciona un protocolo estandarizado que los asistentes de IA pueden entender nativamente.

## La Solución: Integración FastAPI + MCP

Déjame mostrarte cómo construí una API multi-herramienta que sirve tanto a clientes HTTP tradicionales como a asistentes de IA usando la librería `fastapi-mcp`.

### Estableciendo los Fundamentos

Primero, creemos una aplicación FastAPI básica con algunos endpoints de utilidad:

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

Observa los elementos clave que hacen esto compatible con MCP:
- **`operation_id`**: Se convierte en el identificador de herramienta en MCP
- **`summary`**: Proporciona una descripción breve para asistentes de IA
- **Docstring**: Ofrece explicación detallada de funcionalidad
- **Type hints**: Habilitan validación automática de parámetros

### Construyendo Herramientas Más Complejas

Agreguemos un conversor de temperatura con manejo de errores:

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

### Manejando Requests POST con Modelos Pydantic

Para estructuras de datos más complejas, podemos usar modelos Pydantic:

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

## La Magia: Habilitando la Integración MCP

Aquí es donde ocurre la magia. Con solo tres líneas de código, transformamos nuestra app FastAPI en un servidor MCP:

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

¡Eso es todo! Tus endpoints FastAPI ahora son accesibles tanto como endpoints de API REST como herramientas MCP.

## Probando tu API de Doble Propósito

### Uso Tradicional de API REST

Tu API funciona exactamente como antes:

```bash
# Cálculo de IMC
curl "http://localhost:8888/bmi?weight_kg=70&height_m=1.75"

# Conversión de temperatura
curl "http://localhost:8888/temperature?temperature=25&from_unit=celsius&to_unit=fahrenheit"

# Generación de saludo
curl -X POST "http://localhost:8888/greeting" \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "language": "spanish"}'
```

### Pruebas de Herramientas MCP

Puedes probar la funcionalidad MCP con un cliente Python simple:

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

## Integración de IA en el Mundo Real

Cuando se conecta a un asistente de IA, tus herramientas se vuelven disponibles con estas capacidades:

```python
# Los asistentes de IA ahora pueden llamar estas herramientas directamente:
# - calculate_bmi(weight_kg=70, height_m=1.75)
# - convert_temperature(temperature=25, from_unit="celsius", to_unit="fahrenheit")
# - calculate_age(birth_year=1990)
# - create_greeting(name="Alice", language="spanish")
```

El asistente de IA entiende las firmas de herramientas, tipos de parámetros y valores de retorno automáticamente, habilitando interacciones en lenguaje natural como:

- "Calcula mi IMC si peso 70kg y mido 1.75m"
- "Convierte 25 grados Celsius a Fahrenheit"
- "Crea un saludo en español para Carlos"

## Beneficios de la Arquitectura

Este enfoque te da varias ventajas clave:

### 1. **Compatibilidad Dual**
Tu API sirve tanto a clientes HTTP tradicionales como a asistentes de IA sin ningún overhead adicional.

### 2. **Cero Refactorización**
Los endpoints FastAPI existentes se convierten en herramientas MCP con cambios mínimos - solo agrega metadatos y monta la capa MCP.

### 3. **Seguridad de Tipos**
Los modelos Pydantic aseguran que tanto clientes REST como MCP obtengan validación adecuada y manejo de errores.

### 4. **Documentación Automática**
La documentación integrada de FastAPI (Swagger/OpenAPI) continúa funcionando junto con las descripciones de herramientas MCP.

## Consideraciones de Rendimiento y Escalabilidad

La integración MCP agrega overhead mínimo a tu aplicación FastAPI existente:

```python
# Características de rendimiento:
# - Registro de herramientas ligero
# - Operaciones sin estado (perfecto para escalado)
# - Soporte async para alta concurrencia
# - Sin requisitos adicionales de base de datos o almacenamiento
```

## Extendiendo el Sistema

Agregar nuevas herramientas es increíblemente directo:

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

La herramienta automáticamente se vuelve disponible tanto para clientes REST como MCP.

## Conclusión

La integración de FastAPI con MCP representa un paso significativo hacia adelante en la construcción de servicios backend listos para IA. En lugar de elegir entre APIs REST tradicionales e integración de herramientas de IA, podemos tener ambas con mínimo esfuerzo.

Este enfoque nos permite:
- **Aprovechar la experiencia existente en FastAPI** sin aprender frameworks completamente nuevos
- **Adoptar gradualmente la integración de IA** sin refactorización masiva
- **Mantener compatibilidad hacia atrás** con clientes existentes
- **Preparar nuestras APIs para el futuro** en el panorama de desarrollo impulsado por IA

A medida que los asistentes de IA se vuelven más prevalentes en los flujos de trabajo de desarrollo, tener APIs que puedan integrarse sin problemas con estas herramientas se volverá cada vez más valioso. La combinación FastAPI + MCP proporciona una solución elegante que cierra la brecha entre el desarrollo web tradicional y el ecosistema emergente de IA.

El código completo para este proyecto es mínimo pero poderoso - menos de 100 líneas de Python que demuestran cómo el desarrollo backend moderno puede abrazar la integración de IA sin sacrificar la robustez y familiaridad de frameworks establecidos.

Ya sea que estés construyendo herramientas internas, microservicios o APIs orientadas al cliente, considera cómo la integración MCP podría hacer tus servicios más accesibles al creciente ecosistema de herramientas de desarrollo potenciadas por IA. El futuro del desarrollo backend no se trata solo de servir a usuarios humanos - se trata de crear servicios que tanto humanos como asistentes de IA puedan usar efectivamente.

---

*¿Listo para empezar? El código fuente completo e instrucciones de configuración están disponibles en el repositorio del proyecto. ¡Pruébalo y ve qué fácil es hacer que tus aplicaciones FastAPI estén listas para IA!* 