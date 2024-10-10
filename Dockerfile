# 使用python官方映像檔案
FROM python:3.9

# 切換(創建)容器內工作目錄
WORKDIR /app

# 將dockerfile目錄下所有檔案複製到容器內/app目錄下
COPY . /app

# 安裝相依套件，並不暫存檔案
RUN pip install --no-cache-dir -r requirements.txt


