# check_utils.py —— check.bin 校验
import os
import hashlib
import json

CHECK_FILE = "check.bin"

def init_check_bin():
    """首次运行时创建 check.bin，保存项目路径及其哈希"""
    project_path = os.path.abspath(".")
    hash_code = hashlib.sha256(project_path.encode()).hexdigest()
    data = {
        "path": project_path,
        "hash": hash_code
    }
    with open(CHECK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def verify_check_bin():
    """校验当前路径与 check.bin 中路径的哈希是否一致，并检查文件内容是否被篡改"""
    if not os.path.exists(CHECK_FILE):
        return False
    try:
        with open(CHECK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        stored_path = data.get("path")
        stored_hash = data.get("hash")
        if stored_path != os.path.abspath("."):
            return False
        # 校验 check.bin 自身内容未被篡改
        computed = hashlib.sha256(stored_path.encode()).hexdigest()
        return computed == stored_hash
    except:
        return False
