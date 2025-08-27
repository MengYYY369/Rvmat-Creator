import tkinter as tk
from tkinter import ttk, messagebox
import os
import gettext
import locale

from .base_ui import BaseUI
from .log_window import LogWindow
from .drag_drop import DragDropMixin
from src.modules.rvmat_processor import RvmatProcessor
from src.modules.batch_processor import BatchProcessor
from src.modules.file_selector import FileSelector
from src.modules.config_manager import ConfigManager


class MainAppUI(BaseUI, DragDropMixin):
    """主应用UI类"""
    
    def __init__(self, root):
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化翻译器
        self.setup_translations()
        
        self.processor = RvmatProcessor()
        self.batch_processor = BatchProcessor(self.processor)
        self.log_window = LogWindow(root)
        
        # 存储选择的文件列表
        self.selected_files = []
        
        # 拖拽视觉反馈相关变量
        self.drag_frame = None
        self.original_bg = None
        
        # 语言设置（从配置文件读取，默认英文）
        self.language = self.config_manager.get_language()
        
        super().__init__(root)
        
        # 初始化文件选择器
        self.file_selector = FileSelector(self.log_window.log)
    
    def setup_translations(self):
        """设置翻译"""
        # 定义翻译字典
        self.translations = {
            "zh": {
                "title": "Rvmat-Creator - DayZ 材质文件处理器",
                "quick_generate": "快速生成损坏RVMAT",
                "file_list": "文件列表",
                "select_files": "选择文件",
                "select_directory": "选择目录",
                "process_batch": "开始处理",
                "log_window": "处理日志",
                "click_hint": "💡 点击此区域选择文件 (如果拖拽功能失效)",
                "empty_list": "拖拽 .rvmat 文件 到这",
                "confirm_process": "确认",
                "confirm_message": f"确定要处理 {{}} 个文件吗?",
                "warning": "警告",
                "no_files_selected": "请先选择要处理的文件",
                "processing_complete": "批量处理完成!",
                "success": "成功",
                "failure": "失败",
                "error": "错误",
                "processing_error": "处理过程中发生错误:\n{}",
                "settings": "设置",
                "language_settings": "语言设置",
                "select_language": "选择界面语言:",
                "main_processing": "主处理",
                "logs": "日志",
                "clear_logs": "清空日志"
            },
            "en": {
                "title": "Rvmat-Creator - DayZ Material File Processor",
                "quick_generate": "Quick Generate Damaged RVMAT",
                "file_list": "File List",
                "select_files": "Select Files",
                "select_directory": "Select Directory",
                "process_batch": "Start Process",
                "log_window": "Logs",
                "click_hint": "💡 Click this area to select files (if drag and drop fails)",
                "empty_list": "Drag the .rvmat file here.",
                "confirm_process": "Confirm",
                "confirm_message": f"Are you sure you want to process {{}} files?",
                "warning": "Warning",
                "no_files_selected": "Please select files to process first",
                "processing_complete": "Batch processing completed!",
                "success": "Success",
                "failure": "Failure",
                "error": "Error",
                "processing_error": "An error occurred during processing:\n{}",
                "settings": "Settings",
                "language_settings": "Language Settings",
                "select_language": "Select Interface Language:",
                "main_processing": "Main Processing",
                "logs": "Logs",
                "clear_logs": "Clear Logs"
            }
        }
    
    def _(self, key):
        """获取当前语言的翻译文本"""
        return self.translations[self.language].get(key, key)
    
    def setup_base_ui(self):
        """设置基础UI"""
        self.root.title(self._("title"))
        self.root.geometry("800x600")  # 减小窗口大小
        self.root.minsize(600, 500)  # 设置最小窗口大小
        
        # 设置窗口背景色
        self.root.configure(bg="#f5f5f5")
        
        super().setup_base_ui()
        
        # 添加点击选择文件的提示
        self.add_click_hint()
        
        # 绑定快捷键
        self.root.bind("<Control-l>", self.toggle_language)
        
        # 配置网格权重以减少顶部留白
        self.root.rowconfigure(0, weight=0)  # 顶部区域不扩展
        self.root.rowconfigure(1, weight=1)  # 主内容区域扩展
    
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
        # 创建Notebook用于选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 创建主处理框架
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text=self._("main_processing"))
        
        # 创建设置框架
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text=self._("settings"))
        
        # 创建日志框架
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text=self._("logs"))
        
        # 配置权重以支持缩放
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # 创建主处理区域
        self.create_main_processing_area()
        
        # 创建设置区域
        self.create_settings_area()
        
        # 创建日志区域
        self.create_log_area()
    
    def create_main_processing_area(self):
        """创建主处理区域"""
        main_frame = ttk.Frame(self.main_frame)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 创建批量处理区域
        self.create_batch_processing_area(main_frame)
        
    def create_batch_processing_area(self, parent):
        """创建批量处理区域"""
        # 主框架
        batch_frame_text = self._("quick_generate")
        batch_frame = ttk.LabelFrame(parent, text=batch_frame_text, padding="20")
        # 保存引用以便后续更新
        self.batch_frame = batch_frame
        batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        batch_frame.columnconfigure(0, weight=1)
        batch_frame.rowconfigure(0, weight=1)
        
        # 文件列表显示区域 - 现在也作为文件选择区域
        file_list_text = self._("file_list")
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
        empty_text = self._("empty_list")
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
        select_file_text = self._("select_files")
        select_file_btn = ttk.Button(button_frame, text="📁 " + select_file_text, command=self.select_files_via_dialog)
        select_file_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 选择目录按钮 (图标)
        select_dir_text = self._("select_directory")
        select_dir_btn = ttk.Button(button_frame, text="📂 " + select_dir_text, command=self.select_directory_via_dialog)
        select_dir_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 批量处理按钮 (图标)
        process_batch_text = self._("process_batch")
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
    
    def create_settings_area(self):
        """创建设置区域"""
        # 清空设置框架
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # 创建设置框架
        settings_frame = ttk.Frame(self.settings_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 语言设置框架
        lang_frame = ttk.LabelFrame(settings_frame, text=self._("language_settings"), padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 语言选择标签
        lang_label_text = self._("select_language")
        lang_label = ttk.Label(lang_frame, text=lang_label_text)
        lang_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # 语言映射
        self.language_map = {
            "中文": "zh",
            "English": "en"
        }
        
        # 语言选择下拉框
        # 根据当前语言设置默认值
        default_language = "中文" if self.language == "zh" else "English"
        self.language_var = tk.StringVar(value=default_language)
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                 values=list(self.language_map.keys()), state="readonly", width=20)
        lang_combo.grid(row=0, column=1, sticky=tk.W)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # 确保界面语言与配置文件一致
        pass
        
        # 保存引用
        self.lang_combo = lang_combo
    
    def create_log_area(self):
        """创建日志区域"""
        # 清空日志框架
        for widget in self.log_frame.winfo_children():
            widget.destroy()
        
        # 创建日志文本框和滚动条
        text_frame = ttk.Frame(self.log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 获取日志文本框
        self.log_text_widget = self.log_window.text_widget if self.log_window.text_widget else None
        
        # 如果日志窗口已经创建，将其内容复制到新的文本框
        if self.log_text_widget:
            # 保存现有日志内容
            log_content = self.log_text_widget.get(1.0, tk.END)
            
            # 创建新的文本框
            self.log_text_widget = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text_widget.yview)
            self.log_text_widget.configure(yscrollcommand=scrollbar.set)
            
            # 恢复日志内容
            self.log_text_widget.insert(1.0, log_content)
        else:
            # 创建新的文本框
            self.log_text_widget = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text_widget.yview)
            self.log_text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.log_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加清空日志按钮
        clear_btn_frame = ttk.Frame(self.log_frame)
        clear_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        clear_btn = ttk.Button(clear_btn_frame, text=self._("clear_logs"), 
                              command=self.clear_logs)
        clear_btn.pack(side=tk.RIGHT)
        
    def clear_logs(self):
        """清空日志"""
        if self.log_text_widget:
            self.log_text_widget.delete(1.0, tk.END)
        # 同时清空LogWindow中的日志
        self.log_window.clear_log()
    
    def change_language(self, event=None):
        """切换语言"""
        # 如果有事件对象，尝试从事件中获取选中的值
        selected = None
        if event and hasattr(event, 'widget'):
            try:
                # 获取下拉框当前选中的值
                selected = event.widget.get()
            except Exception as e:
                print(f"从事件获取值时出错: {e}")
        
        # 如果没有从事件中获取到值，则使用language_var的值
        if selected is None:
            selected = self.language_var.get()
        
        # 检查选中的值是否在语言映射中
        if selected in self.language_map:
            self.language = self.language_map[selected]
        else:
            print(f"警告: 选中的值 '{selected}' 不在语言映射中，使用默认语言 'en'")
            self.language = "en"
        
        # 保存语言设置到配置文件
        self.config_manager.set_language(self.language)
        
        # 更新界面文本
        self.update_ui_texts()
        
        # 在打包环境中强制刷新界面
        try:
            self.root.update()
        except Exception as e:
            print(f"界面刷新时出错: {e}")
    
    def update_ui_texts(self):
        """更新界面文本"""
        # 更新窗口标题
        self.root.title(self._("title"))
        
        # 更新选项卡文本
        if hasattr(self, 'notebook'):
            self.notebook.tab(0, text=self._("main_processing"))
            self.notebook.tab(1, text=self._("settings"))
            self.notebook.tab(2, text=self._("logs"))
        
        # 更新批量处理区域标题
        if hasattr(self, 'batch_frame'):
            self.batch_frame.configure(text=self._("quick_generate"))
        
        # 更新文件列表区域标题
        if hasattr(self, 'file_list_frame'):
            self.file_list_frame.configure(text=self._("file_list"))
        
        # 更新按钮文本
        if hasattr(self, 'select_file_btn'):
            select_file_text = self._("select_files")
            self.select_file_btn.configure(text="📁 " + select_file_text)
        
        if hasattr(self, 'select_dir_btn'):
            select_dir_text = self._("select_directory")
            self.select_dir_btn.configure(text="📂 " + select_dir_text)
        
        if hasattr(self, 'batch_process_btn'):
            process_batch_text = self._("process_batch")
            self.batch_process_btn.configure(text="⚡ " + process_batch_text)
        
        # 更新空列表提示
        if hasattr(self, 'empty_label'):
            empty_text = self._("empty_list")
            self.empty_label.configure(text=empty_text)
        
        # 更新点击提示
        if hasattr(self, 'drag_frame'):
            hint_text = self._("click_hint")
            # 查找并更新提示标签
            for child in self.drag_frame.winfo_children():
                if isinstance(child, ttk.Label) and ("点击此区域" in str(child.cget("text")) or "Click this area" in str(child.cget("text"))):
                    child.configure(text=hint_text)
        
        # 更新设置区域文本
        if hasattr(self, 'settings_frame'):
            # 更新设置框架内的文本
            for child in self.settings_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.LabelFrame):
                            grandchild.configure(text=self._("language_settings"))
                            # 更新语言设置框架内的标签
                            for great_grandchild in grandchild.winfo_children():
                                if isinstance(great_grandchild, ttk.Label):
                                    great_grandchild.configure(text=self._("select_language"))
        
        # 更新日志区域文本
        if hasattr(self, 'log_frame'):
            # 更新清空日志按钮文本
            for child in self.log_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Button):
                            grandchild.configure(text=self._("clear_logs"))
        
        # 强制刷新界面
        try:
            self.root.update()
        except Exception as e:
            print(f"界面刷新时出错: {e}")
    
    def add_click_hint(self):
        """添加点击选择文件的提示"""
        if hasattr(self, 'drag_frame') and self.drag_frame:
            hint_text = self._("click_hint")
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
        
        # 同时在新的日志文本框中显示日志
        if self.log_text_widget:
            self.log_text_widget.insert(tk.END, log_msg + "\n")
            self.log_text_widget.see(tk.END)
    
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
            log_msg = f"已移除文件: {os.path.basename(removed_file)}"
            self.log_window.log(log_msg)
            
            # 同时在新的日志文本框中显示日志
            if self.log_text_widget:
                self.log_text_widget.insert(tk.END, log_msg + "\n")
                self.log_text_widget.see(tk.END)
    
    def process_batch_files(self):
        """批量处理文件"""
        if not self.selected_files:
            warning_title = self._("warning")
            warning_msg = self._("no_files_selected")
            messagebox.showwarning(warning_title, warning_msg)
            return
        
        try:
            # 处理文件
            success_count, fail_count = self.batch_processor.process_files(self.selected_files)
            
            # 显示结果
            complete_msg = self._("processing_complete")
            success_msg = self._("success")
            failure_msg = self._("failure")
            result_msg = f"{complete_msg}\n{success_msg}: {success_count} {failure_msg}: {fail_count}"
            self.log_window.log(result_msg)
            
            # 同时在新的日志文本框中显示结果
            if self.log_text_widget:
                self.log_text_widget.insert(tk.END, result_msg + "\n")
                self.log_text_widget.see(tk.END)
        
        except Exception as e:
            error_title = self._("error")
            error_msg = self._("processing_error").format(str(e))
            messagebox.showerror(error_title, error_msg)