# project_base.py —— 魔方项目基类
class Project:
    def __init__(self, name, tags=None):
        self.name = name
        self.tags = tags if tags else []

    def get_input_modes(self):
        """返回支持的录入模式，子类可重写"""
        return ["单条录入", "批处理"]

    def validate_time(self, time_str):
        """校验时间输入，返回秒数（浮点数）或 None，子类可重写"""
        try:
            t = float(time_str)
            if 0 < t <= 36000:
                return t
        except:
            pass
        return None
