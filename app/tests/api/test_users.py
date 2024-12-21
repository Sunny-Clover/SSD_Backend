import pytest
from httpx import AsyncClient

# 測試用數據

# 用戶註冊測試數據
test_user_data = {
    "UserName": "testuser",
    "Email": "testuser@example.com",
    "Password": "password123"
}

# 用戶更新測試數據
updated_user_data = {
    "FirstName": "Test",
    "LastName": "User",
    "Gender": "Other",
}

# 用戶密碼更新測試數據
password_update_data = {
    "current_password": "password123",
    "new_password": "newpassword456",
    "confirm_password": "newpassword456"
}

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    # 創建新用戶
    response = await async_client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["UserName"] == test_user_data["UserName"]
    assert data["Email"] == test_user_data["Email"]


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # 登錄用戶以獲取 token
    response = await async_client.post(
        "/auth/token", 
        data={"username": test_user_data["UserName"], "password": test_user_data["Password"]}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
    return tokens["access_token"]


@pytest.mark.asyncio
async def test_read_user_me(async_client: AsyncClient):
    # 獲取當前用戶資料
    token = await test_login_user(async_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["UserName"] == test_user_data["UserName"]
    assert data["Email"] == test_user_data["Email"]


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient):
    # 更新用戶資料
    token = await test_login_user(async_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch("/users/me", json=updated_user_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["FirstName"] == updated_user_data["FirstName"]
    assert data["LastName"] == updated_user_data["LastName"]
    assert data["Gender"] == updated_user_data["Gender"]


@pytest.mark.asyncio
async def test_update_password(async_client: AsyncClient):
    # 更新用戶密碼
    token = await test_login_user(async_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch("/users/me/password", json=password_update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "密碼更新成功"
