# Users/init_user.py —— 初始化用户系统
import os
import json

def init_users():
    if not os.path.exists("Users"):
        os.makedirs("Users")

    admin_file = "Users/admin.json"
    if not os.path.exists(admin_file):
        admin_data = {
            "password_hash": "",
            "require_password": False
        }
        with open(admin_file, "w", encoding="utf-8") as f:
            json.dump(admin_data, f, indent=2)

    user_list_file = "Users/user_list.json"
    if not os.path.exists(user_list_file):
        with open(user_list_file, "w", encoding="utf-8") as f:
            json.dump([], f)

if __name__ == "__main__":
    init_users()
