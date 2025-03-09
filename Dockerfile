FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖 - 修复安装问题
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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

# 确保Python文件使用Unix行尾
RUN find . -name "*.py" -exec dos2unix {} \;

# 设置环境变量
ENV PYTHONUNBUFFERED=1
# 设置默认API令牌（将在运行时被覆盖）
ENV DINOX_API_TOKEN="请在运行容器时提供有效的API令牌"

# 暴露Streamlit默认端口
EXPOSE 8501

# 设置健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "=== DINO-X 图像分析工具启动 ==="\n\
echo "检查API令牌..."\n\
if [ -z "$DINOX_API_TOKEN" ]; then\n\
  echo "警告: DINOX_API_TOKEN环境变量未设置，API调用将会失败"\n\
else\n\
  echo "API令牌已设置: ${DINOX_API_TOKEN:0:5}...${DINOX_API_TOKEN: -5}"\n\
fi\n\
echo "启动Streamlit应用..."\n\
python run.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh && dos2unix /app/start.sh

# 启动命令
ENTRYPOINT ["/app/start.sh"] 