import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chms.settings")
django.setup()

from users.models import User
from organizations.models import Organization

def link_superadmin():
    print("Linking superadmin to organization...")
    user = User.objects.filter(email="symphonytone@gmail.com").first()
    
    if not user:
        print("User not found! Did you use a different email?")
        return
        
    org = Organization.objects.filter(slug="family-of-god").first()
    if not org:
        org = Organization.objects.create(
            name="Family Of God",
            slug="family-of-god",
            country="ZA",
            description="Root organization"
        )
        print("Created Organization: Family Of God")
        
    if user.organization != org:
        user.organization = org
        user.role = "SUPER_ADMIN"
        user.save()
        print(f"Successfully linked {user.email} as SUPER_ADMIN to {org.name}!")
    else:
        print(f"User is already linked to {org.name}.")

if __name__ == "__main__":
    link_superadmin()