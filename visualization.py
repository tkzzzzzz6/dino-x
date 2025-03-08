import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors
import random
from PIL import Image, ImageDraw, ImageFont
import io

# Define a color palette for visualization
COLORS = list(mcolors.TABLEAU_COLORS.values())

def get_color(idx):
    """Get a color from the predefined color palette"""
    return COLORS[idx % len(COLORS)]

def decode_rle_mask(rle, shape):
    """
    Decode a run-length encoded mask in COCO RLE format
    
    COCO RLE格式说明:
    1. counts: 可以是字符串或整数数组
    2. 如果是字符串，它是一个压缩的RLE编码
    3. 如果是整数数组，它表示交替的0和1的像素数量
    """
    if rle is None:
        return None
    
    counts = rle.get("counts")
    size = rle.get("size")
    
    if not counts or not size:
        return None
    
    try:
        # 创建空白掩码
        mask = np.zeros((size[0], size[1]), dtype=np.uint8)
        
        # 检查counts是否为字符串（压缩格式）
        if isinstance(counts, str):
            try:
                # 尝试使用pycocotools解码（如果可用）
                try:
                    from pycocotools import mask as mask_util
                    binary_mask = mask_util.decode({'size': size, 'counts': counts.encode('utf-8')})
                    return binary_mask
                except ImportError:
                    print("pycocotools not available, using fallback method")
                    
                # 如果pycocotools不可用，使用备用方法
                # 这是一个简单的实现，可能不支持所有COCO RLE格式
                # 将压缩的RLE转换为整数数组
                import zlib
                import struct
                
                # 尝试解压缩（如果是压缩的）
                try:
                    decoded = zlib.decompress(counts.encode('ascii'))
                    counts_array = struct.unpack('<%dI' % (len(decoded) // 4), decoded)
                except Exception as e:
                    print(f"Failed to decompress RLE: {e}")
                    # 如果解压缩失败，尝试直接解析
                    counts_array = []
                    for count_str in counts.split():
                        try:
                            counts_array.append(int(count_str))
                        except ValueError:
                            # 如果无法解析为整数，可能是使用了其他编码
                            print(f"Warning: Could not parse count '{count_str}' as integer")
                            return None
            except Exception as e:
                print(f"Error decoding compressed RLE: {e}")
                return None
        else:
            # 如果counts已经是数组，直接使用
            counts_array = counts
        
        # 解码RLE
        idx = 0
        val = 0
        for count in counts_array:
            end_idx = min(idx + count, size[0] * size[1])
            mask.flat[idx:end_idx] = val
            idx = end_idx
            val = 1 - val
        
        # 调整掩码大小以匹配图像形状
        if shape != size:
            mask = cv2.resize(mask, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
        
        return mask
    
    except Exception as e:
        print(f"Error decoding RLE mask: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def draw_bbox(image, bbox, label=None, score=None, color=None):
    """
    Draw a bounding box on an image
    """
    if color is None:
        color = random.choice(COLORS)
    
    # Convert color from matplotlib format to BGR
    if isinstance(color, str):
        rgb = mcolors.to_rgb(color)
        color = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
    
    # Extract coordinates
    x1, y1, x2, y2 = map(int, bbox)
    
    # Draw rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    
    # Draw label if provided
    if label:
        text = label
        if score is not None:
            text += f" {score:.2f}"
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw text background
        cv2.rectangle(image, (x1, y1 - text_height - 5), (x1 + text_width, y1), color, -1)
        
        # Draw text
        cv2.putText(image, text, (x1, y1 - 5), font, font_scale, (255, 255, 255), thickness)
    
    return image

def draw_mask(image, mask, color=None, alpha=0.5):
    """
    Draw a segmentation mask on an image
    """
    if mask is None:
        return image
    
    if color is None:
        color = random.choice(COLORS)
    
    # Convert color from matplotlib format to BGR
    if isinstance(color, str):
        rgb = mcolors.to_rgb(color)
        color = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
    
    # Create a colored mask
    colored_mask = np.zeros_like(image)
    colored_mask[mask > 0] = color
    
    # Blend the mask with the image
    cv2.addWeighted(colored_mask, alpha, image, 1 - alpha, 0, image)
    
    return image

def draw_keypoints(image, keypoints, connections=None, color=None):
    """
    Draw keypoints and connections on an image
    
    keypoints: 可能是以下格式之一:
    1. 扁平列表: [x1, y1, v1, s1, x2, y2, v2, s2, ...]
    2. 嵌套列表: [[x1, y1, v1, s1], [x2, y2, v2, s2], ...]
    3. 字典列表: [{"x": x1, "y": y1, "visible": v1, "score": s1}, ...]
    """
    if keypoints is None or len(keypoints) == 0:
        print("Warning: No keypoints to draw")
        return image
    
    # Make a copy of the image to avoid modifying the original
    vis_image = image.copy()
    
    # If color is not provided, use a default color
    if color is None:
        color = (0, 255, 0)  # Green
    
    try:
        print(f"Keypoints data type: {type(keypoints)}")
        print(f"Keypoints data: {keypoints[:20] if isinstance(keypoints, list) else keypoints}")
        
        # 转换关键点为标准格式: [[x, y, visible, score], ...]
        formatted_keypoints = []
        
        # 检查关键点格式
        if isinstance(keypoints, list):
            if len(keypoints) == 0:
                return vis_image
                
            # 检查是否为扁平列表
            if not isinstance(keypoints[0], (list, dict)):
                # 扁平列表: [x1, y1, v1, s1, x2, y2, v2, s2, ...]
                for i in range(0, len(keypoints), 4):
                    if i + 3 < len(keypoints):
                        x, y, v, s = keypoints[i:i+4]
                        formatted_keypoints.append([x, y, v, s])
            
            # 检查是否为嵌套列表
            elif isinstance(keypoints[0], list):
                # 嵌套列表: [[x1, y1, v1, s1], [x2, y2, v2, s2], ...]
                formatted_keypoints = keypoints
            
            # 检查是否为字典列表
            elif isinstance(keypoints[0], dict):
                # 字典列表: [{"x": x1, "y": y1, "visible": v1, "score": s1}, ...]
                for kp in keypoints:
                    x = kp.get("x", 0)
                    y = kp.get("y", 0)
                    v = kp.get("visible", 0)
                    s = kp.get("score", 0)
                    formatted_keypoints.append([x, y, v, s])
        else:
            print(f"Unsupported keypoints format: {type(keypoints)}")
            return vis_image
        
        print(f"Formatted keypoints: {formatted_keypoints[:5]}")
        
        # 绘制关键点
        for i, kp in enumerate(formatted_keypoints):
            x, y, visible, score = kp
            
            # 只绘制可见的关键点
            if visible > 0 and score > 0.1:
                cv2.circle(vis_image, (int(x), int(y)), 5, color, -1)
                
                # 可选: 绘制关键点索引
                # cv2.putText(vis_image, str(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 绘制连接线
        if connections is not None:
            for connection in connections:
                idx1, idx2 = connection
                
                if idx1 < len(formatted_keypoints) and idx2 < len(formatted_keypoints):
                    kp1 = formatted_keypoints[idx1]
                    kp2 = formatted_keypoints[idx2]
                    
                    x1, y1, v1, s1 = kp1
                    x2, y2, v2, s2 = kp2
                    
                    # 只绘制两个端点都可见的连接线
                    if v1 > 0 and v2 > 0 and s1 > 0.1 and s2 > 0.1:
                        cv2.line(vis_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        
        return vis_image
    
    except Exception as e:
        print(f"Error in draw_keypoints: {e}")
        import traceback
        print(traceback.format_exc())
        return image

def visualize_detection_results(image, objects, show_bbox=True, show_mask=True, 
                               show_pose=True, show_hand=True, show_caption=True):
    """
    Visualize detection results on an image
    """
    if objects is None or not objects:
        return image
    
    # Make a copy of the image to avoid modifying the original
    vis_image = image.copy()
    
    # Process each detected object
    for i, obj in enumerate(objects):
        # Get a color for this object
        color = get_color(i)
        
        # Get the bounding box
        bbox = obj.get("bbox")
        category = obj.get("category", "object")
        score = obj.get("score", 1.0)
        
        # Draw bounding box
        if show_bbox and bbox:
            vis_image = draw_bbox(vis_image, bbox, category, score, color)
        
        # Draw mask
        if show_mask and "mask" in obj and obj["mask"]:
            try:
                print(f"Processing mask for object {i} (category: {category})")
                print(f"Mask data: {obj['mask']}")
                
                mask = decode_rle_mask(obj["mask"], vis_image.shape[:2])
                
                if mask is not None:
                    vis_image = draw_mask(vis_image, mask, color)
                else:
                    print(f"Warning: Failed to decode mask for object {i}")
            except Exception as e:
                print(f"Error processing mask for object {i}: {e}")
                import traceback
                print(traceback.format_exc())
        
        # Draw pose keypoints
        if show_pose and "pose_keypoints" in obj and obj["pose_keypoints"]:
            try:
                keypoints = obj["pose_keypoints"]
                connections = [
                    (0, 1), (0, 2), (1, 3), (2, 4),  # Face
                    (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
                    (5, 6), (5, 11), (6, 12), (11, 12),  # Torso
                    (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
                ]
                vis_image = draw_keypoints(vis_image, keypoints, connections, color)
            except Exception as e:
                print(f"Error drawing pose keypoints: {e}")
        
        # Draw hand keypoints
        if show_hand and "hand_keypoints" in obj and obj["hand_keypoints"]:
            try:
                keypoints = obj["hand_keypoints"]
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
                    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
                    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
                    (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky finger
                ]
                vis_image = draw_keypoints(vis_image, keypoints, connections, color)
            except Exception as e:
                print(f"Error drawing hand keypoints: {e}")
        
        # Draw caption
        if show_caption and "caption" in obj and obj["caption"]:
            try:
                # Get the caption
                caption = obj["caption"]
                
                # Get the top-left corner of the bounding box
                if bbox:
                    x, y = int(bbox[0]), int(bbox[1])
                else:
                    # If no bounding box, use a default position
                    x, y = 10, 10 + i * 20
                
                # Draw the caption
                cv2.putText(vis_image, caption, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            except Exception as e:
                print(f"Error drawing caption: {e}")
    
    return vis_image

def create_detection_summary(objects):
    """
    Create a text summary of detection results
    """
    if not objects:
        return "No objects detected."
    
    summary = f"Detected {len(objects)} objects:\n"
    
    for i, obj in enumerate(objects):
        category = obj.get("category", "unknown")
        score = obj.get("score", 0)
        
        summary += f"{i+1}. {category} (confidence: {score:.2f})"
        
        if "caption" in obj:
            summary += f" - {obj['caption']}"
        
        summary += "\n"
    
    return summary 