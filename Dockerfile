FROM python:3.10-slim-buster

# 设置工作目录并从 Git 仓库中复制项目文件到镜像中
WORKDIR /app
RUN apt-get update && apt-get install -y git && apt-get install -y sqlite3
ARG GIT_REPO
RUN git clone $GIT_REPO .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置入口命令
CMD ["python", "main.py"]
