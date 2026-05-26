
from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    # Common Fields
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)
    github_url = models.URLField(max_length=200, blank=True, null=True)
    portfolio_url = models.URLField(max_length=200, blank=True, null=True)

    # Job Seeker Fields
    skills = models.TextField(blank=True, help_text="Comma separated skills e.g. Python, Django, React")
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    # HR Fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_website = models.URLField(max_length=200, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user.email} Profile"