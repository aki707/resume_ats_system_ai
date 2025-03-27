from django.db import models
from django.contrib.auth.models import User
import uuid

class CandidateProfile(models.Model):
    """Model to store candidate resume and profile information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True) 
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Parsed resume details
    parsed_skills = models.JSONField(null=True, blank=True)
    parsed_education = models.JSONField(null=True, blank=True)
    parsed_work_experience = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name if self.name else f"Candidate {self.id}"



