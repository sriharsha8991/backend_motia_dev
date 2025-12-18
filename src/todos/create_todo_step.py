import uuid
from datetime import datetime, timezone

try:
    from pydantic import BaseModel, Field
    
    class TodoInput(BaseModel):
        title: str = Field(..., min_length=1, description="Todo title")
        description: str = Field(default="", description="Todo description")
        completed: bool = Field(default=False, description="Completion status")
    
    class TodoResponse(BaseModel):
        id: str
        title: str
        description: str
        completed: bool
        createdAt: str
        updatedAt: str
    
    class ErrorResponse(BaseModel):
        error: str
    
    body_schema = TodoInput.model_json_schema()
    response_schema = {
        201: TodoResponse.model_json_schema(),
        400: ErrorResponse.model_json_schema()
    }
except ImportError:
    body_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "description": {"type": "string"},
            "completed": {"type": "boolean"}
        },
        "required": ["title"]
    }
    response_schema = {
        201: {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "completed": {"type": "boolean"},
                "createdAt": {"type": "string"},
                "updatedAt": {"type": "string"}
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    }

config = {
    "name": "CreateTodo",
    "type": "api",
    "path": "/todos",
    "method": "POST",
    "description": "Create a new todo item",
    "emits": [],
    "flows": ["todo-management"],
    "bodySchema": body_schema,
    "responseSchema": response_schema
}

async def handler(req, context):
    try:
        body = req.get("body", {})
        title = body.get("title", "").strip()
        
        if not title:
            return {
                "status": 400,
                "body": {"error": "Title is required"}
            }
        
        # Create new todo
        todo_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        todo = {
            "id": todo_id,
            "title": title,
            "description": body.get("description", ""),
            "completed": body.get("completed", False),
            "createdAt": timestamp,
            "updatedAt": timestamp
        }
        
        # Store in state
        await context.state.set("todos", todo_id, todo)
        
        context.logger.info("Todo created", {"id": todo_id, "title": title})
        
        return {
            "status": 201,
            "body": todo
        }
        
    except Exception as e:
        context.logger.error("Failed to create todo", {"error": str(e)})
        return {
            "status": 400,
            "body": {"error": str(e)}
        }
