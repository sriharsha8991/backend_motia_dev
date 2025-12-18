"""
Generate Job Description Event Step
Background processor that generates job descriptions using Gemini AI
"""
from datetime import datetime, timezone
import sys
import os

# Add src to path for service imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.gemini_service import create_gemini_service
from services.file_service import create_file_service

try:
    from pydantic import BaseModel
    from typing import Optional
    
    class GenerateJobInput(BaseModel):
        job_id: str
        role: str
        description: str
        yoe: int
        comp: Optional[str] = None
    
    input_schema = GenerateJobInput.model_json_schema()
    
except ImportError:
    input_schema = {
        "type": "object",
        "properties": {
            "job_id": {"type": "string"},
            "role": {"type": "string"},
            "description": {"type": "string"},
            "yoe": {"type": "integer"},
            "comp": {"type": "string"}
        },
        "required": ["job_id", "role", "description", "yoe"]
    }


config = {
    "name": "GenerateJobDescription",
    "type": "event",
    "description": "Generate job description using Gemini AI and save to file",
    "subscribes": ["generate-job-description"],
    "emits": [],
    "flows": ["job-generation"],
    "input": input_schema
}


async def handler(input_data, context):
    """
    Handler for generating job descriptions
    Uses Gemini service for AI generation and File service for persistence
    """
    job_id = input_data.get("job_id")
    role = input_data.get("role")
    description = input_data.get("description")
    yoe = input_data.get("yoe")
    comp = input_data.get("comp")
    
    context.logger.info("Starting job description generation", {
        "job_id": job_id,
        "role": role
    })
    
    try:
        # Get job from state
        job = await context.state.get("jobs", job_id)
        
        if not job:
            context.logger.error("Job not found in state", {"job_id": job_id})
            return
        
        # Update status to processing
        job["status"] = "processing"
        job["updated_at"] = datetime.now(timezone.utc).isoformat()
        await context.state.set("jobs", job_id, job)
        
        # Generate job description using Gemini
        context.logger.info("Calling Gemini API", {"job_id": job_id})
        gemini_service = create_gemini_service()
        
        generated_content = await gemini_service.generate_job_description(
            role=role,
            description=description,
            yoe=yoe,
            comp=comp
        )
        
        context.logger.info("Job description generated", {
            "job_id": job_id,
            "content_length": len(generated_content)
        })
        
        # Save to file system
        file_service = create_file_service()
        file_path = await file_service.save_job_description(job_id, generated_content)
        
        context.logger.info("Job description saved to file", {
            "job_id": job_id,
            "file_path": file_path
        })
        
        # Update job status to completed
        job["status"] = "completed"
        job["file_path"] = file_path
        job["updated_at"] = datetime.now(timezone.utc).isoformat()
        job["error"] = None
        await context.state.set("jobs", job_id, job)
        
        context.logger.info("Job description generation completed successfully", {
            "job_id": job_id,
            "role": role
        })
        
    except Exception as e:
        context.logger.error("Failed to generate job description", {
            "job_id": job_id,
            "error": str(e)
        })
        
        # Update job status to failed
        try:
            job = await context.state.get("jobs", job_id)
            if job:
                job["status"] = "failed"
                job["error"] = str(e)
                job["updated_at"] = datetime.now(timezone.utc).isoformat()
                await context.state.set("jobs", job_id, job)
        except Exception as state_error:
            context.logger.error("Failed to update job status to failed", {
                "job_id": job_id,
                "error": str(state_error)
            })
