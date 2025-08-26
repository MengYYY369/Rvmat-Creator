"""
文件选择器模块
提供文件选择功能作为拖拽的替代方案
"""

import tkinter as tk
from tkinter import filedialog
import os


class FileSelector:
    """文件选择器类"""
    
    def __init__(self, log_callback=None):
        """
        初始化文件选择器
        
        Args:
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback
    
    def select_files_dialog(self, parent=None):
        """
        打开文件选择对话框选择文件
        
        Args:
            parent: 父窗口
            
        Returns:
            list: 选择的文件路径列表
        """
        files = filedialog.askopenfilenames(
            parent=parent,
            title="选择RVMAT文件",
            filetypes=[("RVMAT files", "*.rvmat"), ("All files", "*.*")]
        )
        
        rvmat_files = [f for f in files if f.lower().endswith('.rvmat')]
        
        if self.log_callback and rvmat_files:
            self.log_callback(f"通过文件对话框选择了 {len(rvmat_files)} 个文件")
        
        return rvmat_files
    
    def select_directory_dialog(self, parent=None):
        """
        打开目录选择对话框
        
        Args:
            parent: 父窗口
            
        Returns:
            str: 选择的目录路径
        """
        directory = filedialog.askdirectory(
            parent=parent,
            title="选择包含RVMAT文件的目录"
        )
        
        if directory and self.log_callback:
            self.log_callback(f"选择了目录: {directory}")
        
        return directory
    
    def get_rvmat_files_from_directory(self, directory):
        """
        从目录中获取所有RVMAT文件，排除包含_worn, _damage, _destruct的文件
        
        Args:
            directory: 目录路径
            
        Returns:
            list: RVMAT文件路径列表
        """
        if not os.path.isdir(directory):
            return []
        
        rvmat_files = []
        excluded_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.rvmat'):
                    file_path = os.path.join(root, file)
                    filename_lower = file.lower()
                    
                    # 检查文件名是否包含排除的关键词
                    if any(keyword in filename_lower for keyword in ['_worn', '_damage', '_destruct']):
                        excluded_files.append(file_path)
                        if self.log_callback:
                            self.log_callback(f"排除损坏材质文件: {file}")
                    else:
                        rvmat_files.append(file_path)
        
        if self.log_callback:
            if rvmat_files:
                self.log_callback(f"从目录中找到 {len(rvmat_files)} 个RVMAT文件")
            if excluded_files:
                self.log_callback(f"排除了 {len(excluded_files)} 个损坏材质文件")
        
        return rvmat_files