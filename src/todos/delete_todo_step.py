config = {
    "name": "DeleteTodo",
    "type": "api",
    "path": "/todos/:id",
    "method": "DELETE",
    "description": "Delete a todo item",
    "emits": [],
    "flows": ["todo-management"],
    "responseSchema": {
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "id": {"type": "string"}
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
        
        # Check if todo exists
        todo = await context.state.get("todos", todo_id)
        
        if not todo:
            context.logger.warn("Todo not found for deletion", {"id": todo_id})
            return {
                "status": 404,
                "body": {"error": f"Todo with id {todo_id} not found"}
            }
        
        # Delete from state
        await context.state.delete("todos", todo_id)
        
        context.logger.info("Todo deleted", {"id": todo_id})
        
        return {
            "status": 200,
            "body": {
                "message": "Todo deleted successfully",
                "id": todo_id
            }
        }
        
    except Exception as e:
        context.logger.error("Failed to delete todo", {"error": str(e)})
        return {
            "status": 500,
            "body": {"error": str(e)}
        }
