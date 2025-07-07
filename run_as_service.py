import os
import sys
import time
import argparse
import logging
import subprocess
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('stl_to_glb_service.log')
    ]
)
logger = logging.getLogger(__name__)

def install_service_windows(python_path, script_path, input_dir, output_dir):
    """使用NSSM（Non-Sucking Service Manager）安装为Windows服务"""
    logger.info("此功能需要NSSM已安装并在PATH中。")
    logger.info("如果尚未安装NSSM，请从 https://nssm.cc/ 下载。")
    
    service_name = "STLtoGLBConverter"
    cmd_args = f"{script_path} --input \"{input_dir}\" --output \"{output_dir}\""
    
    try:
        # 检查服务是否存在
        check_cmd = f"sc query {service_name}"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if "FAILED 1060" not in result.stderr and "FAILED 1060" not in result.stdout:
            logger.info(f"服务 {service_name} 已存在。先移除它。")
            subprocess.run(f"nssm remove {service_name} confirm", shell=True, check=True)
        
        # 安装服务
        install_cmd = f"nssm install {service_name} \"{python_path}\" \"{cmd_args}\""
        subprocess.run(install_cmd, shell=True, check=True)
        
        # 设置服务描述
        subprocess.run(f"nssm set {service_name} Description \"STL到GLB文件转换服务\"", shell=True, check=True)
        
        # 启动服务
        subprocess.run(f"nssm start {service_name}", shell=True, check=True)
        
        logger.info(f"服务 {service_name} 已成功安装并启动。")
    except subprocess.SubprocessError as e:
        logger.error(f"安装Windows服务失败: {str(e)}")
        return False
    
    return True

def install_service_linux(python_path, script_path, input_dir, output_dir):
    """在Linux上安装为systemd服务"""
    service_name = "stl-to-glb.service"
    service_path = Path("/etc/systemd/system") / service_name
    
    service_content = f"""[Unit]
Description=STL到GLB文件转换服务
After=network.target

[Service]
ExecStart={python_path} {script_path} --input {input_dir} --output {output_dir}
WorkingDirectory={Path(script_path).parent.absolute()}
StandardOutput=append:/var/log/stl-to-glb.log
StandardError=append:/var/log/stl-to-glb.log
Restart=always
User={os.getlogin()}

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # 写入服务文件
        with open("stl-to-glb.service", "w") as f:
            f.write(service_content)
        
        # 复制到systemd目录
        subprocess.run(f"sudo cp stl-to-glb.service {service_path}", shell=True, check=True)
        
        # 重新加载systemd
        subprocess.run("sudo systemctl daemon-reload", shell=True, check=True)
        
        # 启用并启动服务
        subprocess.run(f"sudo systemctl enable {service_name}", shell=True, check=True)
        subprocess.run(f"sudo systemctl start {service_name}", shell=True, check=True)
        
        logger.info(f"服务 {service_name} 已成功安装并启动。")
    except (IOError, subprocess.SubprocessError) as e:
        logger.error(f"安装Linux服务失败: {str(e)}")
        return False
    
    return True

def main():
    """将STL到GLB转换器安装为服务的主函数"""
    parser = argparse.ArgumentParser(description='将STL到GLB转换器安装为服务')
    parser.add_argument('--input', type=str, default='input', help='监控STL文件的输入目录')
    parser.add_argument('--output', type=str, default='output', help='GLB文件的输出目录')
    args = parser.parse_args()
    
    # 获取绝对路径
    input_dir = Path(args.input).absolute()
    output_dir = Path(args.output).absolute()
    
    # 如果目录不存在则创建
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # 获取路径
    python_path = sys.executable
    script_path = Path(__file__).parent / "stl_to_glb_converter.py"
    script_path = script_path.absolute()
    
    logger.info(f"正在将STL到GLB转换器安装为服务")
    logger.info(f"Python路径: {python_path}")
    logger.info(f"脚本路径: {script_path}")
    logger.info(f"输入目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    
    # 根据平台安装服务
    if sys.platform.startswith('win'):
        success = install_service_windows(python_path, script_path, input_dir, output_dir)
    elif sys.platform.startswith('linux'):
        success = install_service_linux(python_path, script_path, input_dir, output_dir)
    else:
        logger.error(f"不支持的平台: {sys.platform}")
        success = False
    
    if success:
        logger.info("服务安装成功完成")
    else:
        logger.error("服务安装失败")

if __name__ == "__main__":
    main() 