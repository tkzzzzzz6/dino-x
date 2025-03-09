import os
import socket
import subprocess
import signal
import sys
import time

# 全局变量，用于跟踪子进程
streamlit_process = None

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    print("\n接收到停止信号，正在关闭服务...")
    if streamlit_process:
        print(f"终止Streamlit进程 (PID: {streamlit_process.pid})...")
        try:
            # 尝试优雅地终止进程
            streamlit_process.terminate()
            # 等待进程终止，最多等待5秒
            for _ in range(5):
                if streamlit_process.poll() is not None:
                    break
                time.sleep(1)
            # 如果进程仍在运行，强制终止
            if streamlit_process.poll() is None:
                print("Streamlit进程未响应，强制终止...")
                streamlit_process.kill()
        except Exception as e:
            print(f"终止进程时出错: {e}")
    print("服务已停止")
    sys.exit(0)

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
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 获取本机 IP
    local_ip = get_local_ip()
    
    # 设置 Streamlit 启动参数
    port = 8501  # 默认 Streamlit 端口
    
    print(f"启动 DINO-X 图像检测服务...")
    print(f"本机 IP 地址: {local_ip}")
    print(f"应用将在以下地址可访问: http://{local_ip}:{port}")
    print("其他设备可以通过上述地址在浏览器中访问此应用")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 启动 Streamlit 应用，指定主机为 0.0.0.0（允许所有网络接口访问）
        streamlit_process = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时打印Streamlit输出
        while True:
            output = streamlit_process.stdout.readline()
            if output == '' and streamlit_process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 等待进程结束
        return_code = streamlit_process.poll()
        print(f"Streamlit进程已退出，返回码: {return_code}")
    
    except KeyboardInterrupt:
        # 这里不需要做任何事情，因为信号处理器会处理Ctrl+C
        pass
    except Exception as e:
        print(f"启动Streamlit时出错: {e}")
    finally:
        # 确保在任何情况下都会清理进程
        if streamlit_process and streamlit_process.poll() is None:
            try:
                streamlit_process.terminate()
                streamlit_process.wait(timeout=5)
            except:
                streamlit_process.kill()
                streamlit_process.wait() 