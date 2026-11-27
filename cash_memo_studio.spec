# PyInstaller ONE-FILE build: pyinstaller cash_memo_studio.spec  ->  dist/RiponCashMemoStudio.exe
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# reportlab loads its barcode/graphics modules dynamically (e.g. barcode.code93), so PyInstaller must be told about ALL of them
hidden = collect_submodules('reportlab')
datas = [('assets', 'assets')] + collect_data_files('reportlab')
try:
    hidden += collect_submodules('qfluentwidgets')
    datas += collect_data_files('qfluentwidgets')
except Exception:
    pass

a = Analysis(['app.py'], pathex=['.'], datas=datas, hiddenimports=hidden,
             excludes=['tkinter', 'matplotlib', 'numpy'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='RiponCashMemoStudio', console=False, icon='assets/app.ico', upx=False)
