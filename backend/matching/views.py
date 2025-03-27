from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JobMatch
from .serializers import JobMatchSerializer
from candidates.models import CandidateProfile
from jobs.models import JobPosting
from utils.llm_functions import GroqLLMFunctions

class JobMatchViewSet(viewsets.ModelViewSet):
    queryset = JobMatch.objects.all()
    serializer_class = JobMatchSerializer

    @action(detail=False, methods=['POST'])
    def match_candidate_to_job(self, request):
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')

        if not candidate_id or not job_id:
            return Response(
                {"error": "Both candidate_id and job_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            job = JobPosting.objects.get(id=job_id)

            # Prepare data for matching
            candidate_data = {
                'skills': candidate.parsed_skills,
                'education': candidate.parsed_education,
                'work_experience': candidate.parsed_work_experience
            }
            job_data = {
                'title': job.title,
                'company': job.company,
                'required_skills': job.required_skills
            }

            # Use Groq LLM for matching
            llm_functions = GroqLLMFunctions()
            match_result = llm_functions.match_candidate_to_job(candidate_data, job_data)

            # Generate cover letter
            cover_letter = llm_functions.generate_cover_letter(candidate_data, job_data)

            # Create or update job match
            job_match, created = JobMatch.objects.get_or_create(
                candidate=candidate,
                job=job,
                defaults={
                    'match_score': match_result.get('match_score', 0),
                    'missing_skills': match_result.get('missing_skills', []),
                    'match_summary': match_result.get('summary', ''),
                    'cover_letter': cover_letter
                }
            )

            # Return only the desired fields
            return Response({
                "match_score": job_match.match_score,
                "missing_skills": job_match.missing_skills,
                "summary": job_match.match_summary
            }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

        except CandidateProfile.DoesNotExist:
            return Response({"error": f"Candidate with id {candidate_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except JobPosting.DoesNotExist:
            return Response({"error": f"Job with id {job_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)