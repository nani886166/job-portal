from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from applications.models import Notification

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    if not created:
        return
    conv = instance.conversation
    for participant in conv.participants.all():
        if participant != instance.sender:
            Notification.objects.create(
                recipient=participant,
                sender=instance.sender,
                notification_type='hr_reply',   # or create a new type 'message'
                title='New Message',
                message=f'{instance.sender.email}: {instance.content[:50]}',
                related_application=None
            )
