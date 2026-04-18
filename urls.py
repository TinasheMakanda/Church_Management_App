from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/organizations/', include('organizations.urls')),
    path('api/onboarding/', include('onboarding.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/events/', include('events.urls')),
]
