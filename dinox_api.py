import requests
import base64
import json
import time
import os
from dotenv import load_dotenv
from PIL import Image
import io
import numpy as np

# Load environment variables
load_dotenv()

# Get API token from environment variables or use a hardcoded value
# 请将下面的 "你的API令牌" 替换为你从 DINO-X 获取的实际 API 令牌
API_TOKEN = os.getenv("DINOX_API_TOKEN") or "你的API令牌"

# 打印API令牌状态（不显示完整令牌）
if API_TOKEN and API_TOKEN != "你的API令牌":
    print(f"API令牌已设置: {API_TOKEN[:5]}...{API_TOKEN[-5:]} (长度: {len(API_TOKEN)})")
else:
    print("警告: API令牌未设置或使用了默认值")

# API endpoints
DETECTION_API_URL = "https://api.deepdataspace.com/v2/task/dinox/detection"
REGION_VL_API_URL = "https://api.deepdataspace.com/v2/task/dinox/region_vl"
TASK_STATUS_API_URL = "https://api.deepdataspace.com/v2/task_status/{task_uuid}"

# 打印API端点
print(f"检测API端点: {DETECTION_API_URL}")
print(f"区域视觉语言API端点: {REGION_VL_API_URL}")
print(f"任务状态API端点: {TASK_STATUS_API_URL}")

def encode_image_to_base64(image):
    """
    Convert an image (numpy array or PIL Image) to base64 string
    """
    if isinstance(image, np.ndarray):
        # Convert numpy array to PIL Image
        image = Image.fromarray(image)
    
    # Convert PIL Image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def detect_objects_async(image, prompt_type="text", prompt_text=None, prompt_universal=None, 
                        targets=["bbox"], bbox_threshold=0.25, iou_threshold=0.8, session_id=None):
    """
    Create a detection task using the DINO-X API and return the task UUID
    按照最新API文档创建检测任务
    """
    if not API_TOKEN or API_TOKEN == "你的API令牌":
        raise ValueError("API token not found or using default value. Please set the DINOX_API_TOKEN environment variable.")
    
    # 准备图像数据
    image_data = image if isinstance(image, str) else encode_image_to_base64(image)
    
    # 准备提示结构
    prompt = {"type": prompt_type}
    if prompt_type == "text" and prompt_text:
        prompt["text"] = prompt_text
    elif prompt_type == "universal" and prompt_universal:
        prompt["universal"] = prompt_universal
    
    # 准备请求载荷
    payload = {
        "image": image_data,
        "targets": targets,
        "bbox_threshold": bbox_threshold,
        "iou_threshold": iou_threshold,
        "prompt": prompt,
        "model": "DINO-X-1.0"
    }
    
    if session_id:
        payload["session_id"] = session_id
    
    # 准备请求头
    headers = {
        "Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {DETECTION_API_URL}")
    print(f"Headers: {headers}")
    print(f"Payload keys: {list(payload.keys())}")
    
    # 尝试多种API调用方式
    try:
        print("尝试方式1: 使用requests.post的json参数")
        response = requests.post(DETECTION_API_URL, json=payload, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text[:500]}...")  # 只打印前500个字符
        
        if response.status_code != 200:
            print("尝试方式2: 使用requests.post的data参数和手动JSON序列化")
            json_payload = json.dumps(payload)
            response = requests.post(DETECTION_API_URL, data=json_payload, headers=headers)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")  # 只打印前500个字符
            
            if response.status_code != 200:
                print("尝试方式3: 按照官方文档示例使用json.dumps")
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    url=DETECTION_API_URL,
                    data=json.dumps(payload),
                    headers=headers
                )
                
                print(f"Response status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}...")  # 只打印前500个字符
    except Exception as e:
        print(f"API request error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    try:
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data)}")
        
        if response_data.get("code") != 0:
            raise Exception(f"API request failed: {response_data.get('msg')}")
        
        # 检查响应中是否包含task_uuid
        if 'data' not in response_data:
            raise Exception(f"API response missing 'data' field: {response_data}")
        
        # 检查是否包含task_uuid或uuid（兼容不同的API版本）
        if 'task_uuid' in response_data['data']:
            return response_data["data"]["task_uuid"]
        elif 'uuid' in response_data['data']:
            return response_data["data"]["uuid"]
        else:
            raise Exception(f"API response missing task identifier in 'data': {response_data['data']}")
    except json.JSONDecodeError:
        print(f"无法解析JSON响应: {response.text}")
        raise Exception("API返回了无效的JSON响应")

def get_task_result(task_uuid, max_retries=30, retry_interval=1):
    """
    Get the result of a task using the DINO-X API
    按照最新API文档获取任务结果
    """
    if not API_TOKEN or API_TOKEN == "你的API令牌":
        raise ValueError("API token not found or using default value. Please set the DINOX_API_TOKEN environment variable.")
    
    headers = {
        "Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"Checking status for task: {task_uuid}")
    
    for retry in range(max_retries):
        url = TASK_STATUS_API_URL.format(task_uuid=task_uuid)
        print(f"Request URL: {url}")
        print(f"Retry {retry+1}/{max_retries}")
        
        try:
            print(f"Sending GET request to {url}")
            response = requests.get(url, headers=headers)
            
            print(f"Response status code: {response.status_code}")
            if response.text:
                print(f"Response text: {response.text[:500]}...")  # 只打印前500个字符
            else:
                print("Response text is empty")
            
            if response.status_code != 200:
                print(f"API request failed with status code {response.status_code}")
                # Continue to retry instead of raising exception immediately
                time.sleep(retry_interval)
                continue
            
            try:
                response_data = response.json()
                print(f"Response data: {json.dumps(response_data)}")
                
                if response_data.get("code") != 0:
                    print(f"API request failed: {response_data.get('msg')}")
                    # Continue to retry instead of raising exception immediately
                    time.sleep(retry_interval)
                    continue
                
                # 检查响应中是否包含data字段
                if 'data' not in response_data:
                    print(f"API response missing 'data' field: {response_data}")
                    time.sleep(retry_interval)
                    continue
                
                data = response_data["data"]
                status = data.get("status")
                
                print(f"Task status: {status}")
                
                if status == "success":
                    # 检查响应中是否包含result字段
                    if 'result' not in data:
                        print(f"API response missing 'result' field in 'data': {data}")
                        # 尝试兼容不同的API版本
                        if 'objects' in data:
                            print("Found 'objects' directly in data, using it as result")
                            return {"objects": data.get("objects")}, data.get("session_id")
                        return {}, data.get("session_id")
                    
                    return data.get("result"), data.get("session_id")
                elif status == "failed":
                    error_msg = data.get("error", "Unknown error")
                    print(f"Task failed: {error_msg}")
                    raise Exception(f"Task failed: {error_msg}")
                elif status in ["waiting", "running"]:
                    print(f"Task is {status}, waiting...")
                else:
                    print(f"Unknown task status: {status}")
            except json.JSONDecodeError:
                print(f"无法解析JSON响应: {response.text}")
                time.sleep(retry_interval)
                continue
            
            print(f"Waiting {retry_interval} seconds before next retry...")
            time.sleep(retry_interval)
        except Exception as e:
            print(f"Error checking task status: {str(e)}")
            import traceback
            print(traceback.format_exc())
            time.sleep(retry_interval)
    
    raise Exception(f"Task timed out after {max_retries * retry_interval} seconds")

def detect_objects(image, prompt_type="text", prompt_text=None, prompt_universal=None, 
                  targets=["bbox"], bbox_threshold=0.25, iou_threshold=0.8, session_id=None):
    """
    Detect objects in an image using the DINO-X API
    """
    try:
        print(f"\n===== DINO-X API 调用开始 =====")
        print(f"提示类型: {prompt_type}")
        if prompt_type == "text":
            print(f"提示文本: {prompt_text}")
        else:
            print(f"通用提示值: {prompt_universal}")
        print(f"检测目标: {targets}")
        print(f"置信度阈值: {bbox_threshold}")
        print(f"IoU 阈值: {iou_threshold}")
        print(f"会话 ID: {session_id}")
        print(f"API URL: {DETECTION_API_URL}")
        
        # 检查 API 令牌
        if not API_TOKEN or API_TOKEN == "你的API令牌":
            print("警告: API 令牌未设置或使用了默认值")
        else:
            print(f"API 令牌: {API_TOKEN[:5]}...{API_TOKEN[-5:]} (已设置)")
        
        # 创建检测任务
        task_uuid = detect_objects_async(
            image, prompt_type, prompt_text, prompt_universal, 
            targets, bbox_threshold, iou_threshold, session_id
        )
        
        print(f"任务 UUID: {task_uuid}")
        
        # 获取任务结果
        result, new_session_id = get_task_result(task_uuid)
        
        print(f"检测完成, 会话 ID: {new_session_id}")
        
        # 打印完整的API响应，包括所有字段
        print("API响应完整数据:")
        if "objects" in result:
            for i, obj in enumerate(result["objects"]):
                print(f"\n对象 {i+1}:")
                for key, value in obj.items():
                    if key == "mask":
                        print(f"  {key}: {type(value)} - {value.keys() if isinstance(value, dict) else '非字典类型'}")
                    elif key in ["pose_keypoints", "hand_keypoints"]:
                        print(f"  {key}: {type(value)} - 长度: {len(value) if isinstance(value, list) else '非列表类型'}")
                    else:
                        print(f"  {key}: {value}")
        
        print(f"===== DINO-X API 调用结束 =====\n")
        
        return result, new_session_id
    
    except Exception as e:
        print(f"检测过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Return empty result but don't raise exception to avoid breaking the UI
        return {"objects": []}, session_id

def create_region_vl_task(image, regions, targets=["caption"], prompt_type=None, 
                         prompt_text=None, prompt_universal=None, session_id=None):
    """
    Create a region visual language task using the DINO-X API
    按照最新API文档创建区域视觉语言任务
    """
    if not API_TOKEN:
        raise ValueError("API token not found. Please set the DINOX_API_TOKEN environment variable.")
    
    # 准备图像数据
    image_data = image if isinstance(image, str) else encode_image_to_base64(image)
    
    # 准备请求载荷
    payload = {
        "image": image_data,
        "regions": regions,
        "targets": targets,
        "model": "DINO-X-1.0"
    }
    
    # 添加提示结构（如果提供）
    if prompt_type:
        prompt = {"type": prompt_type}
        if prompt_type == "text" and prompt_text:
            prompt["text"] = prompt_text
        elif prompt_type == "universal" and prompt_universal:
            prompt["universal"] = prompt_universal
        payload["prompt"] = prompt
    
    if session_id:
        payload["session_id"] = session_id
    
    # 准备请求头
    headers = {
        "Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {REGION_VL_API_URL}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps({k: v if k != 'image' else '...' for k, v in payload.items()})}")
    
    # 发送API请求 - 尝试两种方式
    try:
        # 方式1: 使用json参数（requests会自动处理JSON序列化）
        response = requests.post(REGION_VL_API_URL, json=payload, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code != 200:
            print("尝试替代方法...")
            # 方式2: 手动序列化JSON并使用data参数
            json_payload = json.dumps(payload)
            response = requests.post(REGION_VL_API_URL, data=json_payload, headers=headers)
            
            print(f"Alternative method response status code: {response.status_code}")
            print(f"Alternative method response text: {response.text}")
    except Exception as e:
        print(f"API request error: {str(e)}")
        raise
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    response_data = response.json()
    print(f"Response data: {json.dumps(response_data)}")
    
    if response_data.get("code") != 0:
        raise Exception(f"API request failed: {response_data.get('msg')}")
    
    # 检查响应中是否包含task_uuid
    if 'data' not in response_data:
        raise Exception(f"API response missing 'data' field: {response_data}")
    
    # 检查是否包含task_uuid或uuid（兼容不同的API版本）
    if 'task_uuid' in response_data['data']:
        return response_data["data"]["task_uuid"]
    elif 'uuid' in response_data['data']:
        return response_data["data"]["uuid"]
    else:
        raise Exception(f"API response missing task identifier in 'data': {response_data['data']}")

def get_region_descriptions(image, regions, targets=["caption"], prompt_type=None, 
                           prompt_text=None, prompt_universal=None, session_id=None):
    """
    Get descriptions for regions in an image using the DINO-X API
    """
    try:
        print(f"Starting region descriptions with targets={targets}, regions count={len(regions)}")
        
        # Create region VL task
        task_uuid = create_region_vl_task(
            image, regions, targets, prompt_type, prompt_text, prompt_universal, session_id
        )
        
        print(f"Region VL task created with UUID: {task_uuid}")
        
        # Get task status
        result, new_session_id = get_task_result(task_uuid)
        
        print(f"Region descriptions completed, session_id: {new_session_id}")
        
        return result, new_session_id
    
    except Exception as e:
        print(f"Error in get_region_descriptions: {str(e)}")
        # Return empty result but don't raise exception to avoid breaking the UI
        return {"objects": []}, session_id 