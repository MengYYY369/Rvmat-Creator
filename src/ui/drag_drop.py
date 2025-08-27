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
            
            # 确保widget支持拖拽
            if hasattr(widget, 'drop_target_register'):
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
                print("拖拽功能已成功注册到widget")
            else:
                print("Widget不支持拖拽功能，使用备选方案")
                self._setup_fallback_drag_drop(widget)
                
        except Exception as e:
            print(f"拖拽功能初始化失败: {e}")
            # 如果拖拽功能初始化失败，使用备选方案
            self._setup_fallback_drag_drop(widget)
    
    def _setup_fallback_drag_drop(self, widget):
        """设置备选的拖拽功能（文件选择对话框）"""
        try:
            # 绑定点击事件作为主要文件选择方式
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self.on_drag_enter)
            widget.bind("<Leave>", self.on_drag_leave)
            widget.configure(cursor="hand2")
            print("备选拖拽功能已注册")
        except Exception as e:
            print(f"备选拖拽功能初始化失败: {e}")
    
    def on_drag_enter(self, event):
        """处理拖拽进入事件（提供视觉反馈）"""
        try:
            # 改变拖拽区域的背景色以提供视觉反馈
            widget = event.widget
            # 检查widget是否有background属性
            if hasattr(widget, 'cget') and hasattr(widget, 'configure'):
                try:
                    self.original_bg = widget.cget("background")
                    widget.configure(background="#e3f2fd")
                    print("拖拽进入")
                except _tkinter.TclError:
                    # 如果无法获取或设置background属性，忽略错误
                    print("无法设置拖拽区域背景色")
            else:
                print("Widget不支持背景色设置")
        except Exception as e:
            print(f"处理拖拽进入事件时出错: {e}")
    
    def on_drag_leave(self, event):
        """处理拖拽离开事件"""
        try:
            # 恢复拖拽区域的原始背景色
            widget = event.widget
            if hasattr(self, 'original_bg') and self.original_bg and hasattr(widget, 'configure'):
                try:
                    widget.configure(background=self.original_bg)
                    self.original_bg = None
                    print("拖拽离开")
                except _tkinter.TclError:
                    # 如果无法设置background属性，忽略错误
                    print("无法恢复拖拽区域背景色")
            else:
                print("无需恢复背景色")
        except Exception as e:
            print(f"处理拖拽离开事件时出错: {e}")
    
    def _on_drop(self, event):
        """处理文件拖拽释放事件"""
        try:
            print(f"接收到拖拽事件: {event}")
            # 恢复背景色
            self.on_drag_leave(event)
            
            # 获取拖拽的文件列表
            if hasattr(event, 'data'):
                # tkinterdnd2 返回的数据可能是文件路径列表
                data = event.data
                print(f"原始数据: {data}")
                
                if isinstance(data, str):
                    # 处理文件路径
                    files = []
                    
                    # 使用tk的splitlist方法来正确分割文件路径
                    if hasattr(event.widget, 'tk') and hasattr(event.widget.tk, 'splitlist'):
                        try:
                            files = list(event.widget.tk.splitlist(data))
                            print(f"使用splitlist分割: {files}")
                        except Exception as e:
                            print(f"splitlist失败: {e}")
                            # 备选方法
                            if data.startswith('{') and data.endswith('}'):
                                data = data[1:-1]
                            files = data.split()
                            print(f"使用简单分割: {files}")
                    else:
                        # 如果无法使用tk.splitlist，使用简单分割
                        if data.startswith('{') and data.endswith('}'):
                            data = data[1:-1]
                        files = data.split()
                        print(f"使用简单分割: {files}")
                    
                    # 验证文件路径并过滤.rvmat文件
                    rvmat_files = []
                    for file_path in files:
                        # 移除可能的引号
                        file_path = file_path.strip('"\'')
                        print(f"检查文件: {file_path}, 存在: {os.path.isfile(file_path)}, 是RVMAT: {file_path.lower().endswith('.rvmat')}")
                        if os.path.isfile(file_path) and file_path.lower().endswith('.rvmat'):
                            rvmat_files.append(file_path)
                    
                    if rvmat_files:
                        print(f"找到 {len(rvmat_files)} 个RVMAT文件")
                        self.handle_dropped_files(rvmat_files)
                    elif files:
                        # 如果有文件但没有.rvmat文件，显示警告
                        from tkinter import messagebox
                        language = getattr(self, 'language', 'zh')
                        translations = getattr(self, 'translations', {
                            'zh': {'warning': '警告', 'no_valid_rvmat_files': '拖拽的文件中没有找到有效的 .rvmat 文件'},
                            'en': {'warning': 'Warning', 'no_valid_rvmat_files': 'No valid .rvmat files found in dropped files'}
                        })
                        warning_title = translations.get(language, translations['zh']).get('warning', '警告')
                        warning_msg = translations.get(language, translations['zh']).get('no_valid_rvmat_files', '拖拽的文件中没有找到有效的 .rvmat 文件')
                        messagebox.showwarning(warning_title, warning_msg)
                    else:
                        # 没有有效文件
                        print("没有找到有效文件")
                        pass
        except Exception as e:
            print(f"处理拖拽文件时出错: {e}")
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            language = getattr(self, 'language', 'zh')
            translations = getattr(self, 'translations', {
                'zh': {'error': '错误', 'drag_drop_error': '处理拖拽文件时出错: {str(e)}'},
                'en': {'error': 'Error', 'drag_drop_error': 'Error processing dropped files: {str(e)}'}
            })
            error_title = translations.get(language, translations['zh']).get('error', '错误')
            error_msg = translations.get(language, translations['zh']).get('drag_drop_error', '处理拖拽文件时出错: {str(e)}').format(str=e)
            messagebox.showerror(error_title, error_msg)
    
    def _on_click(self, event=None):
        """处理点击事件，打开文件选择对话框"""
        print("点击事件触发")
        # 获取语言设置
        language = getattr(self, 'language', 'zh')
        translations = getattr(self, 'translations', {
            'zh': {'select_rvmat_files': '选择 RVMAT 文件', 'warning': '警告', 'no_rvmat_files': '选择的文件中没有找到 .rvmat 文件'},
            'en': {'select_rvmat_files': 'Select RVMAT Files', 'warning': 'Warning', 'no_rvmat_files': 'No .rvmat files found in selected files'}
        })
        
        # 弹出文件选择对话框
        title = translations.get(language, translations['zh']).get('select_rvmat_files', '选择 RVMAT 文件')
        files = filedialog.askopenfilenames(
            title=title,
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
                warning_title = translations.get(language, translations['zh']).get('warning', '警告')
                warning_msg = translations.get(language, translations['zh']).get('no_rvmat_files', '选择的文件中没有找到 .rvmat 文件')
                messagebox.showwarning(warning_title, warning_msg)
    
    def handle_dropped_files(self, files):
        """处理拖拽的文件"""
        # 这个方法需要在子类中实现
        raise NotImplementedError("子类必须实现 handle_dropped_files 方法")