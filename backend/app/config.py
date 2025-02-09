import os
from dotenv import load_dotenv

# 把目錄下.env加入環境變數
# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/dbname")
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db:3306/mysql_db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360
REFRESH_TOKEN_EXPIRE_DAYS = 30
