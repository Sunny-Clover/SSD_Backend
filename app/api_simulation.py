import requests

BASE_URL = "http://localhost:8000"  # FastAPI 服務的 URL

# 測試數據
test_user_data = {
    "UserName": "testuser",
    "Email": "testuser@example.com",
    "Password": "password123"
}

updated_user_data = {
    "FirstName": "Test",
    "LastName": "User",
    "Gender": "Other"
}

password_update_data = {
    "current_password": "password123",
    "new_password": "newpassword456",
    "confirm_password": "newpassword456"
}

def create_user():
    response = requests.post(f"{BASE_URL}/users/", json=test_user_data)
    print("Create User Response:", response.json())
    return response

def login_user():
    login_data = {"username": test_user_data["UserName"], "password": test_user_data["Password"]}
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    print("Login Response:", response.json())
    return response.json()["access_token"]

def get_current_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print("Get Current User Response:", response.json())
    return response

def update_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me", json=updated_user_data, headers=headers)
    print("Update User Response:", response.json())
    return response

def update_password(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me/password", json=password_update_data, headers=headers)
    print("Update Password Response:", response.json())
    return response

if __name__ == "__main__":
    print("1. Creating user...")
    create_user()
    
    print("\n2. Logging in user...")
    token = login_user()
    
    print("\n3. Getting current user data...")
    get_current_user(token)
    
    print("\n4. Updating user data...")
    update_user(token)
    
    print("\n5. Updating password...")
    update_password(token)
