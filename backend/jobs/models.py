from django.db import models
import uuid

class JobPosting(models.Model):
    """Model to store job postings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, null=True, blank=True)

    # Parsed job details
    required_skills = models.JSONField(null=True, blank=True)

    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"