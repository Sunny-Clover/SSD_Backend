import httpx

def create_user(client: httpx.Client, username: str, email: str, password: str):
    """創建用戶輔助函數"""
    response = client.post(
        "/users/",
        json={
            "UserName": username,
            "Email": email,
            "Password": password
        }
    )
    return response

def get_auth_token(client: httpx.Client, username: str, password: str):
    """獲取 token 輔助函數"""
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response
