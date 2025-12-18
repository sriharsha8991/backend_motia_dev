from datetime import datetime, timezone

try:
    from pydantic import BaseModel, Field
    from typing import Optional
    
    class TodoUpdateInput(BaseModel):
        title: Optional[str] = Field(None, min_length=1, description="Todo title")
        description: Optional[str] = Field(None, description="Todo description")
        completed: Optional[bool] = Field(None, description="Completion status")
    
    body_schema = TodoUpdateInput.model_json_schema()
except ImportError:
    body_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "description": {"type": "string"},
            "completed": {"type": "boolean"}
        }
    }

config = {
    "name": "UpdateTodo",
    "type": "api",
    "path": "/todos/:id",
    "method": "PUT",
    "description": "Update a todo item",
    "emits": [],
    "flows": ["todo-management"],
    "bodySchema": body_schema,
    "responseSchema": {
        200: {
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
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    }
}

async def handler(req, context):
    try:
        path_params = req.get("pathParams", {})
        todo_id = path_params.get("id")
        
        if not todo_id:
            return {
                "status": 400,
                "body": {"error": "Todo ID is required"}
            }
        
        # Get existing todo
        todo = await context.state.get("todos", todo_id)
        
        if not todo:
            context.logger.warn("Todo not found for update", {"id": todo_id})
            return {
                "status": 404,
                "body": {"error": f"Todo with id {todo_id} not found"}
            }
        
        # Update fields
        body = req.get("body", {})
        if "title" in body:
            todo["title"] = body["title"]
        if "description" in body:
            todo["description"] = body["description"]
        if "completed" in body:
            todo["completed"] = body["completed"]
        
        todo["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        # Save updated todo
        await context.state.set("todos", todo_id, todo)
        
        context.logger.info("Todo updated", {"id": todo_id})
        
        return {
            "status": 200,
            "body": todo
        }
        
    except Exception as e:
        context.logger.error("Failed to update todo", {"error": str(e)})
        return {
            "status": 400,
            "body": {"error": str(e)}
        }
