"""
拖拽功能模块
提供真正的拖拽文件支持 (使用tkinterdnd2实现)
"""

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    print("警告: 未安装 tkinterdnd2 库，拖拽功能将不可用")
    TkinterDnD = None

import tkinter as tk
from tkinter import filedialog
import os


class DragDropMixin:
    """拖拽功能混入类 (使用tkinterdnd2实现真正的拖拽支持)"""
    
    def setup_drag_drop(self, widget):
        """设置真正的拖拽功能"""
        try:
            # 检查是否安装了tkinterdnd2
            if TkinterDnD is None:
                print("tkinterdnd2 未安装，使用文件选择对话框替代")
                self._setup_fallback_drag_drop(widget)
                return
            
            if hasattr(self, 'drag_frame') and widget == self.drag_frame:
                # 注册拖拽目标
                widget.drop_target_register(DND_FILES)
                
                # 绑定拖拽事件
                widget.dnd_bind('<<Drop>>', self._on_drop)
                widget.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                widget.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                
                # 设置光标
                widget.configure(cursor="hand2")
                
                # 绑定点击事件作为备选方案
                widget.bind("<Button-1>", self._on_click)
        except Exception as e:
            print(f"拖拽功能初始化失败: {e}")
            # 如果拖拽功能初始化失败，使用备选方案
            self._setup_fallback_drag_drop(widget)
    
    def _setup_fallback_drag_drop(self, widget):
        """设置备选的拖拽功能（文件选择对话框）"""
        try:
            if hasattr(self, 'drag_frame') and widget == self.drag_frame:
                # 绑定点击事件作为主要文件选择方式
                widget.bind("<Button-1>", self._on_click)
                widget.bind("<Enter>", self.on_drag_enter)
                widget.bind("<Leave>", self.on_drag_leave)
                widget.configure(cursor="hand2")
        except Exception as e:
            print(f"备选拖拽功能初始化失败: {e}")
    
    def on_drag_enter(self, event):
        """处理拖拽进入事件（提供视觉反馈）"""
        # 改变拖拽区域的背景色以提供视觉反馈
        if hasattr(self, 'drag_frame') and self.drag_frame:
            self.original_bg = self.drag_frame.cget("background")
            self.drag_frame.configure(background="#e3f2fd")
    
    def on_drag_leave(self, event):
        """处理拖拽离开事件"""
        # 恢复拖拽区域的原始背景色
        if hasattr(self, 'drag_frame') and self.drag_frame and hasattr(self, 'original_bg') and self.original_bg:
            self.drag_frame.configure(background=self.original_bg)
            self.original_bg = None
    
    def _on_drop(self, event):
        """处理文件拖拽释放事件"""
        try:
            # 获取拖拽的文件列表
            files = self._get_dropped_files(event)
            
            if files:
                # 过滤出.rvmat文件
                rvmat_files = [f for f in files if f.lower().endswith('.rvmat') and os.path.isfile(f)]
                
                if rvmat_files:
                    self.handle_dropped_files(rvmat_files)
                else:
                    # 如果拖拽的文件中没有.rvmat文件，显示警告
                    from tkinter import messagebox
                    warning_title = "警告" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("warning", "警告")
                    warning_msg = "拖拽的文件中没有找到有效的 .rvmat 文件" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("no_valid_rvmat_files", "拖拽的文件中没有找到有效的 .rvmat 文件")
                    messagebox.showwarning(warning_title, warning_msg)
        except Exception as e:
            print(f"处理拖拽文件时出错: {e}")
            from tkinter import messagebox
            error_title = "错误" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("error", "错误")
            error_msg = f"处理拖拽文件时出错: {str(e)}" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("drag_drop_error", "处理拖拽文件时出错: {str(e)}").format(str=e)
            messagebox.showerror(error_title, error_msg)
    
    def _get_dropped_files(self, event):
        """从拖拽事件中提取文件列表"""
        # tkinterdnd2 提供的数据格式
        if hasattr(event, 'data'):
            # 解析拖拽的数据
            data = event.data
            if isinstance(data, str):
                # 处理文件路径列表
                files = []
                # 处理可能被大括号包围的路径
                if data.startswith('{') and data.endswith('}'):
                    data = data[1:-1]
                
                # 分割文件路径（Windows使用空格分隔）
                # 但需要处理带空格的路径
                import shlex
                try:
                    files = shlex.split(data)
                except:
                    # 如果shlex失败，使用简单分割
                    files = data.split()
                
                # 验证文件路径
                valid_files = []
                for file_path in files:
                    # 移除可能的引号
                    file_path = file_path.strip('"\'')
                    if os.path.exists(file_path):
                        valid_files.append(file_path)
                
                return valid_files
        
        return []
    
    def _on_click(self, event=None):
        """处理点击事件，打开文件选择对话框"""
        # 弹出文件选择对话框
        files = filedialog.askopenfilenames(
            title="选择 RVMAT 文件" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("select_rvmat_files", "选择 RVMAT 文件"),
            filetypes=[("RVMAT files", "*.rvmat"), ("All files", "*.*")]
        )
        
        # 先导入所有文件，然后过滤出 .rvmat 文件
        if files:
            rvmat_files = [f for f in files if f.lower().endswith('.rvmat')]
            
            if rvmat_files:
                self.handle_dropped_files(rvmat_files)
            else:
                # 如果选择了文件但没有 .rvmat 文件，显示警告
                from tkinter import messagebox
                warning_title = "警告" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("warning", "警告")
                warning_msg = "选择的文件中没有找到 .rvmat 文件" if not hasattr(self, 'translations') else self.translations.get(self.language, {}).get("no_rvmat_files", "选择的文件中没有找到 .rvmat 文件")
                messagebox.showwarning(warning_title, warning_msg)
    
    def handle_dropped_files(self, files):
        """处理拖拽的文件"""
        # 这个方法需要在子类中实现
        raise NotImplementedError("子类必须实现 handle_dropped_files 方法")