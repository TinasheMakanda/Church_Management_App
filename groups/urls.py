from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChurchGroupViewSet, GroupMembershipViewSet

router = DefaultRouter()
router.register(r'groups',      ChurchGroupViewSet,      basename='group')
router.register(r'memberships', GroupMembershipViewSet,  basename='group-membership')

urlpatterns = [path('', include(router.urls))]
