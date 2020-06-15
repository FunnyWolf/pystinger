# -*- mode: python -*-

block_cipher = None


a = Analysis(['stinger_server.pyw'],
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
             "cherrypy",
             "setuptools",
             "multiprocessing",
             "gevent",
             "rocket",
             "twisted",
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
          name='stinger_server',
          debug=False,
          bootloader_ignore_signals=True,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
