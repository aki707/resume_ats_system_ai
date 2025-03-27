from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JobPosting
from .serializers import JobPostingSerializer
from utils.llm_functions import GroqLLMFunctions
import logging

logger = logging.getLogger(__name__)

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

    @action(detail=False, methods=['POST'])
    def create_from_description(self, request):
        job_description = request.data.get('job_description')
        if not job_description:
            return Response(
                {"error": "Job description is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        llm_functions = GroqLLMFunctions()
        parsed_data = llm_functions.parse_job_posting(job_description)

        if not parsed_data.get('title') or not parsed_data.get('company'):
            return Response(
                {"error": "Parsed job data missing required fields (title or company)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        job_posting = JobPosting.objects.create(
            title=parsed_data.get('title'),
            company=parsed_data.get('company'),
            description=job_description,
            location=parsed_data.get('location'),
            required_skills=parsed_data.get('required_skills', [])
        )

        serializer = self.get_serializer(job_posting)
        return Response(serializer.data, status=status.HTTP_201_CREATED)