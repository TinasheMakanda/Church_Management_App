from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from rest_framework.authtoken import views


def root(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "CHMS API",
            "admin": "/admin/",
            "auth_api": "/api/auth/",
        }
    )

urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
    path("api/api-token-auth/", views.obtain_auth_token),
    path("api/auth/", include("users.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/onboarding/", include("onboarding.urls")),
    path("api/groups/", include("groups.urls")),
    path("api/events/", include("events.urls")),
]
