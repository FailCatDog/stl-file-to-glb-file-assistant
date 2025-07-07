import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "input_directory": "input",
    "output_directory": "output",
    "backup_directory": "backup",
    "log_file": "stl_to_glb.log",
    "console_log_level": "INFO",
    "file_log_level": "DEBUG",
    "recursive_scan": False,
    "watch_interval": 1.0,
    "auto_clean": False,
    "parallel_processing": True,
    "max_workers": None,  # 根据CPU核心数自动确定
    "export_options": {
        "smooth": True,
        "include_normals": True,
        "include_texture": True
    }
}

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

class Config:
    """STL到GLB转换器的配置管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """从文件加载配置"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            logger.info(f"未找到配置文件 {config_path}，使用默认配置")
            self.save()  # 创建默认配置文件
            return
        
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                # 用加载的值更新默认配置
                self._update_nested_dict(self.config, loaded_config)
            logger.info(f"从 {config_path} 加载配置")
        except Exception as e:
            logger.error(f"加载配置时出错: {str(e)}")
    
    def save(self):
        """将当前配置保存到文件"""
        config_path = Path(self.config_file)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"配置已保存到 {config_path}")
        except Exception as e:
            logger.error(f"保存配置时出错: {str(e)}")
    
    def get(self, key, default=None):
        """通过键获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """通过键设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到嵌套字典
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_log_level(self, level_name):
        """从字符串名称获取日志级别"""
        return LOG_LEVELS.get(level_name.upper(), logging.INFO)
    
    def _update_nested_dict(self, d, u):
        """用另一个字典更新嵌套字典"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

# 全局配置实例
config = Config() 