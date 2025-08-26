"""
批量文件处理模块
提供批量处理 RVMAT 文件的功能
"""

import os
from tkinter import filedialog


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, processor, logger=None):
        self.processor = processor
        self.logger = logger
        self.processed_files = []
        self.failed_files = []
    
    def select_files(self, parent=None):
        """选择多个文件"""
        files = filedialog.askopenfilenames(
            parent=parent,
            title="选择 RVMAT 文件",
            filetypes=[("RVMAT files", "*.rvmat"), ("All files", "*.*")]
        )
        
        return list(files)
    
    def select_directory(self, parent=None):
        """选择目录"""
        directory = filedialog.askdirectory(
            parent=parent,
            title="选择包含 RVMAT 文件的目录"
        )
        
        if not directory:
            return []
        
        # 获取目录中所有 .rvmat 文件
        rvmat_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.rvmat'):
                    rvmat_files.append(os.path.join(root, file))
        
        return rvmat_files
    
    def process_files(self, file_list):
        """处理文件列表"""
        self.processed_files = []
        self.failed_files = []
        
        total_files = len(file_list)
        if self.logger:
            self.logger.log(f"开始处理 {total_files} 个文件...")
        
        for i, file_path in enumerate(file_list):
            if self.processor.is_rvmat_file(file_path):
                if self.logger:
                    self.logger.log(f"正在处理 ({i+1}/{total_files}): {os.path.basename(file_path)}")
                
                success = self.processor.process_rvmat_file(file_path)
                if success:
                    self.processed_files.append(file_path)
                    if self.logger:
                        self.logger.log(f"  ✓ 处理成功")
                else:
                    self.failed_files.append(file_path)
                    if self.logger:
                        self.logger.log(f"  ✗ 处理失败")
            else:
                self.failed_files.append(file_path)
                if self.logger:
                    self.logger.log(f"  ✗ 无效的 RVMAT 文件: {os.path.basename(file_path)}")
        
        # 输出处理结果
        if self.logger:
            self.logger.log(f"\n处理完成!")
            self.logger.log(f"成功处理: {len(self.processed_files)} 个文件")
            self.logger.log(f"处理失败: {len(self.failed_files)} 个文件")
            
            if self.failed_files:
                self.logger.log(f"\n失败的文件:")
                for file in self.failed_files:
                    self.logger.log(f"  - {file}")
        
        return len(self.processed_files), len(self.failed_files)
    
    def get_processed_files(self):
        """获取已处理的文件列表"""
        return self.processed_files
    
    def get_failed_files(self):
        """获取处理失败的文件列表"""
        return self.failed_files