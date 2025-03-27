import os
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer, UserRegistrationSerializer, UserLoginSerializer
from utils.resume_parser import ResumeParser
from utils.llm_functions import GroqLLMFunctions
from django.contrib.auth import login as django_login, logout as django_logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            CandidateProfile.objects.create(user=user, name=serializer.validated_data.get('name'))
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def post(self, request):
        django_logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CandidateProfileViewSet(viewsets.ModelViewSet):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['POST'])
    def upload_resume(self, request):
        resume_file = request.FILES.get('resume')
        user = request.user

        if not resume_file:
            return Response(
                {"error": "No resume file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        os.makedirs('media/temp_resumes', exist_ok=True)
        temp_path = f"media/temp_resumes/{resume_file.name}"

        with open(temp_path, 'wb+') as destination:
            for chunk in resume_file.chunks():
                destination.write(chunk)

        try:
            resume_text = ResumeParser.extract_text(temp_path)
            extracted_urls = ResumeParser.extract_urls(resume_text, temp_path)
            logger.info(f"Extracted URLs: {extracted_urls}")
            llm_functions = GroqLLMFunctions()
            parsed_data = llm_functions.parse_resume(resume_text)
            logger.info(f"Parsed resume data: {parsed_data}")

            # If email is a list, extract first valid email address containing '@'
            if isinstance(parsed_data.get('email'), list):
                email_candidates = [item for item in parsed_data['email'] if '@' in item]
                parsed_data['email'] = email_candidates[0] if email_candidates else None

            # Ensure the email is valid (contains '@'); if not, clear it to allow fallback:
            if parsed_data.get('email') and '@' not in parsed_data.get('email'):
                parsed_data['email'] = None

            # Fall back to extracting mailto emails from clickable links if needed
            if not parsed_data.get('email'):
                mailto_emails = [url.replace('mailto:', '') for url in extracted_urls if url.startswith('mailto:')]
                if mailto_emails:
                    parsed_data['email'] = mailto_emails[0]

            if not parsed_data.get('email'):
                logger.error(f"Parsed resume data missing email: {parsed_data}")
                return Response(
                    {"error": "Parsed resume did not contain an email address."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                candidate = CandidateProfile.objects.get(user=user)
                # Update existing profile
                candidate.name = parsed_data.get('name', candidate.name) 
                candidate.email = parsed_data.get('email', candidate.email)
                candidate.parsed_skills = parsed_data.get('skills', [])
                candidate.parsed_education = parsed_data.get('education', [])
                candidate.parsed_work_experience = parsed_data.get('work_experience', [])
                candidate.resume_text = resume_text
                candidate.save()
                serializer = self.get_serializer(candidate)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CandidateProfile.DoesNotExist:
                # Create a new profile if it doesn't exist for this user
                candidate = CandidateProfile.objects.create(
                    user=user,
                    name=parsed_data.get('name'),
                    email=parsed_data.get('email'),
                    parsed_skills=parsed_data.get('skills', []),
                    parsed_education=parsed_data.get('education', []),
                    parsed_work_experience=parsed_data.get('work_experience', []),
                    resume_text=resume_text # Store the raw text
                )
                serializer = self.get_serializer(candidate)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error during resume upload")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    