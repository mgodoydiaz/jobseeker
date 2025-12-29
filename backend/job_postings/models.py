from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    """
    Extends the built-in User model to add a professional summary.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    professional_summary = models.TextField(
        blank=True,
        null=True,
        help_text="Plain text summary of user's experience for LLM analysis."
    )

    def __str__(self):
        return self.user.username

class JobOffer(models.Model):
    """
    Represents a job offer scraped or added by a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    original_url = models.URLField(max_length=2000, unique=True)
    description = models.TextField(blank=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # LLM Analysis Fields
    summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of the job offer.")
    match_score = models.IntegerField(blank=True, null=True, help_text="AI-generated score of how well the user's profile matches the offer.")
    missing_skills = models.TextField(blank=True, null=True, help_text="AI-identified skills that the user is missing for this role.")

    def __str__(self):
        return f"{self.title} at {self.company}"

class Application(models.Model):
    """
    Connects a User to a JobOffer, representing an application.
    This is the core model for the Kanban board.
    """
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPLIED = 'APPLIED', 'Applied'
        INTERVIEW = 'INTERVIEW', 'Interview'
        REJECTED = 'REJECTED', 'Rejected'
        OFFER = 'OFFER', 'Offer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    application_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        # Ensures a user can only apply once to a specific job offer
        unique_together = ('user', 'job_offer')

    def __str__(self):
        return f"{self.user.username}'s application for {self.job_offer.title}"

class ResumeTemplate(models.Model):
    """
    Stores base .docx resume templates for users.
    """
    name = models.CharField(max_length=255)
    template_file = models.FileField(upload_to='resume_templates/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_templates')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
