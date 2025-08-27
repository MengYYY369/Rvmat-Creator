# -*- coding: utf-8 -*-
# PyInstaller runtime hook for encoding

import sys
import os

# 设置环境变量确保UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 重新配置标准输出和标准错误流的编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')