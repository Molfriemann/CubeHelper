# app.py —— 版本号管理与应用入口类（占位）

__version__ = "0.1.0-test.2"

class CubeStatsApp:
    """应用主类，由 main.py 调用，实际界面构建分散在各视图中"""
    def __init__(self, root):
        self.root = root
        self.root.title(f"魔方成绩处理程序 v{__version__}")
