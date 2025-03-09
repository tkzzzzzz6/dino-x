# DINO-X 图像分析工具

基于 DINO-X API 的图像分析工具，支持目标检测和图像处理功能。

## 功能特点

- 图像上传和 URL 输入
- 图像预处理和增强
- 目标检测和可视化
- 检测结果分析和展示

## 环境要求

- Python 3.9+
- Docker (可选，用于容器化部署)

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API 令牌

创建 `.env` 文件并添加您的 DINO-X API 令牌：

```
DINOX_API_TOKEN=your_api_token_here
```

或者设置环境变量：

```bash
# Windows
set DINOX_API_TOKEN=your_api_token_here

# Linux/Mac
export DINOX_API_TOKEN=your_api_token_here
```

### 3. 运行应用

```bash
python run.py
```

应用将在 http://localhost:8501 上运行。

## Docker 部署

### 使用 Docker Compose

1. 创建 `.env` 文件并添加您的 API 令牌
2. 运行以下命令：

```bash
docker-compose up -d
```

### 手动构建和运行

1. 构建 Docker 镜像：

```bash
docker build -t dinox-app .
```

2. 运行容器：

```bash
docker run -p 8501:8501 -e DINOX_API_TOKEN=your_api_token dinox-app
```

## 使用说明

1. 上传图像或输入图像 URL
2. 可选：调整图像（亮度、对比度等）
3. 设置检测参数（提示词、置信度阈值等）
4. 点击"分析图像"按钮进行检测
5. 查看检测结果和可视化效果

## 故障排除

### API 调用失败

- 确保已设置有效的 DINOX_API_TOKEN
- 检查网络连接
- 查看日志以获取详细错误信息

### 容器无法启动

- 确保 Docker 已正确安装
- 检查端口 8501 是否被占用
- 查看容器日志：`docker logs dinox-app`

## 许可证

MIT 