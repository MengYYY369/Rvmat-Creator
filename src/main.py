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

try:
    # 尝试使用 tkinterdnd2 创建支持拖拽的窗口
    from tkinterdnd2 import TkinterDnD
    USE_DND = True
except ImportError:
    # 如果没有安装 tkinterdnd2，使用普通的 tkinter
    import tkinter as tk
    USE_DND = False

from src.ui.main_app_ui import MainAppUI


def main():
    """主函数"""
    if USE_DND:
        # 使用支持拖拽的 Tk 窗口
        root = TkinterDnD.Tk()
    else:
        # 使用普通的 Tk 窗口
        root = tk.Tk()
    
    app = MainAppUI(root)
    app.setup_ui()
    root.mainloop()


if __name__ == "__main__":
    main()