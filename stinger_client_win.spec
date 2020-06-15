# -*- mode: python -*-

block_cipher = None


a = Analysis(['stinger_client.py'],
             pathex=['C:\\Users\\Administrator.WIN7\\Desktop\\pystinger_for_darkshadow'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
             "jinja2",
             "_tkinter",
             "distutils",
             "six",
             "setuptools",
             "multiprocessing",
             "gevent",
             ],
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
          name='stinger_client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
