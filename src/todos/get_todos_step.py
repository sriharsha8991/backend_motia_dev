config = {
    "name": "GetTodos",
    "type": "api",
    "path": "/todos",
    "method": "GET",
    "description": "Get all todo items",
    "emits": [],
    "flows": ["todo-management"],
    "responseSchema": {
        200: {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "completed": {"type": "boolean"},
                            "createdAt": {"type": "string"},
                            "updatedAt": {"type": "string"}
                        }
                    }
                },
                "count": {"type": "number"}
            }
        }
    }
}

async def handler(req, context):
    try:
        # Get all todos from state
        # Note: state.keys() returns all keys in the "todos" group
        todo_keys = await context.state.keys("todos")
        
        todos = []
        for key in todo_keys:
            todo = await context.state.get("todos", key)
            if todo:
                todos.append(todo)
        
        # Sort by creation date (newest first)
        todos.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        
        context.logger.info("Retrieved todos", {"count": len(todos)})
        
        return {
            "status": 200,
            "body": {
                "todos": todos,
                "count": len(todos)
            }
        }
        
    except Exception as e:
        context.logger.error("Failed to get todos", {"error": str(e)})
        return {
            "status": 500,
            "body": {"error": str(e)}
        }
