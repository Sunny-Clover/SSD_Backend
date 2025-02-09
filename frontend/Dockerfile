# 使用 Node.js 官方基礎映像
FROM node:21

# 設置工作目錄
WORKDIR /app

# 複製前端應用程式碼到工作目錄
COPY . .

# 安裝依賴
RUN npm install

# 暴露容器在 3000 埠運行
EXPOSE 3000

# 設定環境變數，讓應用綁定 0.0.0.0 並使用 3000 埠（根據需要，也可設定 PORT=3000）
ENV HOST=0.0.0.0
ENV PORT=3000
ENV CHOKIDAR_USEPOLLING=true

CMD ["npm", "run", "dev"]
