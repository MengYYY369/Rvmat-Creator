"""
日志窗口模块
提供日志显示功能
"""

import tkinter as tk
from tkinter import ttk


class LogWindow:
    """日志窗口类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.text_widget = None
        self.is_visible = False
    
    def toggle_window(self):
        """切换日志窗口显示/隐藏"""
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()
    
    def show_window(self):
        """显示日志窗口"""
        if self.window is None:
            self.create_window()
        
        self.window.deiconify()
        self.is_visible = True
    
    def hide_window(self):
        """隐藏日志窗口"""
        if self.window:
            self.window.withdraw()
            self.is_visible = False
    
    def create_window(self):
        """创建日志窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Logs")
        self.window.geometry("600x400")
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加关闭按钮
        close_btn = ttk.Button(self.window, text="Close", command=self.hide_window)
        close_btn.pack(pady=(0, 10))
    
    def log(self, message):
        """添加日志消息"""
        if self.text_widget:
            self.text_widget.insert(tk.END, message + "\n")
            self.text_widget.see(tk.END)
    
    def clear_log(self):
        """清空日志"""
        if self.text_widget:
            self.text_widget.delete(1.0, tk.END)