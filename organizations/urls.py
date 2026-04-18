from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, RegionViewSet, ProvinceViewSet, ChurchViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'regions',       RegionViewSet,        basename='region')
router.register(r'provinces',     ProvinceViewSet,       basename='province')
router.register(r'churches',      ChurchViewSet,         basename='church')

urlpatterns = [path('', include(router.urls))]
