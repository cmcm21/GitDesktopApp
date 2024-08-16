# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    [
        'main.py',
        'App.py',
        'View/__init__.py',
        'View/BaseWindow.py',
        'View/LauncherWindow.py',
        'View/UICommitWindow.py',
        'View/UILogger.py',
        'View/UIManager.py',
        'View/UIWorkspace.py',
        'View/WindowID.py',
        'Controller/__init__.py',
        'Controller/GitController.py',
        'Controller/SystemController.py',
        'Controller/GitProtocol/__init__.py',
        'Controller/GitProtocol/GitProtocols.py'
    ],
    pathex=['.'],
    binaries=[],
    datas=[
        ('View/', 'View/'),
        ('Controller/', 'Controller/'),
        ('Controller/GitProtocol', 'Controller/GitProtocol'),
        ('Model/', 'Model/'),
        ('Resources/', 'Resources/'),
        ('Resources/Img', 'Resources/Img'),
        ('Resources/Img/arrowDown.png', 'Resources/Img/'),
        ('Resources/Img/arrowUp.png', 'Resources/Img/'),
        ('Resources/Img/checkmark.png', 'Resources/Img/'),
        ('Resources/Img/cross.png', 'Resources/Img/'),
        ('Resources/Img/default_icon.ico', 'Resources/Img/'),
        ('Resources/Img/mayaico.png', 'Resources/Img/'),
        ('Resources/Img/plus.png', 'Resources/Img/'),
        ('Resources/Img/singleplayer.png', 'Resources/Img/'),
        ('Resources/Img/soleil_default.jpg', 'Resources/Img/'),
        ('configFile.toml', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Rigging Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Resources/Img/default_icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)