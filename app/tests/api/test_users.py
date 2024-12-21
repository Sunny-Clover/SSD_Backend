# import pytest
# from fastapi import status
# from app.schemas import UserCreate, UserResponse
# from sqlmodel import Session
# from app.models import User
# from app.database import get_session
# from app.main import app

# @pytest.fixture
# def test_user(client):
#     user_data = {
#         "Email": "test@example.com",
#         "UserName": "testuser",
#         "FirstName": "Test",
#         "LastName": "User",
#         "Password": "securepassword123"
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_200_OK
#     return response.json()

# def test_create_user_success(client):
#     user_data = {
#         "Email": "newuser@example.com",
#         "UserName": "newuser",
#         "FirstName": "New",
#         "LastName": "User",
#         "Password": "newsecurepassword"
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["Email"] == user_data["Email"]
#     assert data["UserName"] == user_data["UserName"]
#     assert "Password" not in data  # 確保密碼不在響應中

# def test_create_user_duplicate_email(client, test_user):
#     user_data = {
#         "Email": "test@example.com",  # 已存在的郵箱
#         "UserName": "anotheruser",
#         "FirstName": "Another",
#         "LastName": "User",
#         "Password": "anotherpassword"
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "電子郵件已被註冊"

# def test_create_user_duplicate_username(client, test_user):
#     user_data = {
#         "Email": "unique@example.com",
#         "UserName": "testuser",  # 已存在的用戶名
#         "FirstName": "Unique",
#         "LastName": "User",
#         "Password": "uniquepassword"
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "用戶名已被使用"

# def test_create_user_invalid_password(client):
#     user_data = {
#         "Email": "invalidpass@example.com",
#         "UserName": "invalidpassuser",
#         "FirstName": "Invalid",
#         "LastName": "Password",
#         "Password": "short"  # 密碼太短
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Pydantic 驗證失敗
#     # 可以檢查具體的錯誤信息
#     assert response.json()["detail"][0]["msg"] == "Password must be between 8 and 40 characters"

# def test_create_user_missing_fields(client):
#     user_data = {
#         "Email": "missingfields@example.com",
#         # 缺少 UserName 和 Password
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     # 檢查缺少的字段
#     errors = response.json()["detail"]
#     assert any(error["loc"][-1] == "UserName" for error in errors)
#     assert any(error["loc"][-1] == "Password" for error in errors)

# def test_create_user_invalid_email(client):
#     user_data = {
#         "Email": "invalidemail",  # 非法郵箱格式
#         "UserName": "invalidemailuser",
#         "FirstName": "Invalid",
#         "LastName": "Email",
#         "Password": "validpassword123"
#     }
#     response = client.post("/users/", json=user_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     assert response.json()["detail"][0]["msg"] == "value is not a valid email address"
