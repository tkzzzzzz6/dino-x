# Add information about the application
st.markdown("<h2 class='sub-header'>关于</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='highlight'>
    <p class='info-text'>
        本演示应用使用 DINO-X API 进行实时视频对象检测、分割、姿态估计等。
        DINO-X 支持开放集目标检测与分割、短语定位、视觉提示计数和姿态估计。
    </p>
    <p class='info-text'>
        <b>使用方法：</b>
        1. 选择输入源（网络摄像头或视频文件）
        2. 配置检测参数（提示类型、检测目标等）
        3. 点击'捕获并分析当前帧'按钮分析当前视频帧
        4. 查看右侧的检测结果和分析
    </p>
    <p class='info-text'>
        <b>功能特点：</b>
        • 实时视频显示
        • 按需图像分析
        • 多种检测目标：边界框、分割掩码、姿态关键点、手部关键点
        • 区域文本描述
        • 检测历史记录
    </p>
</div>
""", unsafe_allow_html=True) 