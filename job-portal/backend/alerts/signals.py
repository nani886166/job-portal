from django.db.models.signals import post_save
from django.dispatch import receiver
from jobs.models import Job
from profiles.models import Profile
from applications.models import Notification
from accounts.models import User

@receiver(post_save, sender=Job)
def notify_matching_seekers(sender, instance, created, **kwargs):
    # Only trigger for new jobs
    if not created:
        return

    # If the job has no required skills, skip (or you can match by keywords)
    if not instance.skills_required:
        return

    # Normalise job skills to lowercase set
    job_skills = {skill.lower().strip() for skill in instance.skills_required if skill}

    # Get all active seekers
    seekers = User.objects.filter(role='seeker', is_active=True)

    for seeker in seekers:
        # Check if user wants to receive alerts (default True)
        if hasattr(seeker, 'alert_preference') and not seeker.alert_preference.receive_job_alerts:
            continue

        profile = Profile.objects.filter(user=seeker).first()
        if not profile or not profile.skills:
            continue

        # Normalise seeker skills
        seeker_skills = {skill.lower().strip() for skill in profile.skills if skill}

        # If intersection exists, send notification
        if job_skills & seeker_skills:
            Notification.objects.create(
                recipient=seeker,
                sender=instance.posted_by,
                notification_type='job_alert',   # you may need to add this choice in Notification model
                title='New Job Matching Your Skills',
                message=f"New job '{instance.title}' at {instance.company} matches your skills: {', '.join(job_skills & seeker_skills)}",
                related_application=None
            )