from rest_framework import serializers
from .models import JobMatch
from candidates.serializers import CandidateProfileSerializer
from jobs.serializers import JobPostingSerializer

class JobMatchSerializer(serializers.ModelSerializer):
    candidate = CandidateProfileSerializer(read_only=True)
    job = JobPostingSerializer(read_only=True)

    class Meta:
        model = JobMatch
        fields = [
            'id', 'candidate', 'job',
            'match_score', 'missing_skills',
            'match_summary', 'cover_letter'
        ]
        read_only_fields = ['id']