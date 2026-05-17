# event_manager.py —— 预设项目加载（自动扫描 Events 目录）
import os
import json
import importlib.util

EVENTS_DIR = "Events"
EVENT_LIST_FILE = os.path.join(EVENTS_DIR, "event_list.json")

class EventManager:
    def __init__(self):
        self.presets = {}   # {预设名称: 项目类}

    def load_presets(self):
        """加载预设：扫描 Events 目录，自动更新 event_list.json 并导入预设类"""
        # 确保目录存在
        if not os.path.exists(EVENTS_DIR):
            os.makedirs(EVENTS_DIR)
        # 读取现有列表
        if os.path.exists(EVENT_LIST_FILE):
            with open(EVENT_LIST_FILE, "r", encoding="utf-8") as f:
                event_list = json.load(f)
        else:
            event_list = {}
        # 扫描目录中所有 .py 文件
        need_save = False
        for filename in os.listdir(EVENTS_DIR):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
            filepath = os.path.join(EVENTS_DIR, filename)
            # 尝试加载模块并获取预设名称
            try:
                spec = importlib.util.spec_from_file_location("_preset_scan", filepath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if not hasattr(mod, "ProjectClass"):
                    continue
                # 实例化临时对象以获取名称
                obj = mod.ProjectClass()
                preset_name = obj.name
                if preset_name not in event_list:
                    event_list[preset_name] = filename
                    need_save = True
            except Exception as e:
                # 忽略无效文件
                continue
        # 保存更新后的列表
        if need_save:
            with open(EVENT_LIST_FILE, "w", encoding="utf-8") as f:
                json.dump(event_list, f, indent=2, ensure_ascii=False)
        # 根据最终列表导入所有预设类
        self.presets.clear()
        for name, filename in event_list.items():
            filepath = os.path.join(EVENTS_DIR, filename)
            if not os.path.exists(filepath):
                continue
            try:
                spec = importlib.util.spec_from_file_location(name, filepath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "ProjectClass"):
                    self.presets[name] = mod.ProjectClass
            except:
                continue
