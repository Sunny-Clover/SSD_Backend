import requests

BASE_URL = "http://localhost:8000"  # FastAPI 服務的 URL

# 測試數據
test_user_datas = [
    {
    "UserName": f"user{x}",
    "Email": f"user{x}@example.com",
    "Password": "123123123"
    } for x in range(10)
]

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
  "EndTime": "2024-12-22T09:40:24.883Z",
  "TotalTime": "00:00:10.0Z",
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

test_detection_data2 = {
    "StartTime": "2024-12-22T17:32:42",
    "EndTime": "2024-12-22T17:34:22",
    "TotalTime": "00:01:40",
    "TotalPredictions": 100,
    "Torso": {
        "BackwardCount": 10,
        "ForwardCount": 20,
        "NeutralCount": 70
    },
    "Feet": {
        "AnkleOnKneeCount": 5,
        "FlatCount": 95
    },
    "Head": {
        "BowedCount": 15,
        "NeutralCount": 80,
        "TiltBackCount": 5
    },
    "Shoulder": {
        "HunchedCount": 10,
        "NeutralCount": 85,
        "ShrugCount": 5
    },
    "Neck": {
        "ForwardCount": 20,
        "NeutralCount": 80
    }
}

def create_user(user_data, is_print=False):
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if is_print:
        print("Create User Response:", response.json())
    return response

def login_user(user_data, is_print=False):
    login_data = {"username": user_data["UserName"], "password": user_data["Password"]}
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if is_print:
        print("Login Response:", response.json())
    return response.json()["access_token"]

def get_current_user(token, is_print=False):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print("Get Current User Response:", response.json())
    return response

def update_user(token, is_print=False):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me", json=updated_user_data, headers=headers)
    print("Update User Response:", response.json())
    return response

def update_password(token, is_print=False):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me/password", json=password_update_data, headers=headers)
    if is_print:
        print("Update Password Response:", response.json())
    return response

def create_detection(token, detection_data, is_print=False):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/detections/", json=detection_data, headers=headers)
    if is_print:
        print("Create Detection Response:", response.json())
    return response

if __name__ == "__main__":
    print("\nCreating user...")
    for user_data in test_user_datas:
        create_user(user_data)
    
    print("\nLogging in user...")
    tokens = []
    for user_data in test_user_datas:
        token = login_user(user_data)
        tokens.append(token)
    
    # print("\n3. Getting current user data...")
    # get_current_user(token)
    
    # print("\n4. Updating user data...")
    # update_user(token)
    
    # print("\n5. Updating password...")
    # update_password(token)

    print("\nCreating detection...")
    for idx, user_data in enumerate(test_user_datas):
        create_detection(tokens[idx], test_detection_data2)