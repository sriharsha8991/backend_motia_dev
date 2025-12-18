"""
Gemini AI Service for generating job descriptions
Reusable service for any AI text generation needs
"""
import os
from typing import Optional
import asyncio
from google import genai


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-exp"
    
    async def generate_job_description(
        self,
        role: str,
        description: str,
        yoe: int,
        comp: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive job description using Gemini AI
        
        Args:
            role: Job title/role
            description: Brief job description (100-150 chars)
            yoe: Years of experience required
            comp: Optional compensation details
            
        Returns:
            Generated job description as string
        """
        prompt = self._build_prompt(role, description, yoe, comp)
        
        try:
            # Generate content using Gemini Client API
            # Run in executor to make it async-compatible
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.95,
                        "max_output_tokens": 1024,
                    }
                )
            )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Failed to generate job description: {str(e)}")
    
    def _build_prompt(
        self, 
        role: str, 
        description: str, 
        yoe: int, 
        comp: Optional[str]
    ) -> str:
        """Build structured prompt for Gemini"""
        prompt = f"""Generate a comprehensive, professional job description based on the following details:

Role: {role}
Brief Description: {description}
Required Years of Experience: {yoe} years
"""
        
        if comp:
            prompt += f"Compensation: {comp}\n"
        
        prompt += """
Please generate a detailed job description including:
1. Role Overview (2-3 sentences)
2. Key Responsibilities (5-7 bullet points)
3. Required Qualifications (3-5 bullet points)
4. Preferred Qualifications (2-3 bullet points)
5. What We Offer (3-4 bullet points)

Make it professional, engaging, and suitable for posting on job boards.
"""
        return prompt


# Factory function for easy instantiation
def create_gemini_service() -> GeminiService:
    """Create and return a configured GeminiService instance"""
    return GeminiService()
