import os
import socket
import subprocess

def get_local_ip():
    """获取本机局域网 IP 地址"""
    try:
        # 创建一个临时 socket 连接到外部，以获取本机在局域网中的 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # 如果获取失败，返回本地回环地址

if __name__ == "__main__":
    # 获取本机 IP
    local_ip = get_local_ip()
    
    # 设置 Streamlit 启动参数
    port = 8501  # 默认 Streamlit 端口
    
    print(f"启动 DINO-X 图像检测服务...")
    print(f"本机 IP 地址: {local_ip}")
    print(f"应用将在以下地址可访问: http://{local_ip}:{port}")
    print("其他设备可以通过上述地址在浏览器中访问此应用")
    print("按 Ctrl+C 停止服务")
    
    # 启动 Streamlit 应用，指定主机为 0.0.0.0（允许所有网络接口访问）
    subprocess.run(["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", str(port)]) 