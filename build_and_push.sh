#!/bin/bash

# 设置变量
DOCKERHUB_USERNAME="$1"
IMAGE_NAME="dinox-app"
TAG="latest"

# 检查是否提供了Docker Hub用户名
if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo "请提供Docker Hub用户名作为参数"
    echo "用法: ./build_and_push.sh your_dockerhub_username"
    exit 1
fi

# 构建Docker镜像
echo "正在构建Docker镜像..."
docker build -t $IMAGE_NAME .

# 为镜像添加标签
echo "为镜像添加标签..."
docker tag $IMAGE_NAME $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

# 登录到Docker Hub
echo "登录到Docker Hub..."
docker login

# 推送镜像到Docker Hub
echo "推送镜像到Docker Hub..."
docker push $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

echo "完成！镜像已推送到 $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG" 