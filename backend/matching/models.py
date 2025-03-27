from django.db import models
from candidates.models import CandidateProfile
from jobs.models import JobPosting
import uuid

class JobMatch(models.Model):
    """Model to store job matching results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='candidate_matches')

    # Matching details
    match_score = models.FloatField()
    missing_skills = models.JSONField(null=True, blank=True)
    match_summary = models.TextField(null=True, blank=True)
    cover_letter = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')

    def __str__(self):
        return f"Match for {self.candidate.username} - {self.job.title}"