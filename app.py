import streamlit as st
import cv2
import numpy as np
import time
import os
from PIL import Image
import io
import base64
import json
from dotenv import load_dotenv

# Import custom modules
from dinox_api import detect_objects, encode_image_to_base64
from visualization import visualize_detection_results, create_detection_summary

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="DINO-X 图像检测",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2196F3;
        margin-bottom: 1rem;
    }
    .info-text {
        font-size: 1rem;
        color: #555;
    }
    .highlight {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .detection-summary {
        background-color: #e6f7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
    }
    .top-objects {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'last_detection_time' not in st.session_state:
    st.session_state.last_detection_time = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

# Main application header
st.markdown("<h1 class='main-header'>DINO-X 图像检测</h1>", unsafe_allow_html=True)

# Create sidebar for configuration
with st.sidebar:
    st.markdown("<h2 class='sub-header'>配置</h2>", unsafe_allow_html=True)
    
    # API information
    st.info('DINO-X API 设计为一次处理一张图片。上传图片并点击"分析图像"按钮进行检测。')
    
    # API token status
    token_status = "已设置 ✅" if os.getenv("DINOX_API_TOKEN") else "未设置 ❌"
    st.warning(f"API 令牌状态: {token_status}")
    
    if not os.getenv("DINOX_API_TOKEN"):
        api_token = st.text_input("输入 API 令牌", type="password")
        if api_token:
            os.environ["DINOX_API_TOKEN"] = api_token
            st.success("API 令牌已设置！请刷新页面。")
            st.experimental_rerun()
    else:
        # Add API token validation
        if st.button("验证 API 令牌", key="validate_token"):
            try:
                # Create a simple test image
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                test_image[40:60, 40:60] = [255, 255, 255]  # White square
                
                # Test API connection
                with st.spinner("正在验证 API 令牌..."):
                    result, _ = detect_objects(
                        test_image,
                        prompt_type="universal",
                        prompt_universal=1,
                        targets=["bbox"],
                        bbox_threshold=0.1
                    )
                
                st.success("API 令牌有效！")
            except Exception as e:
                st.error(f"API 令牌验证失败: {str(e)}")
                if "401" in str(e):
                    st.error("错误 401: 未授权。请检查您的 API 令牌是否正确。")
                elif "403" in str(e):
                    st.error("错误 403: 禁止访问。您的 API 令牌可能没有足够的权限。")
                elif "429" in str(e):
                    st.error("错误 429: 请求过多。您已超出 API 调用限制，请稍后再试。")
        
        # Add option to change API token
        if st.checkbox("更改 API 令牌", value=False):
            new_api_token = st.text_input("输入新的 API 令牌", type="password")
            if new_api_token:
                os.environ["DINOX_API_TOKEN"] = new_api_token
                st.success("API 令牌已更新！请刷新页面。")
                st.experimental_rerun()
    
    # Prompt type
    st.markdown("<h3>检测参数</h3>", unsafe_allow_html=True)
    prompt_type = st.radio("提示类型", ["文本提示", "通用提示"], index=0)
    prompt_type_value = "text" if prompt_type == "文本提示" else "universal"
    
    # Text prompt
    if prompt_type == "文本提示":
        # Add preset prompts
        preset_prompts = {
            "人物检测": "person.man.woman.child",
            "人物和配件": "person.man.woman.child.glasses.hat.headphones",
            "常见物品": "person.car.dog.cat.chair.table.phone.laptop",
            "室内场景": "person.chair.table.sofa.tv.laptop.phone.cup",
            "自定义": "custom"
        }
        
        selected_preset = st.selectbox("选择预设提示词", list(preset_prompts.keys()))
        
        if selected_preset == "自定义":
            prompt_text = st.text_input("文本提示 (用点号分隔)", "person.headphones.man")
        else:
            prompt_text = preset_prompts[selected_preset]
            st.info(f"当前提示词: {prompt_text}")
    else:
        prompt_text = None
    
    # Detection targets
    st.markdown("<h3>检测目标</h3>", unsafe_allow_html=True)
    
    # 简化为只有边界框检测
    bbox = st.checkbox("边界框", value=True, key="target_bbox")
    
    # 始终包含bbox目标
    targets = ["bbox"]
    
    # 置信度阈值
    confidence_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.25, 0.05)
    
    # 简化可视化选项，只保留边界框显示
    st.markdown("<h3>可视化选项</h3>", unsafe_allow_html=True)
    show_bbox = st.checkbox("显示边界框", value=True, key="show_bbox")
    show_caption = st.checkbox("显示描述", value=True, key="show_caption")

# Create main content area with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 class='sub-header'>上传图像</h2>", unsafe_allow_html=True)
    
    # 使用单选按钮替代tabs
    input_method = st.radio("选择输入方式", ["上传图像文件", "输入图像 URL"])
    
    if input_method == "上传图像文件":
        # Image upload
        uploaded_file = st.file_uploader("选择图像文件", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                # Read the image
                image = Image.open(uploaded_file)
                
                # Convert to numpy array for processing
                image_np = np.array(image)
                
                # Store the image in session state
                st.session_state.uploaded_image = image_np
                
                # Display the image
                st.image(image_np, caption="上传的图像", use_column_width=True)
                
                # Image adjustments
                st.markdown("<h3>图像调整</h3>", unsafe_allow_html=True)
                
                # Add auto-enhance option
                auto_enhance = st.checkbox("自动增强图像", value=False, help="自动调整亮度、对比度和锐度以提高检测成功率")

                if auto_enhance:
                    # Apply automatic image enhancement
                    # Convert to LAB color space for better enhancement
                    lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)
                    # Split the LAB channels
                    l, a, b = cv2.split(lab)
                    # Apply CLAHE to L channel
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    cl = clahe.apply(l)
                    # Merge the enhanced L channel with the original A and B channels
                    enhanced_lab = cv2.merge((cl, a, b))
                    # Convert back to RGB
                    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
                    
                    # Apply sharpening
                    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                    enhanced_image = cv2.filter2D(enhanced_image, -1, kernel * 0.5)
                    
                    # Store the enhanced image
                    st.session_state.processed_image = enhanced_image
                    
                    # Display the enhanced image
                    st.image(enhanced_image, caption="自动增强后的图像", use_column_width=True)
                else:
                    # Manual adjustments
                    # Create columns for adjustment controls
                    adj_col1, adj_col2 = st.columns(2)
                    
                    with adj_col1:
                        # Brightness adjustment
                        brightness = st.slider("亮度", -100, 100, 0, 5)
                        
                        # Contrast adjustment
                        contrast = st.slider("对比度", -100, 100, 0, 5)
                    
                    with adj_col2:
                        # Saturation adjustment
                        saturation = st.slider("饱和度", -100, 100, 0, 5)
                        
                        # Sharpness adjustment
                        sharpness = st.slider("锐度", 0, 100, 0, 5)
                    
                    # Apply adjustments to the image
                    adjusted_image = image_np.copy()
                    
                    # Apply brightness adjustment
                    if brightness != 0:
                        hsv = cv2.cvtColor(adjusted_image, cv2.COLOR_RGB2HSV)
                        h, s, v = cv2.split(hsv)
                        
                        if brightness > 0:
                            v = np.clip(v + brightness * 2.55, 0, 255).astype(np.uint8)
                        else:
                            v = np.clip(v - abs(brightness) * 2.55, 0, 255).astype(np.uint8)
                        
                        hsv = cv2.merge((h, s, v))
                        adjusted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                    
                    # Apply contrast adjustment
                    if contrast != 0:
                        f = 131 * (contrast + 127) / (127 * (131 - contrast))
                        alpha_c = f
                        gamma_c = 127 * (1 - f)
                        
                        adjusted_image = cv2.addWeighted(adjusted_image, alpha_c, adjusted_image, 0, gamma_c)
                    
                    # Apply saturation adjustment
                    if saturation != 0:
                        hsv = cv2.cvtColor(adjusted_image, cv2.COLOR_RGB2HSV)
                        h, s, v = cv2.split(hsv)
                        
                        if saturation > 0:
                            s = np.clip(s + saturation * 2.55, 0, 255).astype(np.uint8)
                        else:
                            s = np.clip(s - abs(saturation) * 2.55, 0, 255).astype(np.uint8)
                        
                        hsv = cv2.merge((h, s, v))
                        adjusted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                    
                    # Apply sharpness adjustment
                    if sharpness > 0:
                        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                        adjusted_image = cv2.filter2D(adjusted_image, -1, kernel * (sharpness / 100))
                    
                    # Store the adjusted image
                    st.session_state.processed_image = adjusted_image
                    
                    # Display the adjusted image if any adjustments were made
                    if brightness != 0 or contrast != 0 or saturation != 0 or sharpness > 0:
                        st.image(adjusted_image, caption="调整后的图像", use_column_width=True)

                # Add image resize option
                resize_image = st.checkbox("调整图像尺寸", value=False, help="调整图像尺寸可能会影响检测效果")

                if resize_image:
                    # Get the current image
                    current_image = st.session_state.processed_image if st.session_state.processed_image is not None else image_np
                    
                    # Get original dimensions
                    h, w = current_image.shape[:2]
                    
                    # Create a slider for resize factor
                    resize_factor = st.slider("调整比例", 0.1, 2.0, 1.0, 0.1)
                    
                    if resize_factor != 1.0:
                        # Calculate new dimensions
                        new_w = int(w * resize_factor)
                        new_h = int(h * resize_factor)
                        
                        # Resize the image
                        resized_image = cv2.resize(current_image, (new_w, new_h))
                        
                        # Store the resized image
                        st.session_state.processed_image = resized_image
                        
                        # Display the resized image
                        st.image(resized_image, caption=f"调整后的图像 ({new_w}x{new_h})", use_column_width=True)

                # Add a button to analyze the image
                if st.button("🔍 分析图像", key="analyze_image", use_container_width=True):
                    with st.spinner("正在分析图像..."):
                        # Record start time
                        start_time = time.time()
                        
                        # Get the image to analyze
                        image_to_analyze = st.session_state.processed_image if st.session_state.processed_image is not None else st.session_state.uploaded_image
                        
                        # Perform detection
                        prompt_universal = 1 if prompt_type_value == "universal" else None
                        result, session_id = detect_objects(
                            image_to_analyze,
                            prompt_type=prompt_type_value,
                            prompt_text=prompt_text,
                            prompt_universal=prompt_universal,
                            targets=["bbox"],  # 只使用边界框检测
                            bbox_threshold=confidence_threshold
                        )
                        
                        # Calculate detection time
                        detection_time = time.time() - start_time
                        
                        # Store results in session state
                        st.session_state.detection_results = result
                        st.session_state.session_id = session_id
                        st.session_state.last_detection_time = detection_time
                        
                        # Show success message
                        if "objects" in result and result["objects"]:
                            st.success(f"成功检测到 {len(result['objects'])} 个对象！")
                        else:
                            st.warning("未检测到任何对象。尝试调整提示词或降低置信度阈值。")

                # Add a button for universal detection (fallback)
                if st.button("🌐 通用检测 (检测所有物体)", key="universal_detection", use_container_width=True):
                    with st.spinner("正在进行通用检测..."):
                        # Record start time
                        start_time = time.time()
                        
                        # Get the image to analyze
                        image_to_analyze = st.session_state.processed_image if st.session_state.processed_image is not None else st.session_state.uploaded_image
                        
                        # 只使用边界框检测
                        bbox_targets = ["bbox"]
                        
                        # Perform detection with universal mode
                        result, session_id = detect_objects(
                            image_to_analyze,
                            prompt_type="universal",
                            prompt_universal=1,
                            targets=bbox_targets,  # 只使用边界框检测
                            bbox_threshold=0.05  # 使用更低的阈值
                        )
                        
                        # Calculate detection time
                        detection_time = time.time() - start_time
                        
                        # Store results in session state
                        st.session_state.detection_results = result
                        st.session_state.session_id = session_id
                        st.session_state.last_detection_time = detection_time
                        
                        # Show success message
                        if "objects" in result and result["objects"]:
                            st.success(f"成功检测到 {len(result['objects'])} 个对象！")
                        else:
                            st.error("通用检测也未能检测到任何对象。请检查图像质量或 API 连接。")
            
            except Exception as e:
                st.error(f"处理图像时出错: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
    
    elif input_method == "输入图像 URL":
        # Image URL input
        image_url = st.text_input("输入图像 URL", "")
        
        if image_url:
            try:
                # Add a button to fetch the image
                if st.button("获取图像", key="fetch_image"):
                    with st.spinner("正在获取图像..."):
                        # Download the image
                        import requests
                        from io import BytesIO
                        
                        response = requests.get(image_url)
                        if response.status_code != 200:
                            st.error(f"获取图像失败: HTTP 状态码 {response.status_code}")
                        else:
                            # Open the image
                            image = Image.open(BytesIO(response.content))
                            
                            # Convert to numpy array for processing
                            image_np = np.array(image)
                            
                            # Store the image in session state
                            st.session_state.uploaded_image = image_np
                            
                            # Display the image
                            st.image(image_np, caption="从 URL 获取的图像", use_column_width=True)
            except Exception as e:
                st.error(f"处理图像 URL 时出错: {str(e)}")

    # Check if an image is uploaded or fetched
    if 'uploaded_image' in st.session_state and st.session_state.uploaded_image is not None:
        # Image adjustments
        st.markdown("<h3>图像调整</h3>", unsafe_allow_html=True)

with col2:
    st.markdown("<h2 class='sub-header'>检测结果</h2>", unsafe_allow_html=True)
    
    # 显示检测结果
    if 'detection_results' in st.session_state and st.session_state.detection_results:
        result = st.session_state.detection_results
        
        # 显示检测时间
        if 'last_detection_time' in st.session_state:
            st.info(f"检测耗时: {st.session_state.last_detection_time:.2f} 秒")
        
        # 显示会话ID
        if 'session_id' in st.session_state and st.session_state.session_id:
            st.info(f"会话 ID: {st.session_state.session_id}")
        
        # 显示检测结果摘要
        if "objects" in result and result["objects"]:
            st.success(f"检测到 {len(result['objects'])} 个对象")
            
            # 显示检测结果可视化
            if 'uploaded_image' in st.session_state and st.session_state.uploaded_image is not None:
                # 获取原始图像
                original_image = st.session_state.processed_image if st.session_state.processed_image is not None else st.session_state.uploaded_image
                
                # 简化显示选项，只保留边界框和描述
                st.markdown("<h3>显示选项</h3>", unsafe_allow_html=True)
                result_show_bbox = st.checkbox("显示边界框", value=True, key="result_show_bbox")
                result_show_caption = st.checkbox("显示描述", value=True, key="result_show_caption")
                
                # 可视化检测结果，只使用边界框和描述
                visualized_image = visualize_detection_results(
                    original_image, 
                    result["objects"],
                    show_bbox=result_show_bbox,
                    show_mask=False,  # 不显示掩码
                    show_pose=False,  # 不显示姿态
                    show_hand=False,  # 不显示手部
                    show_caption=result_show_caption
                )
                
                # 显示可视化结果
                st.image(visualized_image, caption="检测结果", use_column_width=True)
                
                # 添加保存按钮
                if st.button("💾 保存结果", key="save_image", use_container_width=True):
                    try:
                        # Convert the visualized image to PIL Image
                        pil_image = Image.fromarray(visualized_image)
                        
                        # Create a BytesIO object
                        buf = io.BytesIO()
                        pil_image.save(buf, format="PNG")
                        
                        # Get the byte value
                        byte_im = buf.getvalue()
                        
                        # Create a download button
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        filename = f"dinox_analysis_{timestamp}.png"
                        st.download_button(
                            label="📥 下载图像",
                            data=byte_im,
                            file_name=filename,
                            mime="image/png",
                            key="download_button"
                        )
                        
                        st.success(f"图像已准备好下载: {filename}")
                    except Exception as e:
                        st.error(f"保存图像时出错: {str(e)}")
                
                # 显示检测结果详情
                with st.expander("检测结果详情", expanded=False):
                    summary = create_detection_summary(result["objects"])
                    st.markdown(summary)

                # 显示原始JSON结果（作为单独的expander，不嵌套）
                with st.expander("原始JSON结果", expanded=False):
                    st.json(result)
            else:
                st.warning("无法显示检测结果可视化，因为没有上传图像")
        else:
            st.warning("未检测到任何对象")
    else:
        st.info("请上传图像并点击分析按钮")
    
    # Add debug information
    with st.expander("调试信息"):
        st.markdown("### API 调用信息")
        st.write("API 令牌状态:", "已设置" if os.getenv("DINOX_API_TOKEN") else "未设置")
        st.write("提示类型:", prompt_type_value)
        if prompt_type_value == "text":
            st.write("提示文本:", prompt_text)
        else:
            st.write("通用提示值:", "1 (粗力度检测万物)")
        st.write("检测目标:", targets)
        st.write("置信度阈值:", confidence_threshold)
        
        if st.session_state.last_detection_time is not None:
            st.write("检测时间:", f"{st.session_state.last_detection_time:.2f} 秒")
        
        if st.session_state.session_id:
            st.write("会话 ID:", st.session_state.session_id)
        
        # Add a button to test API connection
        if st.button("测试 API 连接", key="test_api"):
            try:
                # Create a simple test image
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                test_image[40:60, 40:60] = [255, 255, 255]  # White square
                
                # Test API connection
                with st.spinner("正在测试 API 连接..."):
                    result, _ = detect_objects(
                        test_image,
                        prompt_type="universal",
                        prompt_universal=1,
                        targets=["bbox"],
                        bbox_threshold=0.1
                    )
                
                st.success("API 连接成功!")
                st.write("API 响应:", result)
            except Exception as e:
                st.error(f"API 连接失败: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Add information about the application
st.markdown("<h2 class='sub-header'>关于</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='highlight'>
    <p class='info-text'>
        本演示应用使用 DINO-X API 进行图像对象检测、分割、姿态估计等。
        DINO-X 支持开放集目标检测与分割、短语定位、视觉提示计数和姿态估计。
    </p>
    <p class='info-text'>
        <b>使用方法：</b>
        1. 上传图像文件
        2. 配置检测参数（提示类型、检测目标等）
        3. 调整图像参数（可选）
        4. 点击'分析图像'按钮
        5. 查看检测结果和分析
    </p>
    <p class='info-text'>
        <b>功能特点：</b>
        • 图像上传和调整
        • 多种检测目标：边界框、分割掩码、姿态关键点、手部关键点
        • 可视化检测结果
        • 结果保存和下载
        • 详细的检测摘要
    </p>
</div>
""", unsafe_allow_html=True)

# Create a footer with API information
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888;">
    <p>DINO-X API 由 DeepDataSpace 提供</p>
    <p>本应用程序仅用于演示目的</p>
</div>
""", unsafe_allow_html=True)

# 在页面最底部添加访问计数组件
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
    <span>
        <img src="https://count.getloli.com/@tkzzzzzz6?name=tkzzzzzz6&theme=rule34&padding=8&offset=0&align=top&scale=1&pixelated=1&darkmode=auto" alt="访问计数" />
    </span>
</div>
<div style="text-align: center; font-size: 12px; color: #888;">
    © 2025 Ke Tan ->DINO-X 图像分析工具 | 由 Streamlit 提供支持
</div>
""", unsafe_allow_html=True) 