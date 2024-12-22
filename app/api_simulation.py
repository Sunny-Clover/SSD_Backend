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

test_detection_data = {
  "StartTime": "2024-12-22T09:40:14.883Z",
  "EndTime": "2024-12-22T09:40:14.883Z",
  "TotalTime": "09:40:14.883Z",
  "TotalPredictions": 10,
  "Torso": {
    "BackwardCount": 0,
    "ForwardCount": 0,
    "NeutralCount": 10
  },
  "Feet": {
    "AnkleOnKneeCount": 5,
    "FlatCount": 5
  },
  "Head": {
    "BowedCount": 2,
    "NeutralCount": 3,
    "TiltBackCount": 5
  },
  "Shoulder": {
    "HunchedCount": 2,
    "NeutralCount": 3,
    "ShrugCount": 5
  },
  "Neck": {
    "ForwardCount": 2,
    "NeutralCount": 8
  }
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

def create_detection(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/detections/", json=test_detection_data, headers=headers)
    print("Create Detection Response:", response.json())
    return response

if __name__ == "__main__":
    print("1. Creating user...")
    create_user()
    
    print("\n2. Logging in user...")
    token = login_user()
    
    print("\n3. Getting current user data...")
    get_current_user(token)
    
    # print("\n4. Updating user data...")
    # update_user(token)
    
    # print("\n5. Updating password...")
    # update_password(token)

    print("\n6. Creating detection...")
    create_detection(token)