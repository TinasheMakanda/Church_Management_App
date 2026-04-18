from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvitationViewSet, validate_token, accept_invitation

router = DefaultRouter()
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('accept/',             accept_invitation, name='accept-invitation'),
    path('validate/<uuid:token>/', validate_token,   name='validate-token'),
]
