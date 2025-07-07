import os
import logging
import trimesh
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(log_file='stl_to_glb.log', console_level=logging.INFO, file_level=logging.DEBUG):
    """设置日志配置"""
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
    
    logging.basicConfig(
        level=min(console_level, file_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # 为单独的处理器设置级别
    handlers[0].setLevel(console_level)
    handlers[1].setLevel(file_level)
    
    return logging.getLogger(__name__)

def ensure_directory(directory):
    """确保目录存在，如不存在则创建"""
    path = Path(directory)
    path.mkdir(exist_ok=True, parents=True)
    return path

def clean_directory(directory, file_pattern='*.glb'):
    """清理目录，删除匹配模式的文件"""
    path = Path(directory)
    if not path.exists():
        return 0
    
    count = 0
    for item in path.glob(file_pattern):
        if item.is_file():
            item.unlink()
            count += 1
    
    return count

def is_valid_stl(file_path):
    """检查文件是否为有效的STL文件"""
    try:
        # 尝试用trimesh加载文件
        mesh = trimesh.load(file_path)
        # 检查是否为有效网格
        return mesh.is_watertight
    except Exception:
        return False

def get_file_info(file_path):
    """获取文件信息"""
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    stats = path.stat()
    
    return {
        'name': path.name,
        'extension': path.suffix,
        'size': stats.st_size,
        'modified': stats.st_mtime,
        'created': stats.st_ctime,
        'is_stl': path.suffix.lower() == '.stl'
    }

def backup_file(file_path, backup_dir):
    """创建文件备份"""
    source = Path(file_path)
    if not source.exists():
        logger.warning(f"无法备份不存在的文件: {source}")
        return None
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True, parents=True)
    
    # 创建带时间戳的备份文件名
    timestamp = source.stat().st_mtime
    backup_file = backup_path / f"{source.stem}_{int(timestamp)}{source.suffix}"
    
    try:
        shutil.copy2(source, backup_file)
        logger.info(f"创建备份: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"创建 {source} 的备份失败: {str(e)}")
        return None

def get_conversion_stats(input_dir, output_dir):
    """获取转换过程的统计信息"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    stl_files = list(input_path.glob('**/*.stl'))
    glb_files = list(output_path.glob('**/*.glb'))
    
    # 通过名称匹配GLB文件和STL文件
    converted_files = []
    for stl_file in stl_files:
        for glb_file in glb_files:
            if stl_file.stem == glb_file.stem:
                converted_files.append((stl_file, glb_file))
                break
    
    return {
        'total_stl': len(stl_files),
        'total_glb': len(glb_files),
        'converted': len(converted_files),
        'pending': len(stl_files) - len(converted_files)
    } 