import os
import argparse
import logging
import trimesh
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('batch_convert.log')
    ]
)
logger = logging.getLogger(__name__)

def convert_stl_to_glb(stl_path, output_dir):
    """将单个STL文件转换为GLB格式"""
    stl_path = Path(stl_path)
    output_dir = Path(output_dir)
    output_path = output_dir / f"{stl_path.stem}.glb"
    
    try:
        logger.info(f"正在转换 {stl_path}")
        mesh = trimesh.load(stl_path)
        mesh.export(output_path)
        logger.info(f"成功将 {stl_path} 转换为 {output_path}")
        return True
    except Exception as e:
        logger.error(f"转换 {stl_path} 时出错: {str(e)}")
        return False

def batch_convert(input_dir, output_dir, max_workers=None):
    """将输入目录中的所有STL文件批量转换为GLB格式"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 如果输出目录不存在则创建
    output_path.mkdir(exist_ok=True)
    
    # 查找所有STL文件
    stl_files = list(input_path.glob('**/*.stl'))
    total_files = len(stl_files)
    
    if total_files == 0:
        logger.info(f"在 {input_path} 中未找到STL文件")
        return
    
    logger.info(f"找到 {total_files} 个STL文件需要转换")
    
    # 并行处理文件
    successful = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有转换任务
        future_to_file = {
            executor.submit(convert_stl_to_glb, stl_file, output_path): stl_file
            for stl_file in stl_files
        }
        
        # 处理结果
        for future in as_completed(future_to_file):
            stl_file = future_to_file[future]
            try:
                if future.result():
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"转换 {stl_file} 失败: {str(e)}")
                failed += 1
    
    logger.info(f"批量转换完成。成功: {successful}, 失败: {failed}")

def main():
    """运行批量转换的主函数"""
    parser = argparse.ArgumentParser(description='批量将STL文件转换为GLB格式')
    parser.add_argument('--input', type=str, default='input', help='包含STL文件的输入目录')
    parser.add_argument('--output', type=str, default='output', help='GLB文件的输出目录')
    parser.add_argument('--workers', type=int, default=None, help='工作线程的最大数量')
    args = parser.parse_args()
    
    logger.info(f"开始从 {args.input} 到 {args.output} 的批量转换")
    batch_convert(args.input, args.output, args.workers)
    logger.info("批量转换过程完成")

if __name__ == "__main__":
    main() 