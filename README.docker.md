# DINO-X 图像分析工具 Docker 指南

这个文档提供了如何使用Docker构建和运行DINO-X图像分析工具的说明。

## 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/) (可选，但推荐)
- 获取 DINO-X API 令牌

## 使用 Docker 构建和运行

### 构建 Docker 镜像

```bash
docker build -t dinox-app .
```

### 运行 Docker 容器

```bash
docker run -p 8501:8501 -e DINOX_API_TOKEN=your_api_token dinox-app
```

替换 `your_api_token` 为您的实际 DINO-X API 令牌。

### 访问应用程序

在浏览器中打开 http://localhost:8501 访问应用程序。

## 使用 Docker Compose 构建和运行

### 创建 .env 文件

创建一个 `.env` 文件，包含您的 DINO-X API 令牌：

```
DINOX_API_TOKEN=your_api_token
```

替换 `your_api_token` 为您的实际 DINO-X API 令牌。

### 启动服务

```bash
docker-compose up -d
```

### 停止服务

```bash
docker-compose down
```

### 访问应用程序

在浏览器中打开 http://localhost:8501 访问应用程序。

## 上传到 Docker Hub

### 登录到 Docker Hub

```bash
docker login
```

### 为镜像添加标签

```bash
docker tag dinox-app your_dockerhub_username/dinox-app:latest
```

替换 `your_dockerhub_username` 为您的 Docker Hub 用户名。

### 推送镜像到 Docker Hub

```bash
docker push your_dockerhub_username/dinox-app:latest
```

## 从 Docker Hub 拉取和运行

```bash
docker pull your_dockerhub_username/dinox-app:latest
docker run -p 8501:8501 -e DINOX_API_TOKEN=your_api_token your_dockerhub_username/dinox-app:latest
```

## 注意事项

- 应用程序需要有效的 DINO-X API 令牌才能正常工作
- 默认情况下，应用程序在容器内的 8501 端口上运行
- 您可以通过修改 `docker run` 命令中的端口映射来更改主机上的端口 