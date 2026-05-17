# Events/init_event.py —— 初始化事件列表
import os
import json

EVENTS_DIR = "Events"
EVENT_LIST_FILE = os.path.join(EVENTS_DIR, "event_list.json")

DEFAULT_EVENTS = {
    "三阶魔方": "cube_3x3x3.py"
}
def init_events():
    if not os.path.exists(EVENTS_DIR):
        os.makedirs(EVENTS_DIR)

    if os.path.exists(EVENT_LIST_FILE):
        with open(EVENT_LIST_FILE, "r", encoding="utf-8") as f:
            event_list = json.load(f)
    else:
        event_list = {}

    for name, filename in DEFAULT_EVENTS.items():
        filepath = os.path.join(EVENTS_DIR, filename)
        if os.path.exists(filepath) and name not in event_list:
            event_list[name] = filename

    with open(EVENT_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(event_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    init_events()
