import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Invitation

logger = logging.getLogger(__name__)

@shared_task
def send_invitation_email(invitation_id):
    """
    Celery task to send an onboarding invitation email.
    """
    try:
        invitation = Invitation.objects.select_related('organization', 'invited_by').get(id=invitation_id)
    except Invitation.DoesNotExist:
        logger.error(f"Failed to send email: Invitation {invitation_id} does not exist.")
        return

    subject = f"You've been invited to join {invitation.organization.name}"
    
    # We create a simple HTML template string here, but you can move this to a real template file
    html_message = f"""
    <html>
        <body>
            <h2>Welcome to {invitation.organization.name}</h2>
            <p>You have been invited by {invitation.invited_by.full_name} to join as a <strong>{invitation.get_role_proffered_display()}</strong>.</p>
            <p>{invitation.message}</p>
            <br>
            <p>Please click the link below to accept your invitation and set up your account:</p>
            <a href="{invitation.invite_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Accept Invitation</a>
            <br><br>
            <p>Or copy and paste this link into your browser:</p>
            <p>{invitation.invite_url}</p>
            <br>
            <p>This invitation will expire on {invitation.expires_at.strftime('%Y-%m-%d')}.</p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Successfully sent invitation email to {invitation.email}")
    except Exception as e:
        logger.error(f"Error sending email to {invitation.email}: {str(e)}")
        raise e  # Re-raise to trigger celery retry if configured
