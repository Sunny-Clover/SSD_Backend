# import pytest
# from fastapi.testclient import TestClient
# from sqlmodel import SQLModel, create_engine, Session
# from app.main import app  # 假設您的 FastAPI 應用在 app/main.py 中
# from app.database import get_session
# from app.models import User  # 根據您的模型位置調整

# # 使用 SQLite 的內存數據庫進行測試
# TEST_DATABASE_URL = "sqlite:///:memory:"

# # 創建引擎
# test_engine = create_engine(TEST_DATABASE_URL, echo=True)

# # 創建所有表
# SQLModel.metadata.create_all(test_engine)

# # 定義一個覆蓋的 get_session 依賴
# def get_test_session():
#     with Session(test_engine) as session:
#         yield session

# # 使用 fixture 來覆蓋 get_session
# @pytest.fixture(name="client")
# def client_fixture():
#     app.dependency_overrides[get_session] = get_test_session
#     with TestClient(app) as client:
#         yield client
#     app.dependency_overrides.pop(get_session, None)
