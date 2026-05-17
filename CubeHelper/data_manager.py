# data_manager.py —— 用户成绩数据管理（按用户独立文件，逐条存取）
import json
import os
from datetime import datetime

USERS_DIR = "Users"

class UserDataManager:
    def __init__(self, username):
        self.username = username
        self.filepath = os.path.join(USERS_DIR, f"{username}.json")
        # 数据结构
        self.projects = {}        # {项目名: {"tags": [...], "preset": bool, "preset_name": None/str}}
        self.records = {}         # {项目名: [record, ...]}
        self.next_record_id = 1

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.projects = data.get("projects", {})
            self.records = data.get("records", {})
            self.next_record_id = data.get("next_record_id", 1)
        else:
            self.save()

    def save(self):
        data = {
            "projects": self.projects,
            "records": self.records,
            "next_record_id": self.next_record_id
        }
        os.makedirs(USERS_DIR, exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_project(self, name, tags=None, preset=False, preset_name=None):
        if name in self.projects:
            return False
        self.projects[name] = {
            "tags": tags if tags else [],
            "preset": preset,
            "preset_name": preset_name
        }
        self.records[name] = []
        self.save()
        return True

    def delete_project(self, name):
        if name in self.projects:
            del self.projects[name]
        if name in self.records:
            del self.records[name]
        self.save()

    def add_record(self, project_name, time_seconds, tags, note="", invalid=False, input_mode="单条录入"):
        if project_name not in self.records:
            self.records[project_name] = []
        record_id = str(self.next_record_id)
        self.next_record_id += 1
        record = {
            "id": record_id,
            "time_seconds": time_seconds,
            "tags": tags,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": note,
            "invalid": invalid,
            "input_mode": input_mode
        }
        self.records[project_name].append(record)
        self.save()
        return record

    def add_batch_records(self, project_name, times_list, common_tags, notes_list=None, input_mode="批处理"):
        if project_name not in self.records:
            self.records[project_name] = []
        base_id = str(self.next_record_id)
        self.next_record_id += 1
        records = []
        for i, t in enumerate(times_list, 1):
            rid = f"{base_id}-{i}"
            note = notes_list[i-1] if notes_list and i-1 < len(notes_list) else ""
            rec = {
                "id": rid,
                "time_seconds": t,
                "tags": common_tags,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": note,
                "invalid": False,
                "input_mode": input_mode
            }
            self.records[project_name].append(rec)
            records.append(rec)
        self.save()
        return records

    def add_competition_records(self, project_name, times_list, common_tags, notes_list=None):
        """
        比赛模式固定5次录入
        times_list: 长度为5的列表，元素为秒数（数字）或 None（代表DNF）
        """
        if len(times_list) != 5:
            raise ValueError("比赛模式必须录入5次成绩")
        if project_name not in self.records:
            self.records[project_name] = []
        base_id = str(self.next_record_id)
        self.next_record_id += 1
        records = []
        for i, t in enumerate(times_list, 1):
            rid = f"{base_id}-{i}"
            note = notes_list[i-1] if notes_list and i-1 < len(notes_list) else ""
            invalid = (t is None)
            rec = {
                "id": rid,
                "time_seconds": t if t is not None else 0.0,
                "tags": common_tags,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": note,
                "invalid": invalid,
                "input_mode": "比赛模式(五次取平均)"
            }
            self.records[project_name].append(rec)
            records.append(rec)
        self.save()
        return records

    def delete_record(self, project_name, record_id):
        if project_name in self.records:
            self.records[project_name] = [r for r in self.records[project_name] if r["id"] != record_id]
            self.save()

    def edit_record(self, project_name, record_id, new_time=None, new_tags=None, new_note=None):
        rec = self.find_record(project_name, record_id)
        if rec:
            if new_time is not None:
                rec["time_seconds"] = new_time
            if new_tags is not None:
                rec["tags"] = new_tags
            if new_note is not None:
                rec["note"] = new_note
            self.save()

    def find_record(self, project_name, record_id):
        for r in self.records.get(project_name, []):
            if r["id"] == record_id:
                return r
        return None
    def get_competition_averages(self, project_name):
        """返回比赛模式平均成绩列表"""
        records = self.records.get(project_name, [])
        comp_records = [r for r in records if r.get("input_mode") == "比赛模式(五次取平均)"]
        batches = {}
        for r in comp_records:
            base = r["id"].split("-")[0]
            batches.setdefault(base, []).append(r)
        results = []
        for base, batch in batches.items():
            if len(batch) != 5:
                continue
            batch.sort(key=lambda r: int(r["id"].split("-")[1]))
            times = [r["time_seconds"] if not r["invalid"] else None for r in batch]
            dnf_count = sum(1 for t in times if t is None)
            if dnf_count >= 2:
                avg = "DNF"
            else:
                valid = [t for t in times if t is not None]
                if len(valid) < 3:
                    avg = "DNF"
                else:
                    valid.sort()
                    trimmed = valid[1:-1]
                    avg = round(sum(trimmed)/len(trimmed), 3)
            best = min([t for t in times if t is not None]) if any(t is not None for t in times) else None
            worst = max([t for t in times if t is not None]) if any(t is not None for t in times) else None
            results.append({
                "base_id": base,
                "average": avg,
                "best_time": best,
                "worst_time": worst,
                "records": batch,
                "timestamp": batch[0]["timestamp"]
            })
        return results
    def add_tag(self, project_name, tag):
        """为项目添加标签"""
        if project_name in self.projects and tag not in self.projects[project_name]["tags"]:
            self.projects[project_name]["tags"].append(tag)
            self.save()

    def remove_tag(self, project_name, tag):
        """删除标签，预设标签受保护（在界面层判断）"""
        if project_name in self.projects and tag in self.projects[project_name]["tags"]:
            self.projects[project_name]["tags"].remove(tag)
            self.save()
