@echo off
setlocal

REM Set variables
set DOCKERHUB_USERNAME=%1
set IMAGE_NAME=dinox-app
set TAG=latest

REM Check if Docker Hub username is provided
if "%DOCKERHUB_USERNAME%"=="" (
    echo Please provide Docker Hub username as a parameter
    echo Usage: rebuild_and_push.bat your_dockerhub_username
    exit /b 1
)

REM Check Streamlit version compatibility
echo Checking Streamlit version compatibility...
python check_compatibility.py
if %ERRORLEVEL% neq 0 (
    echo Version compatibility check failed, please fix the issue before continuing
    exit /b 1
)

REM Build Docker image
echo Rebuilding Docker image...
docker build -t %IMAGE_NAME% --no-cache .

REM Tag the image
echo Tagging the image...
docker tag %IMAGE_NAME% %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

REM Test run the container
echo Testing the container locally...
docker run -d --name test-dinox-app -p 8501:8501 -e DINOX_API_TOKEN=%DINOX_API_TOKEN% %IMAGE_NAME%
echo Waiting for container to start...
timeout /t 5 /nobreak > nul
echo Checking container health status...
docker inspect --format="{{.State.Health.Status}}" test-dinox-app
echo Please visit http://localhost:8501 in your browser to test the application

echo Press any key to continue pushing the image to Docker Hub, or press Ctrl+C to cancel...
pause > nul

REM Stop and remove test container
echo Stopping and removing test container...
docker stop test-dinox-app > nul
docker rm test-dinox-app > nul

REM Log in to Docker Hub
echo Logging in to Docker Hub...
docker login

REM Push the image to Docker Hub
echo Pushing the image to Docker Hub...
docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

echo Done! The fixed image has been pushed to %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%TAG%

endlocal 