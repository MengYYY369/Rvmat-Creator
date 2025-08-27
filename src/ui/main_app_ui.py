"""
主应用UI模块
提供主应用程序界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from .base_ui import BaseUI
from .log_window import LogWindow
from .drag_drop import DragDropMixin
from src.modules.rvmat_processor import RvmatProcessor
from src.modules.batch_processor import BatchProcessor
from src.modules.file_selector import FileSelector


class MainAppUI(BaseUI, DragDropMixin):
    """主应用UI类"""
    
    def __init__(self, root):
        self.processor = RvmatProcessor()
        self.batch_processor = BatchProcessor(self.processor)
        self.log_window = LogWindow(root)
        
        # 存储选择的文件列表
        self.selected_files = []
        
        # 拖拽视觉反馈相关变量
        self.drag_frame = None
        self.original_bg = None
        
        # 语言设置（默认中文）
        self.language = "en"  # "zh" for Chinese, "en" for English
        self.translations = {
            "zh": {
                "title": "Rvmat-Creator - DayZ 材质文件处理器",
                "quick_generate": "快速生成损坏RVMAT",
                "file_list": "文件列表",
                "select_files": "选择文件",
                "select_directory": "选择目录",
                "process_batch": "批量处理",
                "log_window": "处理日志",
                "click_hint": "💡 点击此区域选择文件 (如果拖拽功能失效)",
                "empty_list": "拖拽 .rvmat 文件 到这",
                "confirm_process": "确认",
                "confirm_message": f"确定要处理 {len(self.selected_files) if hasattr(self, 'selected_files') else 0} 个文件吗?",
                "warning": "警告",
                "no_files_selected": "请先选择要处理的文件",
                "processing_complete": "批量处理完成!",
                "success": "成功",
                "failure": "失败",
                "error": "错误",
                "processing_error": "处理过程中发生错误:\n{str(e)}"
            },
            "en": {
                "title": "Rvmat-Creator - DayZ Material File Processor",
                "quick_generate": "Quick Generate Damaged RVMAT",
                "file_list": "File List",
                "select_files": "Select Files",
                "select_directory": "Select Directory",
                "process_batch": "Batch Process",
                "log_window": "Logs",
                "click_hint": "💡 Click this area to select files (if drag and drop fails)",
                "empty_list": "Drag the .rvmat file here.",
                "confirm_process": "Confirm",
                "confirm_message": f"Are you sure you want to process {len(self.selected_files) if hasattr(self, 'selected_files') else 0} files?",
                "warning": "Warning",
                "no_files_selected": "Please select files to process first",
                "processing_complete": "Batch processing completed!",
                "success": "Success",
                "failure": "Failure",
                "error": "Error",
                "processing_error": "An error occurred during processing:\n{str(e)}"
            }
        }
        
        super().__init__(root)
        
        # 初始化文件选择器
        self.file_selector = FileSelector(self.log_window.log)
    
    def setup_base_ui(self):
        """设置基础UI"""
        self.root.title(self.translations[self.language]["title"])
        self.root.geometry("800x600")  # 减小窗口大小
        self.root.minsize(600, 500)  # 设置最小窗口大小
        
        # 设置窗口背景色
        self.root.configure(bg="#f5f5f5")
        
        super().setup_base_ui()
        
        # 添加语言选择
        self.add_language_selector()
        
        # 添加点击选择文件的提示
        self.add_click_hint()
        
        # 绑定快捷键
        self.root.bind("<Control-l>", self.toggle_language)
    
    def toggle_language(self, event=None):
        """切换语言快捷键 (Ctrl+L)"""
        # 获取当前语言列表
        languages = list(self.language_map.keys())
        current_index = languages.index(self.language_var.get())
        # 切换到下一个语言
        next_index = (current_index + 1) % len(languages)
        next_language = languages[next_index]
        
        # 更新选择
        self.language_var.set(next_language)
        self.change_language()
        
        # 设置样式
        self.setup_styles()
    
    def setup_styles(self):
        """设置UI样式"""
        style = ttk.Style()
        
        # 设置按钮样式
        style.configure("TButton", padding=6, relief="flat")
        style.map("TButton",
                 foreground=[('pressed', 'white'), ('active', 'blue')],
                 background=[('pressed', '!disabled', 'gray'), ('active', 'lightgray')])
        
        # 设置标签框架样式
        style.configure("TLabelframe.Label", font=("Arial", 11, "bold"), foreground="#34495e")
        
        # 设置处理按钮样式
        style.configure("Process.TButton", font=("Arial", 10, "bold"), padding=8)
    
    def setup_ui(self):
        """设置主界面"""
        main_frame = self.create_main_frame()
        
        # 直接创建主处理区域，移除标题
        self.create_main_processing_area()
        
        # 创建日志控制区域
        self.create_log_control_frame(main_frame)
    
    def create_main_processing_area(self):
        """创建主处理区域"""
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=30, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 创建批量处理区域
        self.create_batch_processing_area(main_frame)
    
    def create_batch_processing_area(self, parent):
        """创建批量处理区域"""
        # 主框架
        batch_frame_text = self.translations[self.language]["quick_generate"]
        batch_frame = ttk.LabelFrame(parent, text=batch_frame_text, padding="20")
        # 保存引用以便后续更新
        self.batch_frame = batch_frame
        batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        batch_frame.columnconfigure(0, weight=1)
        batch_frame.rowconfigure(0, weight=1)
        
        # 文件列表显示区域 - 现在也作为文件选择区域
        file_list_text = self.translations[self.language]["file_list"]
        file_list_frame = ttk.LabelFrame(batch_frame, text=file_list_text, padding="10")
        # 保存引用以便后续更新
        self.file_list_frame = file_list_frame
        file_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        file_list_frame.columnconfigure(0, weight=1)
        file_list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview来显示文件列表，支持删除按钮
        list_frame = ttk.Frame(file_list_frame)
        
        # 保存拖拽框架引用以供视觉反馈使用
        self.drag_frame = file_list_frame
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview和滚动条
        self.file_tree = ttk.Treeview(list_frame, columns=("filename", "remove"), show="", height=12)  # 隐藏表头
        self.file_tree.column("#0", width=0, stretch=False)  # 隐藏tree列
        self.file_tree.column("filename", width=400)  # 增加宽度
        self.file_tree.column("remove", width=80, anchor="center")
        
        # 设置拖拽功能 - 在drag_frame创建后初始化
        self.setup_drag_drop(self.drag_frame)
        
        # 创建滚动条
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=list_scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定删除按钮事件
        self.file_tree.bind("<Button-1>", self.on_tree_click)
        
        
        # 添加空列表提示
        empty_text = self.translations[self.language]["empty_list"]
        self.empty_label = ttk.Label(list_frame, text=empty_text, 
                                   font=("Arial", 11), foreground="gray", justify="center")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 绑定标签的点击事件
        self.empty_label.bind("<Button-1>", self.on_list_frame_click)
        self.empty_label.configure(cursor="hand2")
        
        # 文件选择按钮区域
        button_frame = ttk.Frame(batch_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10))
        
        # 选择文件按钮 (图标)
        select_file_text = self.translations[self.language]["select_files"]
        select_file_btn = ttk.Button(button_frame, text="📁 " + select_file_text, command=self.select_files_via_dialog)
        select_file_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 选择目录按钮 (图标)
        select_dir_text = self.translations[self.language]["select_directory"]
        select_dir_btn = ttk.Button(button_frame, text="📂 " + select_dir_text, command=self.select_directory_via_dialog)
        select_dir_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 批量处理按钮 (图标)
        process_batch_text = self.translations[self.language]["process_batch"]
        batch_process_btn = ttk.Button(button_frame, text="⚡ " + process_batch_text, command=self.process_batch_files, 
                                      style="Process.TButton")
        batch_process_btn.grid(row=0, column=2)
        
        # 保存按钮引用以便后续更新
        self.select_file_btn = select_file_btn
        self.select_dir_btn = select_dir_btn
        self.batch_process_btn = batch_process_btn
    
    def select_files_via_dialog(self):
        """通过文件对话框选择文件"""
        files = self.file_selector.select_files_dialog(self.root)
        if files:
            self.selected_files.extend(files)
            self.update_file_list_display()
    
    def select_directory_via_dialog(self):
        """通过目录对话框选择文件"""
        directory = self.file_selector.select_directory_dialog(self.root)
        if directory:
            files = self.file_selector.get_rvmat_files_from_directory(directory)
            if files:
                self.selected_files.extend(files)
                self.update_file_list_display()
    
    def create_log_control_frame(self, parent):
        """创建日志控制区域"""
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        log_frame.columnconfigure(0, weight=1)
        
        # 日志按钮 (使用文本图标)
        log_text = self.translations[self.language]["log_window"]
        log_btn = ttk.Button(log_frame, text="📝 " + log_text, command=self.log_window.toggle_window)
        log_btn.grid(row=0, column=0, sticky=tk.E)
        
        # 保存按钮引用以便后续更新
        self.log_btn = log_btn
    
    def add_language_selector(self):
        """添加语言选择器"""
        # 创建语言选择框架
        lang_frame = ttk.Frame(self.root)
        lang_frame.grid(row=0, column=0, sticky=(tk.E), padx=10, pady=5)
        
        # 语言选择标签
        lang_label = ttk.Label(lang_frame, text="语言/Language:")
        lang_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 语言映射
        self.language_map = {
            "中文": "zh",
            "English": "en"
        }
        
        # 语言选择下拉框
        self.language_var = tk.StringVar(value="中文" if self.language == "zh" else "English")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                 values=list(self.language_map.keys()), state="readonly", width=12)
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # 快捷键提示
        shortcut_label = ttk.Label(lang_frame, text="(Ctrl+L)", font=("Arial", 8), foreground="gray")
        shortcut_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 保存引用
        self.lang_combo = lang_combo
    
    def change_language(self, event=None):
        """切换语言"""
        selected = self.language_var.get()
        self.language = self.language_map.get(selected, "zh")
        
        # 更新界面文本
        self.update_ui_texts()
    
    def update_ui_texts(self):
        """更新界面文本"""
        # 更新窗口标题
        self.root.title(self.translations[self.language]["title"])
        
        # 更新批量处理区域标题
        if hasattr(self, 'batch_frame'):
            self.batch_frame.configure(text=self.translations[self.language]["quick_generate"])
        
        # 更新文件列表区域标题
        if hasattr(self, 'file_list_frame'):
            self.file_list_frame.configure(text=self.translations[self.language]["file_list"])
        
        # 更新按钮文本
        if hasattr(self, 'select_file_btn'):
            select_file_text = self.translations[self.language]["select_files"]
            self.select_file_btn.configure(text="📁 " + select_file_text)
        
        if hasattr(self, 'select_dir_btn'):
            select_dir_text = self.translations[self.language]["select_directory"]
            self.select_dir_btn.configure(text="📂 " + select_dir_text)
        
        if hasattr(self, 'batch_process_btn'):
            process_batch_text = self.translations[self.language]["process_batch"]
            self.batch_process_btn.configure(text="⚡ " + process_batch_text)
        
        if hasattr(self, 'log_btn'):
            log_text = self.translations[self.language]["log_window"]
            self.log_btn.configure(text="📝 " + log_text)
        
        # 更新空列表提示
        if hasattr(self, 'empty_label'):
            empty_text = self.translations[self.language]["empty_list"]
            self.empty_label.configure(text=empty_text)
        
        # 更新点击提示
        if hasattr(self, 'drag_frame'):
            hint_text = self.translations[self.language]["click_hint"]
            # 查找并更新提示标签
            for child in self.drag_frame.winfo_children():
                if isinstance(child, ttk.Label) and "点击此区域" in str(child.cget("text")):
                    child.configure(text=hint_text)
    
    def add_click_hint(self):
        """添加点击选择文件的提示"""
        if hasattr(self, 'drag_frame') and self.drag_frame:
            hint_text = self.translations[self.language]["click_hint"]
            hint_label = ttk.Label(self.drag_frame, 
                                 text=hint_text,
                                 font=("Arial", 9), 
                                 foreground="gray")
            hint_label.grid(row=2, column=0, pady=(5, 10))
    
    def update_file_list_display(self):
        """更新文件列表显示"""
        # 清空Treeview
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加文件到Treeview
        for i, file_path in enumerate(self.selected_files):
            filename = os.path.basename(file_path)
            self.file_tree.insert("", "end", iid=i, values=(filename, "❌"))
        
        # 根据文件列表是否为空来显示/隐藏提示标签
        if self.selected_files:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def handle_dropped_files(self, files):
        """处理拖拽的文件"""
        # 添加拖拽的文件到待处理列表
        self.selected_files.extend(files)
        self.update_file_list_display()
        
        # 记录日志
        log_msg = f"通过拖拽添加了 {len(files)} 个文件" if self.language == "zh" else f"Added {len(files)} files via drag and drop"
        self.log_window.log(log_msg)
    
    def on_tree_click(self, event):
        """处理Treeview点击事件"""
        region = self.file_tree.identify("region", event.x, event.y)
        column = self.file_tree.identify_column(event.x)
        row = self.file_tree.identify_row(event.y)
        
        # 如果点击的是删除列并且是有效行
        if region == "cell" and column == "#2" and row:
            self.remove_file(int(row))
    
    def on_list_frame_click(self, event):
        """处理列表框架的点击事件"""
        # 打开文件选择对话框
        self.select_files_via_dialog()
    
    def remove_file(self, index):
        """移除指定索引的文件"""
        if 0 <= index < len(self.selected_files):
            # 从文件列表中移除
            removed_file = self.selected_files.pop(index)
            # 更新显示
            self.update_file_list_display()
            # 记录日志
            self.log_window.log(f"已移除文件: {os.path.basename(removed_file)}")
    
    def process_batch_files(self):
        """批量处理文件"""
        if not self.selected_files:
            warning_title = self.translations[self.language]["warning"]
            warning_msg = self.translations[self.language]["no_files_selected"]
            messagebox.showwarning(warning_title, warning_msg)
            return
        
        try:
            # 处理文件
            success_count, fail_count = self.batch_processor.process_files(self.selected_files)
            
            # 显示结果
            complete_msg = self.translations[self.language]["processing_complete"]
            success_msg = self.translations[self.language]["success"]
            failure_msg = self.translations[self.language]["failure"]
            result_msg = f"{complete_msg}\n{success_msg}: {success_count} {failure_msg}: {fail_count}"
            self.log_window.log(result_msg)
        
        except Exception as e:
            error_title = self.translations[self.language]["error"]
            error_msg = self.translations[self.language]["processing_error"].format(str=e)
            messagebox.showerror(error_title, error_msg)