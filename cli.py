#!/usr/bin/env python
import os
import sys
import argparse
import logging
from pathlib import Path

# 导入本地模块
import utils
from config import config
import stl_to_glb_converter as converter
import batch_convert as batch

def setup_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='STL到GLB转换器 - 一个用于将STL文件转换为GLB格式的工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py watch --input 输入目录 --output 输出目录
  python cli.py batch --input 输入目录 --output 输出目录
  python cli.py config --set input_directory=新输入目录
  python cli.py service --install
"""
    )
    
    # 为不同命令创建子解析器
    subparsers = parser.add_subparsers(dest='command', help='要执行的命令')
    
    # watch命令 - 监控目录变化
    watch_parser = subparsers.add_parser('watch', help='监控STL文件并转换它们')
    watch_parser.add_argument('--input', type=str, help='要监控的输入目录')
    watch_parser.add_argument('--output', type=str, help='GLB文件的输出目录')
    watch_parser.add_argument('--recursive', action='store_true', help='递归监控子目录')
    watch_parser.add_argument('--config', type=str, help='配置文件路径')
    
    # batch命令 - 一次性转换所有文件
    batch_parser = subparsers.add_parser('batch', help='一次性转换目录中的所有STL文件')
    batch_parser.add_argument('--input', type=str, help='包含STL文件的输入目录')
    batch_parser.add_argument('--output', type=str, help='GLB文件的输出目录')
    batch_parser.add_argument('--workers', type=int, help='工作线程数量')
    batch_parser.add_argument('--recursive', action='store_true', help='递归扫描子目录')
    batch_parser.add_argument('--config', type=str, help='配置文件路径')
    
    # config命令 - 管理配置
    config_parser = subparsers.add_parser('config', help='管理配置')
    config_parser.add_argument('--set', type=str, action='append', help='设置配置值(键=值)')
    config_parser.add_argument('--get', type=str, help='获取配置值')
    config_parser.add_argument('--reset', action='store_true', help='重置配置为默认值')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    config_parser.add_argument('--file', type=str, help='配置文件路径')
    
    # service命令 - 管理服务
    service_parser = subparsers.add_parser('service', help='管理服务')
    service_parser.add_argument('--install', action='store_true', help='安装为服务')
    service_parser.add_argument('--uninstall', action='store_true', help='卸载服务')
    service_parser.add_argument('--start', action='store_true', help='启动服务')
    service_parser.add_argument('--stop', action='store_true', help='停止服务')
    service_parser.add_argument('--status', action='store_true', help='检查服务状态')
    service_parser.add_argument('--config', type=str, help='配置文件路径')
    
    return parser

def handle_watch_command(args):
    """处理watch命令"""
    # 如果指定了自定义配置，则加载
    if args.config:
        config.config_file = args.config
        config.load()
    
    # 命令行参数覆盖配置
    if args.input:
        config.set('input_directory', args.input)
    if args.output:
        config.set('output_directory', args.output)
    if args.recursive:
        config.set('recursive_scan', True)
    
    # 启动转换器
    converter.main()

def handle_batch_command(args):
    """处理batch命令"""
    # 如果指定了自定义配置，则加载
    if args.config:
        config.config_file = args.config
        config.load()
    
    # 命令行参数覆盖配置
    input_dir = args.input or config.get('input_directory')
    output_dir = args.output or config.get('output_directory')
    workers = args.workers or config.get('max_workers')
    recursive = args.recursive or config.get('recursive_scan')
    
    # 在配置中设置递归扫描以供将来使用
    if recursive:
        config.set('recursive_scan', True)
    
    # 如果目录不存在则创建
    utils.ensure_directory(input_dir)
    utils.ensure_directory(output_dir)
    
    # 查找STL文件
    input_path = Path(input_dir)
    if recursive:
        stl_files = list(input_path.glob('**/*.stl'))
    else:
        stl_files = list(input_path.glob('*.stl'))
    
    logger = logging.getLogger(__name__)
    logger.info(f"找到 {len(stl_files)} 个STL文件需要转换")
    
    # 运行批量转换
    batch.batch_convert(input_dir, output_dir, workers)

def handle_config_command(args):
    """处理config命令"""
    # 如果指定了自定义配置文件，则加载
    if args.file:
        config.config_file = args.file
        config.load()
    
    # 重置配置为默认值
    if args.reset:
        config.config = config.DEFAULT_CONFIG.copy()
        config.save()
        print("配置已重置为默认值")
    
    # 设置配置值
    if args.set:
        for kv in args.set:
            if '=' in kv:
                key, value = kv.split('=', 1)
                # 尝试将值转换为适当的类型
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.lower() == 'none':
                    value = None
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
                    value = float(value)
                
                config.set(key, value)
                print(f"设置 {key} = {value}")
        
        # 保存更改
        config.save()
    
    # 获取配置值
    if args.get:
        value = config.get(args.get)
        print(f"{args.get} = {value}")
    
    # 显示当前配置
    if args.show or (not args.set and not args.get and not args.reset):
        import json
        print(json.dumps(config.config, indent=2))

def handle_service_command(args):
    """处理service命令"""
    # 如果指定了自定义配置，则加载
    if args.config:
        config.config_file = args.config
        config.load()
    
    # 导入服务模块
    try:
        import run_as_service as service
    except ImportError:
        print("未找到服务模块")
        return
    
    # 安装服务
    if args.install:
        # 获取Python可执行文件路径
        python_path = sys.executable
        
        # 获取脚本路径
        script_path = Path(__file__).parent / "stl_to_glb_converter.py"
        script_path = script_path.absolute()
        
        # 获取输入和输出目录
        input_dir = Path(config.get('input_directory')).absolute()
        output_dir = Path(config.get('output_directory')).absolute()
        
        # 根据平台安装服务
        if sys.platform.startswith('win'):
            success = service.install_service_windows(python_path, script_path, input_dir, output_dir)
        elif sys.platform.startswith('linux'):
            success = service.install_service_linux(python_path, script_path, input_dir, output_dir)
        else:
            print(f"不支持的平台: {sys.platform}")
            success = False
        
        if success:
            print("服务安装成功")
        else:
            print("服务安装失败")
    
    # 卸载服务
    if args.uninstall:
        print("服务卸载功能尚未实现")
    
    # 启动服务
    if args.start:
        print("服务启动功能尚未实现")
    
    # 停止服务
    if args.stop:
        print("服务停止功能尚未实现")
    
    # 检查服务状态
    if args.status:
        print("服务状态检查功能尚未实现")

def main():
    """CLI的主函数"""
    # 设置日志
    logger = utils.setup_logging()
    
    # 解析命令行参数
    parser = setup_parser()
    args = parser.parse_args()
    
    # 处理命令
    if args.command == 'watch':
        handle_watch_command(args)
    elif args.command == 'batch':
        handle_batch_command(args)
    elif args.command == 'config':
        handle_config_command(args)
    elif args.command == 'service':
        handle_service_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 