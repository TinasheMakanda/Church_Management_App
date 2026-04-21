import requests

BASE_URL = "https://church-management-app-ae98.onrender.com/api"
EMAIL = "symphonytone@gmail.com"
PASSWORD = "Shalom7$"

def main():
    print("Testing API endpoints...")
    session = requests.Session()
    auth = (EMAIL, PASSWORD)
    
    # Get CSRF token first
    session.get(f"{BASE_URL}/organizations/organizations/", auth=auth)
    if 'csrftoken' in session.cookies:
        headers = {'X-CSRFToken': session.cookies['csrftoken']}
    else:
        headers = {}
        
    print("\n1. Verifying Organization Access...")
    response = session.get(
        f"{BASE_URL}/organizations/organizations/", 
        auth=auth,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(response.json())
    
    # 2. Test sending an invitation
    print("\n2. Sending an invitation...")
    invite_data = {
        "email": "another_test@example.com",
        "role_proffered": "APOSTLE",
        "message": "Testing the flow again!"
    }
    
    response = session.post(
        f"{BASE_URL}/onboarding/invitations/", 
        json=invite_data, 
        auth=auth,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    main()