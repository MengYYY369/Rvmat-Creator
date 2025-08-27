"""
配置管理模块
用于管理应用程序的配置设置，如语言偏好等
"""

import os
import json
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="app_config.json"):
        """初始化配置管理器"""
        # 获取用户配置目录
        self.config_dir = Path.home() / ".rvmat_creator"
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        # 配置文件路径
        self.config_file = self.config_dir / config_file
        # 默认配置
        self.default_config = {
            "language": "en",  # 默认英语
            "last_directory": ""
        }
        # 当前配置
        self.config = self.default_config.copy()
        # 加载现有配置
        self.load_config()
        print(f"配置文件路径: {self.config_file}")
        print(f"初始配置: {self.config}")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置和加载的配置
                    self.config.update(loaded_config)
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config()
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            # 使用默认配置
            self.config = self.default_config.copy()
    
    def save_config(self):
        """保存配置到文件"""
        print(f"尝试保存配置到: {self.config_file}")
        print(f"配置目录是否存在: {self.config_dir.exists()}")
        print(f"配置文件是否存在: {self.config_file.exists()}")
        try:
            # 检查目录权限
            test_file = self.config_dir / "test_permission.txt"
            with open(test_file, "w") as f:
                f.write("test")
            test_file.unlink()
            print("目录写入权限正常")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("配置文件保存成功")
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        # 自动保存配置
        self.save_config()
    
    def get_language(self):
        """获取语言设置"""
        return self.config.get("language", "en")
    
    def set_language(self, language):
        """设置语言"""
        print(f"设置语言: {language}")
        self.config["language"] = language
        print(f"更新后配置: {self.config}")
        self.save_config()
        print(f"配置已保存到: {self.config_file}")
        # 验证配置是否保存成功
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
            print(f"验证保存的配置: {saved_config}")
        except Exception as e:
            print(f"验证配置时出错: {e}")
    
    def get_last_directory(self):
        """获取上次使用的目录"""
        return self.config.get("last_directory", "")
    
    def set_last_directory(self, directory):
        """设置上次使用的目录"""
        self.config["last_directory"] = directory
        self.save_config()