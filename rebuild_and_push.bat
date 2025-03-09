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

REM 检查API令牌是否设置
if "%DINOX_API_TOKEN%"=="" (
    echo 警告: DINOX_API_TOKEN环境变量未设置
    echo 请设置DINOX_API_TOKEN环境变量，例如:
    echo set DINOX_API_TOKEN=your_api_token
    set /p CONTINUE=是否继续？(Y/N) 
    if /i "%CONTINUE%" neq "Y" exit /b 1
)

REM 构建Docker镜像
echo 正在重新构建Docker镜像...
docker build -t %IMAGE_NAME% --no-cache .

REM 为镜像添加标签
echo 为镜像添加标签...
docker tag %IMAGE_NAME% %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM 测试运行容器
echo 正在本地测试容器...
if not "%DINOX_API_TOKEN%"=="" (
    echo 使用环境变量中的API令牌: %DINOX_API_TOKEN:~0,5%...%DINOX_API_TOKEN:~-5%
    docker run -d --name test-dinox-app -p 8501:8501 -e DINOX_API_TOKEN=%DINOX_API_TOKEN% %IMAGE_NAME%
) else (
    echo 警告: 未设置API令牌，测试容器可能无法正常工作
    docker run -d --name test-dinox-app -p 8501:8501 %IMAGE_NAME%
)

echo 等待容器启动...
timeout /t 10 /nobreak > nul

REM 检查容器是否在运行
echo 检查容器状态...
docker ps -f name=test-dinox-app
echo 检查容器日志...
docker logs test-dinox-app

REM 检查容器健康状态
echo 检查容器健康状态...
docker inspect --format="{{.State.Health.Status}}" test-dinox-app

REM 测试API连接
echo 测试API连接...
echo 请在浏览器中访问 http://localhost:8501 测试应用
echo 特别注意检查API连接是否正常工作

echo 按任意键继续推送镜像到Docker Hub，或按Ctrl+C取消...
pause > nul

REM 停止并删除测试容器
echo 停止并删除测试容器...
docker stop test-dinox-app
docker rm test-dinox-app

REM 登录到Docker Hub
echo 登录到Docker Hub...
docker login

REM 推送镜像到Docker Hub
echo 推送镜像到Docker Hub...
docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

echo 完成！修复后的镜像已推送到 %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM 提供使用说明
echo.
echo 使用说明:
echo 1. 拉取镜像: docker pull %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%
echo 2. 运行容器: docker run -p 8501:8501 -e DINOX_API_TOKEN=your_api_token %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%
echo 3. 访问应用: http://localhost:8501
echo.
echo 注意: 必须提供有效的DINOX_API_TOKEN环境变量，否则API调用将会失败

endlocal 