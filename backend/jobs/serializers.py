from rest_framework import serializers
from .models import JobPosting

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'company', 'description',
            'location', 'required_skills',
            'posted_date', 'closing_date'
        ]
        read_only_fields = ['id', 'posted_date']