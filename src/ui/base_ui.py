"""
UI 基础模块
提供基础的 UI 组件和功能
"""

import tkinter as tk
from tkinter import ttk


class BaseUI:
    """基础 UI 类"""
    
    def __init__(self, root):
        self.root = root
        self.setup_base_ui()
    
    def setup_base_ui(self):
        """设置基础 UI"""
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_main_frame(self, parent=None):
        """创建主框架"""
        if parent is None:
            parent = self.root
            
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        return main_frame
    
    def create_label_frame(self, parent, text, padding="10"):
        """创建标签框架"""
        frame = ttk.LabelFrame(parent, text=text, padding=padding)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        return frame