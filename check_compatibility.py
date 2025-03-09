#!/usr/bin/env python3
"""
检查应用程序中使用的Streamlit功能与指定版本的兼容性
"""

import os
import re
import sys
import pkg_resources
import importlib

def get_installed_streamlit_version():
    """获取已安装的Streamlit版本"""
    try:
        return pkg_resources.get_distribution("streamlit").version
    except pkg_resources.DistributionNotFound:
        return None

def check_streamlit_features(file_path):
    """检查文件中使用的Streamlit功能"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用了tabs功能
    tabs_pattern = r'st\.tabs\('
    uses_tabs = bool(re.search(tabs_pattern, content))
    
    # 检查其他可能的新功能
    features = {
        'tabs': uses_tabs,
        'columns': bool(re.search(r'st\.columns\(', content)),
        'expander': bool(re.search(r'st\.expander\(', content)),
        'checkbox': bool(re.search(r'st\.checkbox\(', content)),
        'selectbox': bool(re.search(r'st\.selectbox\(', content)),
        'multiselect': bool(re.search(r'st\.multiselect\(', content)),
        'radio': bool(re.search(r'st\.radio\(', content)),
        'button': bool(re.search(r'st\.button\(', content)),
        'download_button': bool(re.search(r'st\.download_button\(', content)),
        'file_uploader': bool(re.search(r'st\.file_uploader\(', content)),
        'camera_input': bool(re.search(r'st\.camera_input\(', content)),
        'form': bool(re.search(r'st\.form\(', content)),
        'session_state': bool(re.search(r'st\.session_state', content)),
    }
    
    return features

def check_feature_compatibility(features, version):
    """检查功能与指定版本的兼容性"""
    compatibility_issues = []
    
    # 版本引入功能的映射
    feature_versions = {
        'tabs': '1.12.0',
        'columns': '0.80.0',
        'expander': '0.83.0',
        'checkbox': '0.1.0',
        'selectbox': '0.1.0',
        'multiselect': '0.27.0',
        'radio': '0.1.0',
        'button': '0.1.0',
        'download_button': '0.88.0',
        'file_uploader': '0.1.0',
        'camera_input': '1.10.0',
        'form': '0.86.0',
        'session_state': '0.84.0',
    }
    
    for feature, used in features.items():
        if used and feature in feature_versions:
            required_version = feature_versions[feature]
            if pkg_resources.parse_version(version) < pkg_resources.parse_version(required_version):
                compatibility_issues.append(f"功能 'st.{feature}' 需要 Streamlit {required_version} 或更高版本，但当前指定的版本是 {version}")
    
    return compatibility_issues

def main():
    """主函数"""
    # 获取已安装的Streamlit版本
    installed_version = get_installed_streamlit_version()
    if not installed_version:
        print("警告: Streamlit未安装")
        return
    
    print(f"已安装的Streamlit版本: {installed_version}")
    
    # 获取requirements.txt中指定的Streamlit版本
    required_version = None
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                if line.startswith('streamlit=='):
                    required_version = line.strip().split('==')[1]
                    break
    except FileNotFoundError:
        print("警告: 未找到requirements.txt文件")
    
    if required_version:
        print(f"requirements.txt中指定的Streamlit版本: {required_version}")
    else:
        print("警告: requirements.txt中未指定Streamlit版本")
        required_version = installed_version
    
    # 检查app.py中使用的Streamlit功能
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"错误: 未找到{app_file}文件")
        return
    
    features = check_streamlit_features(app_file)
    print(f"\n在{app_file}中检测到的Streamlit功能:")
    for feature, used in features.items():
        status = "使用" if used else "未使用"
        print(f"- st.{feature}: {status}")
    
    # 检查功能与指定版本的兼容性
    compatibility_issues = check_feature_compatibility(features, required_version)
    if compatibility_issues:
        print("\n兼容性问题:")
        for issue in compatibility_issues:
            print(f"- {issue}")
        print("\n建议: 更新requirements.txt中的Streamlit版本至少为1.12.0以支持所有使用的功能")
    else:
        print("\n未发现兼容性问题。所有使用的功能都与指定的Streamlit版本兼容。")

if __name__ == "__main__":
    main() 