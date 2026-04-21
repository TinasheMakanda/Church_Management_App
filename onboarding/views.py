"""
onboarding/views.py
--------------------
Endpoints:

  POST   /api/onboarding/invitations/          — send an invitation
  GET    /api/onboarding/invitations/           — list sent invitations (scoped to org)
  GET    /api/onboarding/invitations/{id}/      — detail
  DELETE /api/onboarding/invitations/{id}/      — revoke
  POST   /api/onboarding/accept/               — accept an invitation (public, no auth)
  GET    /api/onboarding/validate/{token}/     — check token validity (public)
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.permissions import CanInvite, IsSameOrganization
from .models import Invitation, InvitationStatus
from .serializers import (
    InvitationSerializer,
    SendInvitationSerializer,
    AcceptInvitationSerializer,
)


class InvitationViewSet(viewsets.ModelViewSet):
    """
    Manage invitations for the authenticated user's Organization.
    Only users with an inviter-eligible role can create invitations.
    """
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization, CanInvite]
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']  # no PUT/PATCH

    def get_queryset(self):
        return (
            Invitation.objects
            .filter(organization=self.request.user.organization)
            .select_related('invited_by', 'accepted_by', 'organization')
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return SendInvitationSerializer
        return InvitationSerializer

    def create(self, request, *args, **kwargs):
        from .tasks import send_invitation_email
        serializer = SendInvitationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()

        # Fire async celery task
        send_invitation_email.delay(invitation.id)

        return Response(
            InvitationSerializer(invitation, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        invitation = self.get_object()
        if invitation.status != InvitationStatus.PENDING:
            return Response(
                {'detail': 'Only pending invitations can be revoked.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invitation.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Public endpoints (no authentication required)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def validate_token(request, token):
    """
    GET /api/onboarding/validate/{token}/
    Returns basic info about the invitation so the frontend can
    pre-fill the registration form (email, role, org name).
    """
    try:
        invitation = Invitation.objects.select_related('organization').get(token=token)
    except Invitation.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

    if not invitation.is_valid:
        return Response(
            {'detail': f"Invitation is {invitation.get_status_display().lower()}."},
            status=status.HTTP_410_GONE,
        )

    return Response({
        'email':            invitation.email,
        'role':             invitation.role_proffered,
        'role_display':     invitation.get_role_proffered_display(),
        'organization':     invitation.organization.name,
        'invited_by':       invitation.invited_by.full_name if invitation.invited_by else '',
        'expires_at':       invitation.expires_at,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def accept_invitation(request):
    """
    POST /api/onboarding/accept/
    Body: { token, first_name, last_name, password, phone_number }

    Creates the User, stamps the Invitation as ACCEPTED, and returns
    the new user's basic info. The frontend should then redirect to login.
    """
    serializer = AcceptInvitationSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    return Response({
        'detail': 'Registration successful. Please log in.',
        'email': user.email,
        'role':  user.role,
    }, status=status.HTTP_201_CREATED)
