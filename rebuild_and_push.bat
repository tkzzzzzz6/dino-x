@echo off
setlocal

REM 设置变量
set DOCKERHUB_USERNAME=%1
set IMAGE_NAME=dinox-app
set TAG=latest

REM 检查是否提供了Docker Hub用户名
if "%DOCKERHUB_USERNAME%"=="" (
    echo 请提供Docker Hub用户名作为参数
    echo 用法: rebuild_and_push.bat your_dockerhub_username
    exit /b 1
)

REM 构建Docker镜像
echo 正在重新构建Docker镜像...
docker build -t %IMAGE_NAME% --no-cache .

REM 为镜像添加标签
echo 为镜像添加标签...
docker tag %IMAGE_NAME% %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM 登录到Docker Hub
echo 登录到Docker Hub...
docker login

REM 推送镜像到Docker Hub
echo 推送镜像到Docker Hub...
docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

echo 完成！修复后的镜像已推送到 %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM 测试运行容器
echo 正在本地测试容器...
docker run -d --name test-dinox-app -p 8501:8501 %IMAGE_NAME%
echo 请在浏览器中访问 http://localhost:8501 测试应用
echo 测试完成后，可以使用以下命令停止并删除测试容器:
echo docker stop test-dinox-app ^&^& docker rm test-dinox-app

endlocal 