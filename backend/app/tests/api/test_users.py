import pytest
import requests

BASE_URL = "http://localhost:8000"

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

@pytest.fixture
def token():
    """Fixture to create a user and log in to get a token."""
    # 創建用戶
    requests.post(f"{BASE_URL}/users/", json=test_user_data)
    # 登錄並獲取 token
    login_data = {"username": test_user_data["UserName"], "password": test_user_data["Password"]}
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    return tokens["access_token"]

def test_create_user():
    """測試創建用戶"""
    response = requests.post(f"{BASE_URL}/users/", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["UserName"] == test_user_data["UserName"]
    assert data["Email"] == test_user_data["Email"]

def test_read_user_me(token):
    """測試獲取當前用戶資料"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["UserName"] == test_user_data["UserName"]
    assert data["Email"] == test_user_data["Email"]

def test_update_user(token):
    """測試更新用戶資料"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me", json=updated_user_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["FirstName"] == updated_user_data["FirstName"]
    assert data["LastName"] == updated_user_data["LastName"]
    assert data["Gender"] == updated_user_data["Gender"]

def test_update_password(token):
    """測試更新用戶密碼"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/users/me/password", json=password_update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "密碼更新成功"
