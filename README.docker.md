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

## 网络配置和常见问题

### 无法从外部访问应用程序

如果您无法从其他设备访问应用程序，请检查以下几点：

1. **确保应用绑定到正确的地址**：
   - 应用程序必须绑定到 `0.0.0.0` 而不是 `127.0.0.1` 才能从外部访问
   - 我们的 Dockerfile 已配置为使用 `--server.address=0.0.0.0`

2. **检查防火墙设置**：
   - 确保主机防火墙允许 8501 端口的入站连接
   - 在 Windows 上，您可能需要在 Windows Defender 防火墙中添加例外
   - 在 Linux 上，您可以使用 `sudo ufw allow 8501` 开放端口

3. **使用正确的访问 URL**：
   - 使用主机的 IP 地址而不是 `localhost` 或 `127.0.0.1`
   - 例如：`http://192.168.1.100:8501`（使用您主机的实际 IP 地址）

4. **在云服务器上运行**：
   - 如果在云服务器上运行，确保安全组/网络 ACL 允许 8501 端口的入站流量
   - 您可能需要配置公网 IP 和端口转发

### 在 Linux 上使用 Host 网络模式

在 Linux 主机上，您可以使用 host 网络模式来简化网络配置：

```bash
docker run --network host -e DINOX_API_TOKEN=your_api_token dinox-app
```

或者在 docker-compose.yml 中：

```yaml
services:
  dinox-app:
    # ... 其他配置 ...
    network_mode: "host"
```

注意：host 网络模式仅在 Linux 主机上有效，在 Windows 和 Mac 上不起作用。

### 查找容器 IP 地址

如果需要查找容器的 IP 地址，可以使用以下命令：

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dinox-app
```

### 测试容器网络连接

要测试容器内的网络连接，可以执行以下命令：

```bash
docker exec -it dinox-app curl -v http://localhost:8501
```

如果返回 HTML 内容，则表示应用程序在容器内正常运行。 