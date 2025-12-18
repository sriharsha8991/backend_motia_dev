"""
List Jobs API Step
GET /jobs - Lists all jobs with their status
"""


config = {
    "name": "ListJobs",
    "type": "api",
    "path": "/jobs",
    "method": "GET",
    "description": "List all jobs with their current status",
    "emits": [],
    "flows": ["job-generation"],
    "responseSchema": {
        200: {
            "type": "object",
            "properties": {
                "jobs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "job_id": {"type": "string"},
                            "role": {"type": "string"},
                            "status": {"type": "string"},
                            "created_at": {"type": "string"},
                            "updated_at": {"type": "string"}
                        }
                    }
                },
                "count": {"type": "integer"},
                "summary": {
                    "type": "object",
                    "properties": {
                        "pending": {"type": "integer"},
                        "processing": {"type": "integer"},
                        "completed": {"type": "integer"},
                        "failed": {"type": "integer"}
                    }
                }
            }
        }
    }
}


async def handler(req, context):
    """
    Handler for listing all jobs
    Returns summary with status counts
    """
    try:
        # Get all job keys from state
        job_keys = await context.state.keys("jobs")
        
        jobs = []
        status_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        # Fetch all jobs and build summary
        for key in job_keys:
            job = await context.state.get("jobs", key)
            if job:
                # Add summary info for list view
                jobs.append({
                    "job_id": job.get("job_id"),
                    "role": job.get("role"),
                    "description": job.get("description"),
                    "yoe": job.get("yoe"),
                    "status": job.get("status"),
                    "created_at": job.get("created_at"),
                    "updated_at": job.get("updated_at"),
                    "error": job.get("error")
                })
                
                # Count by status
                status = job.get("status", "unknown")
                if status in status_counts:
                    status_counts[status] += 1
        
        # Sort by creation date (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        context.logger.info("Retrieved jobs list", {
            "total_count": len(jobs),
            "summary": status_counts
        })
        
        return {
            "status": 200,
            "body": {
                "jobs": jobs,
                "count": len(jobs),
                "summary": status_counts
            }
        }
        
    except Exception as e:
        context.logger.error("Failed to list jobs", {"error": str(e)})
        return {
            "status": 500,
            "body": {"error": str(e)}
        }
