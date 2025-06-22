# main.spec

import os
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files

# Path to selenium-stealth JS files
stealth_js_dir = os.path.join(
    os.environ['VIRTUAL_ENV'], "Lib", "site-packages", "selenium_stealth", "js"
)

# Collect all .js files from selenium_stealth/js
stealth_datas = [
    (os.path.join(stealth_js_dir, file), "selenium_stealth/js")
    for file in os.listdir(stealth_js_dir) if file.endswith(".js")
]

# Add your own folders (Images, Fonts, data)
my_assets = [
    ('Images', 'Images'),
    ('Fonts', 'Fonts')
]

# Final datas
datas = my_assets + stealth_datas

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("scripts"),  # Assuming your custom scripts are in scripts/
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Buy Buddy',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='Images/logo_icon.ico'
)
