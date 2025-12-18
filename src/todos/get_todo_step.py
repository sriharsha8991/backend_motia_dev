config = {
    "name": "GetTodo",
    "type": "api",
    "path": "/todos/:id",
    "method": "GET",
    "description": "Get a single todo item by ID",
    "emits": [],
    "flows": ["todo-management"],
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
        }
    }
}

async def handler(req, context):
    try:
        path_params = req.get("pathParams", {})
        todo_id = path_params.get("id")
        
        if not todo_id:
            return {
                "status": 404,
                "body": {"error": "Todo ID is required"}
            }
        
        # Get todo from state
        todo = await context.state.get("todos", todo_id)
        
        if not todo:
            context.logger.warn("Todo not found", {"id": todo_id})
            return {
                "status": 404,
                "body": {"error": f"Todo with id {todo_id} not found"}
            }
        
        context.logger.info("Todo retrieved", {"id": todo_id})
        
        return {
            "status": 200,
            "body": todo
        }
        
    except Exception as e:
        context.logger.error("Failed to get todo", {"error": str(e)})
        return {
            "status": 500,
            "body": {"error": str(e)}
        }
