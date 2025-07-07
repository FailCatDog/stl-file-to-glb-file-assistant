import os
import time
import logging
import trimesh
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 导入本地模块
import utils
from config import config

# 配置日志
logger = utils.setup_logging(
    log_file=config.get('log_file'),
    console_level=config.get_log_level(config.get('console_log_level')),
    file_level=config.get_log_level(config.get('file_log_level'))
)

class STLHandler(FileSystemEventHandler):
    """STL文件事件处理器"""
    
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def on_created(self, event):
        """处理文件创建事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.stl':
            logger.info(f"检测到新的STL文件: {file_path}")
            self.convert_stl_to_glb(file_path)
    
    def on_modified(self, event):
        """处理文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.stl':
            logger.info(f"检测到STL文件被修改: {file_path}")
            self.convert_stl_to_glb(file_path)
    
    def convert_stl_to_glb(self, stl_path):
        """将STL文件转换为GLB格式"""
        try:
            # 检查文件是否有效
            if not utils.is_valid_stl(stl_path):
                logger.warning(f"无效或损坏的STL文件: {stl_path}")
                return
            
            # 如果配置了备份，则创建备份
            if config.get('backup_directory'):
                backup_dir = Path(config.get('backup_directory'))
                utils.backup_file(stl_path, backup_dir)
            
            # 加载STL文件
            mesh = trimesh.load(stl_path)
            
            # 创建输出路径
            output_filename = stl_path.stem + '.glb'
            output_path = Path(self.output_dir) / output_filename
            
            # 应用导出选项
            export_options = config.get('export_options', {})
            
            # 导出为GLB
            mesh.export(
                output_path,
                **export_options
            )
            
            logger.info(f"成功将 {stl_path} 转换为 {output_path}")
        except Exception as e:
            logger.error(f"转换 {stl_path} 时出错: {str(e)}")

def process_existing_files(input_dir, output_dir):
    """处理输入目录中已存在的STL文件"""
    logger.info(f"处理 {input_dir} 中已存在的STL文件")
    input_path = Path(input_dir)
    
    # 根据配置决定是否递归搜索
    if config.get('recursive_scan'):
        stl_files = list(input_path.glob('**/*.stl'))
    else:
        stl_files = list(input_path.glob('*.stl'))
    
    logger.info(f"找到 {len(stl_files)} 个已存在的STL文件")
    
    # 创建STL处理器用于转换
    handler = STLHandler(input_dir, output_dir)
    
    # 处理每个文件
    for stl_file in stl_files:
        logger.info(f"处理已存在的文件: {stl_file}")
        
        # 如果输出文件已存在则跳过
        output_filename = stl_file.stem + '.glb'
        output_path = Path(output_dir) / output_filename
        
        if output_path.exists():
            logger.info(f"输出文件 {output_path} 已存在，跳过")
            continue
        
        # 转换文件
        handler.convert_stl_to_glb(stl_file)
    
    # 记录转换统计信息
    stats = utils.get_conversion_stats(input_dir, output_dir)
    logger.info(f"转换统计: {stats}")

def main():
    """启动STL到GLB转换器的主函数"""
    parser = argparse.ArgumentParser(description='将STL文件转换为GLB格式')
    parser.add_argument('--input', type=str, help='监控STL文件的输入目录')
    parser.add_argument('--output', type=str, help='GLB文件的输出目录')
    parser.add_argument('--config', type=str, help='配置文件路径')
    args = parser.parse_args()
    
    # 如果指定了自定义配置，则加载
    if args.config:
        config.config_file = args.config
        config.load()
    
    # 命令行参数覆盖配置
    if args.input:
        config.set('input_directory', args.input)
    if args.output:
        config.set('output_directory', args.output)
    
    # 从配置获取目录
    input_dir = Path(config.get('input_directory'))
    output_dir = Path(config.get('output_directory'))
    backup_dir = Path(config.get('backup_directory')) if config.get('backup_directory') else None
    
    # 如果目录不存在则创建
    utils.ensure_directory(input_dir)
    utils.ensure_directory(output_dir)
    if backup_dir:
        utils.ensure_directory(backup_dir)
    
    # 如果配置了自动清理，则清理输出目录
    if config.get('auto_clean'):
        cleaned = utils.clean_directory(output_dir)
        logger.info(f"从输出目录清理了 {cleaned} 个文件")
    
    logger.info(f"启动STL到GLB转换器")
    logger.info(f"监控目录: {input_dir.absolute()}")
    logger.info(f"输出目录: {output_dir.absolute()}")
    if backup_dir:
        logger.info(f"备份目录: {backup_dir.absolute()}")
    
    # 处理已存在的文件
    process_existing_files(input_dir, output_dir)
    
    # 设置文件系统观察器
    event_handler = STLHandler(input_dir, output_dir)
    observer = Observer()
    observer.schedule(event_handler, str(input_dir), recursive=config.get('recursive_scan', False))
    observer.start()
    
    try:
        logger.info("监控已启动。按Ctrl+C停止。")
        while True:
            time.sleep(config.get('watch_interval', 1.0))
    except KeyboardInterrupt:
        logger.info("正在停止监控...")
        observer.stop()
    
    observer.join()
    logger.info("转换器已停止")

if __name__ == "__main__":
    main() 