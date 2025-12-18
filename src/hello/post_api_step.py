# Optional: Using Pydantic for validation
try:
    from pydantic import BaseModel
    
    class NameInput(BaseModel):
        name: str
        
    
    class GreetingResponse(BaseModel):
        greeting: str
        message: str
    
    # Generate JSON schemas from Pydantic models
    input_schema = NameInput.model_json_schema()
    response_schema = {
        200: GreetingResponse.model_json_schema()
    }
except ImportError:
    # Without Pydantic, define JSON schemas manually
    input_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    response_schema = {
        200: {
            "type": "object",
            "properties": {
                "greeting": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["greeting", "message"]
        }
    }

config = {
    "name": "PostGreeting",
    "type": "api",
    "path": "/greet",
    "method": "POST",
    "description": "Receives name and returns personalized greeting",
    "emits": ["log-greeting"],
    "flows": ["hello-world-flow"],
    "bodySchema": input_schema,
    "responseSchema": response_schema
}

async def handler(req, context):
    # Extract name from request body
    body = req.get("body", {})
    name = body.get("name", "stranger")
    
    context.logger.info("Greeting request received", {
        "name": name
    })
    
    # Emit event for background logging (optional)
    await context.emit(
        {
            "topic": "log-greeting",
            "data": {
                "name": name
            }
        }
    )
    
    # API steps MUST return an HTTP response
    return {
        "status": 200,
        "body": {
            "greeting": "hi there how are you",
            "message": f"telling nice meeting {name}"
        }
    }