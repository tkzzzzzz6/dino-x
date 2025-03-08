@echo off
setlocal

REM Set variables
set DOCKERHUB_USERNAME=%1
set IMAGE_NAME=dinox-app
set TAG=latest

REM Check if Docker Hub username is provided
if "%DOCKERHUB_USERNAME%"=="" (
    echo Please provide Docker Hub username as an argument
    echo Usage: build_and_push.bat your_dockerhub_username
    exit /b 1
)

REM Build Docker image
echo Building Docker image...
docker build -t %IMAGE_NAME% .

REM Tag the image
echo Tagging the image...
docker tag %IMAGE_NAME% %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM Log in to Docker Hub
echo Logging in to Docker Hub...
docker login

REM Push the image to Docker Hub
echo Pushing the image to Docker Hub...
docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

echo Done! The image has been pushed to %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

endlocal 