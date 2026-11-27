from .w import FLUENT
if FLUENT:
    from .main_window_fluent import MainWindow
else:
    from .main_window_basic import MainWindow
