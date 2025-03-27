import os
import json
import logging
from typing import Dict, Any, List

from groq import Groq
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GroqLLMFunctions:
    def __init__(self, api_key: str = None):
        """
        Initialize Groq LLM client.
        
        Args:
            api_key (str, optional): Groq API key. Defaults to environment variable.
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY in .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"  # Default model

    def _call_groq_api(
        self, 
        messages: List[Dict[str, str]], 
        response_format: Dict[str, str] = None
    ) -> str:
        """
        Generic method to call Groq API.
        
        Args:
            messages (List[Dict]): Conversation messages
            response_format (Dict, optional): Response format specification
        
        Returns:
            str: API response content
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=response_format or {"type": "text"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise

    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text into structured JSON.
        
        Args:
            resume_text (str): Resume text content
        
        Returns:
            Dict: Structured resume data
        """
        messages = [
            {
                "role": "system",
                "content": """
                You are an expert resume parser. Extract comprehensive, accurate information 
                from the given resume text. Return a structured JSON with the following keys:
                - name: Full name of the candidate
                - email: Email address
                - phone: Phone number
                - skills: List of professional skills
                - education: List of educational qualifications
                - work_experience: List of work experiences
                """
            },
            {
                "role": "user",
                "content": resume_text
            }
        ]

        try:
            result = self._call_groq_api(
                messages, 
                response_format={"type": "json_object"}
            )
            return json.loads(result)
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {
                "name": None,
                "email": None,
                "phone": None,
                "skills": [],
                "education": [],
                "work_experience": []
            }

    def parse_job_posting(self, job_text: str) -> Dict[str, Any]:
        """
        Parse job posting text into structured JSON.
        
        Args:
            job_text (str): Job posting text
        
        Returns:
            Dict: Structured job posting data
        """
        messages = [
            {
                "role": "system",
                "content": """
                You are an expert job posting parser. Extract comprehensive, accurate information 
                from the given job posting text. Return a structured JSON with the following keys:
                - title: Job title
                - company: Company name
                - location: Job location
                - required_skills: List of required skills
                - responsibilities: List of key responsibilities
                - qualifications: List of required qualifications
                """
            },
            {
                "role": "user",
                "content": job_text
            }
        ]

        try:
            result = self._call_groq_api(
                messages, 
                response_format={"type": "json_object"}
            )
            return json.loads(result)
        except Exception as e:
            logger.error(f"Job posting parsing failed: {e}")
            return {
                "title": None,
                "company": None,
                "location": None,
                "required_skills": [],
                "responsibilities": [],
                "qualifications": []
            }

    def match_candidate_to_job(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match candidate profile to job posting.

        Args:
            candidate_data (Dict): Candidate's profile data
            job_data (Dict): Job posting data

        Returns:
            Dict: Matching results with score, missing skills, etc.
        """
        messages = [
            {
                "role": "system",
                "content": """
                    You are an expert job matching algorithm. Analyze the candidate's profile
                    against the job requirements and provide a comprehensive match assessment.
                    """
            },
            {
                "role": "user",
                "content": f"""
                    Candidate Profile:
                    {json.dumps(candidate_data, indent=2)}

                    Job Requirements:
                    {json.dumps(job_data, indent=2)}

                    Provide a detailed match analysis in JSON format including:
                    - "match_score": (0-100, integer)
                    - "missing_skills": (list of strings)
                    - "summary": (string)
                    """
            }
        ]

        try:
            result = self._call_groq_api(
                messages,
                response_format={"type": "json_object"}
            )
            return json.loads(result)
        except Exception as e:
            logger.error(f"Job matching failed: {e}")
            return {
                "match_score": 0,
                "missing_skills": [],
                "summary": "Unable to perform match analysis"
            }