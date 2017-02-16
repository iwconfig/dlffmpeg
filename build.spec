# -*- mode: python -*-
from pkgutil import iter_modules
from platform import system, architecture

for m in ['cursor', 'requests']:
    if m not in [name for loader, name, ispkg in iter_modules()]:
        import pip
        pip.main(['install', '-U', 'cursor', 'requests'])

system = system().lower()
arch = architecture()[0]
if 'linux' in system:
    hiddenimports = []
    system_arch = 'linux-{}'.format(arch)
if 'darwin' in system:
    system_arch = 'macosx-{}'.format(arch)
    hiddenimports = []
    import sys, os
    for i in sys.argv:
        if i.endswith('.spec'):
            sys.path.append(os.path.realpath(i))
            break
if 'windows' in system:
    system_arch = 'windows-{}'.format(arch)
    hiddenimports=[
        '_sitebuiltins',
        'sysconfig',
        'site',
        'ipaddress',
        'requests.packages.urllib3.packages.ssl_match_hostname._implementation',
        'queue',
        'cursor.cursor']

from sys import path
path.insert(0, os.getcwd())
from dlffmpeg import __version__ as v
name = 'dlffmpeg-{0}-{1}'.format(v, system_arch)

block_cipher = None


a = Analysis(['dlffmpeg.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=name,
          debug=False,
          strip=False,
          upx=True,
          console=True )
