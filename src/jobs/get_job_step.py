"""
Get Job API Step
GET /jobs/:id - Retrieves job status and content
"""
import sys
import os

# Add src to path for service imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.file_service import create_file_service


config = {
    "name": "GetJob",
    "type": "api",
    "path": "/jobs/:id",
    "method": "GET",
    "description": "Get job status and description content",
    "emits": [],
    "flows": ["job-generation"],
    "responseSchema": {
        200: {
            "type": "object",
            "properties": {
                "job_id": {"type": "string"},
                "role": {"type": "string"},
                "description": {"type": "string"},
                "yoe": {"type": "integer"},
                "comp": {"type": "string"},
                "status": {"type": "string"},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
                "file_path": {"type": "string"},
                "content": {"type": "string"},
                "error": {"type": "string"}
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
    """
    Handler for retrieving job details
    Returns job metadata and generated content (if available)
    """
    try:
        path_params = req.get("pathParams", {})
        job_id = path_params.get("id")
        
        if not job_id:
            return {
                "status": 404,
                "body": {"error": "Job ID is required"}
            }
        
        # Get job from state
        job = await context.state.get("jobs", job_id)
        
        if not job:
            context.logger.warn("Job not found", {"job_id": job_id})
            return {
                "status": 404,
                "body": {"error": f"Job with id {job_id} not found"}
            }
        
        context.logger.info("Job retrieved", {
            "job_id": job_id,
            "status": job.get("status")
        })
        
        # If job is completed, include file content
        response_body = {**job}
        
        if job.get("status") == "completed" and job.get("file_path"):
            try:
                file_service = create_file_service()
                content = await file_service.read_job_description(job_id)
                response_body["content"] = content
            except Exception as e:
                context.logger.error("Failed to read job description file", {
                    "job_id": job_id,
                    "error": str(e)
                })
                response_body["content"] = None
        else:
            response_body["content"] = None
        
        return {
            "status": 200,
            "body": response_body
        }
        
    except Exception as e:
        context.logger.error("Failed to get job", {"error": str(e)})
        return {
            "status": 500,
            "body": {"error": str(e)}
        }
