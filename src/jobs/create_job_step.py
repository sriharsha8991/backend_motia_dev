"""
Create Job API Step
POST /jobs - Creates a new job and triggers description generation
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

try:
    from pydantic import BaseModel, Field, field_validator
    
    class JobInput(BaseModel):
        role: str = Field(..., min_length=1, description="Job title/role")
        description: str = Field(..., min_length=100, max_length=150, description="Brief job description")
        yoe: int = Field(..., ge=0, description="Years of experience required")
        comp: Optional[str] = Field(None, description="Optional compensation details")
        
        @field_validator('role')
        @classmethod
        def validate_role(cls, v):
            if not v or not v.strip():
                raise ValueError('Role cannot be empty')
            return v.strip()
        
        @field_validator('description')
        @classmethod
        def validate_description(cls, v):
            if len(v) < 100:
                raise ValueError('Description must be at least 100 characters')
            if len(v) > 150:
                raise ValueError('Description must not exceed 150 characters')
            return v.strip()
    
    class JobResponse(BaseModel):
        job_id: str
        role: str
        description: str
        yoe: int
        comp: Optional[str]
        status: str
        message: str
        created_at: str
    
    class ErrorResponse(BaseModel):
        error: str
        details: Optional[dict] = None
    
    body_schema = JobInput.model_json_schema()
    response_schema = {
        201: JobResponse.model_json_schema(),
        400: ErrorResponse.model_json_schema()
    }
    
except ImportError:
    # Fallback without Pydantic
    body_schema = {
        "type": "object",
        "properties": {
            "role": {"type": "string", "minLength": 1},
            "description": {"type": "string", "minLength": 100, "maxLength": 150},
            "yoe": {"type": "integer", "minimum": 0},
            "comp": {"type": "string"}
        },
        "required": ["role", "description", "yoe"]
    }
    response_schema = {
        201: {
            "type": "object",
            "properties": {
                "job_id": {"type": "string"},
                "role": {"type": "string"},
                "status": {"type": "string"},
                "message": {"type": "string"},
                "created_at": {"type": "string"}
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
    "name": "CreateJob",
    "type": "api",
    "path": "/jobs",
    "method": "POST",
    "description": "Create a new job and trigger description generation",
    "emits": ["generate-job-description"],
    "flows": ["job-generation"],
    "bodySchema": body_schema,
    "responseSchema": response_schema
}


async def handler(req, context):
    """
    Handler for creating a new job
    Validates input, stores in state, emits event for background generation
    """
    try:
        body = req.get("body", {})
        
        # Validate required fields
        role = body.get("role", "").strip()
        description = body.get("description", "").strip()
        yoe = body.get("yoe")
        comp = body.get("comp")
        
        # Manual validation
        if not role:
            return {
                "status": 400,
                "body": {"error": "Role is required"}
            }
        
        if not description:
            return {
                "status": 400,
                "body": {"error": "Description is required"}
            }
        
        if len(description) < 100 or len(description) > 150:
            return {
                "status": 400,
                "body": {
                    "error": f"Description must be 100-150 characters (current: {len(description)})"
                }
            }
        
        if yoe is None or not isinstance(yoe, int) or yoe < 0:
            return {
                "status": 400,
                "body": {"error": "Valid years of experience (yoe) is required (must be >= 0)"}
            }
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create job object
        job = {
            "job_id": job_id,
            "role": role,
            "description": description,
            "yoe": yoe,
            "comp": comp,
            "status": "pending",
            "created_at": timestamp,
            "updated_at": timestamp,
            "file_path": None,
            "error": None
        }
        
        # Store in state (job tracking)
        await context.state.set("jobs", job_id, job)
        
        context.logger.info("Job created, triggering generation", {
            "job_id": job_id,
            "role": role,
            "yoe": yoe
        })
        
        # Emit event for background processing
        await context.emit({
            "topic": "generate-job-description",
            "data": {
                "job_id": job_id,
                "role": role,
                "description": description,
                "yoe": yoe,
                "comp": comp
            }
        })
        
        # Return immediate response
        return {
            "status": 201,
            "body": {
                "job_id": job_id,
                "role": role,
                "description": description,
                "yoe": yoe,
                "comp": comp,
                "status": "pending",
                "message": "Job created successfully. Description generation in progress.",
                "created_at": timestamp
            }
        }
        
    except Exception as e:
        context.logger.error("Failed to create job", {"error": str(e)})
        return {
            "status": 400,
            "body": {
                "error": "Failed to create job",
                "details": {"message": str(e)}
            }
        }
