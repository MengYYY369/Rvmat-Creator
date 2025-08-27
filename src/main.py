#!/usr/bin/env python3
"""
Rvmat-Creator 主程序
用于快速处理 DayZ 材质 Rvmat 文件
"""

import os
import sys

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 初始化tkinterdnd2可用性标志
USE_DND = False

try:
    # 先尝试导入tkinterdnd2
    import tkinterdnd2
    print("tkinterdnd2模块可用")
    
    # 在PyInstaller打包环境中运行时，设置tkdnd路径
    if getattr(sys, 'frozen', False):
        # 在打包环境中，设置tkdnd路径
        base_path = sys._MEIPASS  # PyInstaller提取文件到_MEIPASS
        tkdnd_path = os.path.join(base_path, "tkinterdnd2", "tkdnd")
        # 只包含64位库路径，避免32/64位不匹配错误
        tkdnd_paths = [
            tkdnd_path,
            os.path.join(base_path, "tkinterdnd2", "tkdnd", "win-x64")
        ]
        
        # 尝试加载tkdnd库
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口避免多余窗口显示
            for path in tkdnd_paths:
                if os.path.exists(path):
                    root.tk.call("lappend", "auto_path", path)
            root.tk.call("package", "require", "tkdnd")
            root.destroy()
            print("成功加载tkdnd库")
        except Exception as e:
            print(f"加载tkdnd库时出错: {e}")
    
    # 尝试使用 tkinterdnd2 创建支持拖拽的窗口
    from tkinterdnd2 import TkinterDnD
    USE_DND = True
    print("tkinterdnd2导入成功")
except ImportError as e:
    # 如果没有安装 tkinterdnd2，使用普通的 tkinter
    print(f"导入tkinterdnd2失败: {e}")
    import tkinter as tk

from src.ui.main_app_ui import MainAppUI


def main():
    """主函数"""
    print(f"USE_DND状态: {USE_DND}")
    if USE_DND:
        # 使用支持拖拽的 Tk 窗口
        try:
            root = TkinterDnD.Tk()
            print("成功创建TkinterDnD.Tk()窗口")
        except Exception as e:
            print(f"创建TkinterDnD.Tk()窗口失败: {e}")
            import tkinter as tk
            root = tk.Tk()
    else:
        # 使用普通的 Tk 窗口
        import tkinter as tk
        root = tk.Tk()
    
    # 设置窗口关闭协议，确保程序完全退出
    def on_closing():
        root.destroy()
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    app = MainAppUI(root)
    app.setup_ui()
    root.mainloop()


if __name__ == "__main__":
    main()