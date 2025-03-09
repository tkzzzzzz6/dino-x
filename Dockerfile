FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖 - 确保使用确切的版本
RUN pip install --no-cache-dir -r requirements.txt

# 安装pycocotools（用于掩码解码）
RUN pip install --no-cache-dir pycocotools

# 验证Streamlit版本
RUN python -c "import streamlit; print(f'Installed Streamlit version: {streamlit.__version__}')"

# 复制应用程序代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露Streamlit默认端口
EXPOSE 8501

# 设置健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 启动命令 - 修改地址为0.0.0.0以允许外部访问
ENTRYPOINT ["python", "run.py", "--server.port=8501", "--server.address=0.0.0.0"] 