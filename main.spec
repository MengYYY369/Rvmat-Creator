# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\main.py'],
             pathex=['D:\\Python Project\\Rvmat-Creator'],
             binaries=[('C:\\Users\\fengzhi\\AppData\\Roaming\\Python\\Python313\\site-packages\\tkinterdnd2\\tkdnd\\win-x64\\libtkdnd2.9.4.dll', 'tkinterdnd2/tkdnd/win-x64')],
             datas=[('C:\\Users\\fengzhi\\AppData\\Roaming\\Python\\Python313\\site-packages\\tkinterdnd2\\tkdnd\\win-x64', 'tkinterdnd2/tkdnd/win-x64'),
                    ('C:\\Users\\fengzhi\\AppData\\Roaming\\Python\\Python313\\site-packages\\tkinterdnd2', 'tkinterdnd2')],
             hiddenimports=['tkinterdnd2', 'tkinterdnd2.TkinterDnD'],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Rvmat-Creator',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
