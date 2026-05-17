# user_manager.py —— 用户管理（管理员 + 用户列表）
import os
import json
import hashlib

ADMIN_FILE = "Users/admin.json"
USER_LIST_FILE = "Users/user_list.json"

class UserManager:
    def __init__(self):
        self.admin_password_hash = ""
        self.admin_require_password = False
        self.users = []  # 每个元素为 dict: name, password_hash, require_password

    def load_admin(self):
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.admin_password_hash = data.get("password_hash", "")
            self.admin_require_password = data.get("require_password", False)
        else:
            self.save_admin()

    def save_admin(self):
        data = {
            "password_hash": self.admin_password_hash,
            "require_password": self.admin_require_password
        }
        os.makedirs("Users", exist_ok=True)
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_user_list(self):
        if os.path.exists(USER_LIST_FILE):
            with open(USER_LIST_FILE, "r", encoding="utf-8") as f:
                self.users = json.load(f)
        else:
            self.users = []
            self.save_user_list()

    def save_user_list(self):
        os.makedirs("Users", exist_ok=True)
        with open(USER_LIST_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)

    def hash_password(self, pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    def verify_admin_password(self, pw):
        if not self.admin_require_password:
            return True
        return self.hash_password(pw) == self.admin_password_hash

    def verify_user_password(self, username, pw):
        for u in self.users:
            if u["name"] == username:
                if u.get("require_password", False):
                    return self.hash_password(pw) == u.get("password_hash", "")
                else:
                    return True
        return False

    def get_user_info(self, username):
        for u in self.users:
            if u["name"] == username:
                return u
        return None

    # ----- 管理员功能 -----
    def create_user(self, name, password="", require_password=False):
        if self.get_user_info(name):
            return False
        self.users.append({
            "name": name,
            "password_hash": self.hash_password(password) if require_password else "",
            "require_password": require_password
        })
        self.save_user_list()
        return True

    def delete_user(self, name):
        if name == "admin":
            return False
        self.users = [u for u in self.users if u["name"] != name]
        self.save_user_list()
        return True

    def update_user(self, old_name, new_name, password=None, require_password=None):
        user = self.get_user_info(old_name)
        if not user:
            return False
        if new_name != old_name and self.get_user_info(new_name):
            return False
        user["name"] = new_name
        if password is not None:
            user["password_hash"] = self.hash_password(password)
        if require_password is not None:
            user["require_password"] = require_password
            if not require_password:
                user["password_hash"] = ""
        self.save_user_list()
        return True
