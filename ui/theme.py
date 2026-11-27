NAVY, BLUE, CYAN, LIGHT = "#0B2A5B", "#0B6BCB", "#19B5D8", "#EAF2FB"
QSS = f"""
* {{ font-family: 'Noto Sans Bengali','Segoe UI',sans-serif; font-size: 10pt; }}
QMainWindow, QWidget#page {{ background: #F5F8FC; }}
QFrame#sidebar {{ background: {NAVY}; }}
QPushButton#nav {{ color: #CFE3FA; background: transparent; border: none; text-align: left; padding: 11px 18px; font-size: 10.5pt; }}
QPushButton#nav:hover {{ background: #123A78; }}
QPushButton#nav:checked {{ background: {BLUE}; color: white; font-weight: bold; }}
QPushButton {{ background: {BLUE}; color: white; border: none; border-radius: 4px; padding: 7px 14px; }}
QPushButton:hover {{ background: #0A5CB0; }}
QPushButton[secondary="true"] {{ background: white; color: {BLUE}; border: 1px solid {BLUE}; }}
QPushButton[danger="true"] {{ background: #C0392B; }}
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit, QDateEdit {{ background: white; border: 1px solid #B8C7DA; border-radius: 4px; padding: 5px; }}
QTableWidget {{ background: white; gridline-color: #D5E0EE; alternate-background-color: {LIGHT}; }}
QHeaderView::section {{ background: {NAVY}; color: white; padding: 6px; border: none; }}
QLabel#h1 {{ font-size: 17pt; font-weight: bold; color: {NAVY}; }}
QFrame#card {{ background: white; border: 1px solid #D5E0EE; border-radius: 8px; }}
QLabel#statv {{ font-size: 16pt; font-weight: bold; color: {BLUE}; }}
QLabel#statl {{ color: #5A6B80; }}
"""
