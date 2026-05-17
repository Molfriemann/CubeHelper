# main.py —— 魔方成绩处理程序入口 (v0.1.0-test.4)
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from check_utils import init_check_bin, verify_check_bin
from user_manager import UserManager
from event_manager import EventManager
from data_manager import UserDataManager
from app import __version__


# ----------------------------- 登录对话框 -----------------------------
def login_dialog(user_mgr):
    dlg = tk.Toplevel()
    dlg.title("用户登录")
    dlg.geometry("350x220")
    dlg.resizable(False, False)
    dlg.grab_set()

    result = {'username': None, 'is_admin': False}

    f1 = ttk.Frame(dlg)
    f1.pack(pady=(20, 5))
    ttk.Label(f1, text="用户名：").pack(side=tk.LEFT)
    user_var = tk.StringVar()
    names = [u['name'] for u in user_mgr.users] if user_mgr.users else ["admin"]
    combo = ttk.Combobox(f1, textvariable=user_var, values=names, state="readonly", width=20)
    combo.pack(side=tk.LEFT, padx=5)
    combo.current(0)

    f2 = ttk.Frame(dlg)
    f2.pack(pady=5)
    lbl_pw = ttk.Label(f2, text="密  码：")
    lbl_pw.pack(side=tk.LEFT)
    entry_pw = ttk.Entry(f2, show="*", width=25)
    entry_pw.pack(side=tk.LEFT, padx=5)

    def update_pw_state(*args):
        uname = user_var.get()
        info = user_mgr.get_user_info(uname)
        need_pw = False
        if uname == 'admin':
            need_pw = user_mgr.admin_require_password
        elif info:
            need_pw = info.get('require_password', False)
        if need_pw:
            lbl_pw.config(state=tk.NORMAL)
            entry_pw.config(state=tk.NORMAL)
        else:
            lbl_pw.config(state=tk.DISABLED)
            entry_pw.config(state=tk.DISABLED)
            entry_pw.delete(0, tk.END)
    combo.bind("<<ComboboxSelected>>", update_pw_state)
    update_pw_state()

    f3 = ttk.Frame(dlg)
    f3.pack(pady=15)

    def on_login():
        uname = user_var.get().strip()
        if not uname:
            messagebox.showwarning("提示", "请选择用户")
            return
        if entry_pw.cget('state') == 'normal':
            pw = entry_pw.get().strip()
            if uname == 'admin':
                if not user_mgr.verify_admin_password(pw):
                    messagebox.showerror("错误", "密码错误")
                    return
            else:
                if not user_mgr.verify_user_password(uname, pw):
                    messagebox.showerror("错误", "密码错误")
                    return
        result['username'] = uname
        result['is_admin'] = (uname == 'admin')
        dlg.destroy()

    ttk.Button(f3, text="登录", command=on_login).pack(side=tk.LEFT, padx=10)
    ttk.Button(f3, text="退出程序", command=dlg.destroy).pack(side=tk.LEFT, padx=10)

    dlg.wait_window()
    return result['username'], result['is_admin']


# ----------------------------- 管理员界面 -----------------------------
class AdminPanel:
    def __init__(self, root, user_mgr):
        self.root = root
        self.user_mgr = user_mgr
        self.root.deiconify()
        self.root.title(f"魔方成绩处理程序 v{__version__} - 管理员模式")
        for w in self.root.winfo_children():
            w.destroy()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_users = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_users, text="用户管理")
        self._build_user_tab()

        ttk.Button(self.root, text="登出", command=self.logout).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=5)

    def _build_user_tab(self):
        f = ttk.Frame(self.tab_users, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(f)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.user_listbox = tk.Listbox(list_frame, height=8)
        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.user_listbox.yview)
        self.user_listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._refresh_user_list()

        btn_frame = ttk.Frame(f)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="新建用户", command=self.create_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="修改用户", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="注销用户", command=self.delete_user).pack(side=tk.LEFT, padx=5)

    def _refresh_user_list(self):
        self.user_listbox.delete(0, tk.END)
        for u in self.user_mgr.users:
            extra = " [管理员]" if u['name'] == 'admin' else ""
            extra += " [密码保护]" if u.get('require_password') else " [免密]"
            self.user_listbox.insert(tk.END, u['name'] + extra)

    def create_user(self):
        name = simpledialog.askstring("新建用户", "输入用户名：", parent=self.root)
        if name and (name := name.strip()):
            if self.user_mgr.get_user_info(name):
                messagebox.showwarning("错误", "用户已存在")
                return
            self.user_mgr.create_user(name)
            self._refresh_user_list()

    def edit_user(self):
        sel = self.user_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请选择用户")
            return
        idx = sel[0]
        user = self.user_mgr.users[idx]
        is_admin = (user['name'] == 'admin')

        win = tk.Toplevel(self.root)
        win.title("编辑用户")
        win.geometry("350x250")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="用户名：").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_var = tk.StringVar(value=user['name'])
        entry_name = ttk.Entry(win, textvariable=name_var)
        entry_name.grid(row=0, column=1, padx=5, pady=5)
        if is_admin:
            entry_name.configure(state='disabled')

        require_var = tk.BooleanVar(value=user.get('require_password', False))
        ttk.Checkbutton(win, text="登录时需要密码", variable=require_var).grid(row=1, column=0, columnspan=2, sticky='w', padx=5)

        ttk.Label(win, text="新密码：").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        new_pw = ttk.Entry(win, show="*")
        new_pw.grid(row=2, column=1, padx=5)
        ttk.Label(win, text="确认密码：").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        conf_pw = ttk.Entry(win, show="*")
        conf_pw.grid(row=3, column=1, padx=5)

        def save():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("错误", "用户名不能为空")
                return
            if not is_admin and new_name != user['name'] and self.user_mgr.get_user_info(new_name):
                messagebox.showwarning("错误", "用户名已存在")
                return
            pw = new_pw.get()
            pw2 = conf_pw.get()
            if require_var.get() and pw != pw2:
                messagebox.showwarning("错误", "两次密码不一致")
                return
            if not is_admin:
                old_file = f"Users/{user['name']}.json"
                new_file = f"Users/{new_name}.json"
                if old_file != new_file and os.path.exists(old_file):
                    os.rename(old_file, new_file)
                user['name'] = new_name
            if require_var.get() and pw:
                user['password_hash'] = self.user_mgr.hash_password(pw)
            elif not require_var.get():
                user['password_hash'] = ""
            user['require_password'] = require_var.get()
            self.user_mgr.save_user_list()
            if user['name'] == 'admin':
                self.user_mgr.admin_require_password = require_var.get()
                self.user_mgr.admin_password_hash = user['password_hash']
                self.user_mgr.save_admin()
            self._refresh_user_list()
            win.destroy()

        ttk.Button(win, text="保存修改", command=save).grid(row=4, column=0, columnspan=2, pady=15)

    def delete_user(self):
        sel = self.user_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请选择用户")
            return
        user = self.user_mgr.users[sel[0]]
        if user['name'] == 'admin':
            messagebox.showwarning("禁止", "不能注销管理员")
            return
        if messagebox.askyesno("确认注销", f"确定注销用户“{user['name']}”并删除其所有数据吗？"):
            data_file = f"Users/{user['name']}.json"
            if os.path.exists(data_file):
                os.remove(data_file)
            self.user_mgr.users.pop(sel[0])
            self.user_mgr.save_user_list()
            self._refresh_user_list()

    def logout(self):
        self.root.withdraw()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.quit()


# ----------------------------- 普通用户界面 -----------------------------
class UserMainView:
    def __init__(self, root, username, user_data, event_mgr):
        self.root = root
        self.username = username
        self.user_data = user_data
        self.event_mgr = event_mgr
        self.root.deiconify()
        self.root.title(f"魔方成绩处理程序 v{__version__} - {username}")
        for w in self.root.winfo_children():
            w.destroy()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_help = ttk.Frame(self.notebook)
        self.tab_manage = ttk.Frame(self.notebook)
        self.tab_view = ttk.Frame(self.notebook)
        self.tab_input = ttk.Frame(self.notebook)
        self.tab_user = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_help, text="使用说明")
        self.notebook.add(self.tab_manage, text="项目管理")
        self.notebook.add(self.tab_view, text="查看成绩")
        self.notebook.add(self.tab_input, text="录入成绩")
        self.notebook.add(self.tab_user, text="用户")

        self._init_help_tab()
        self._init_manage_tab()
        self._init_view_tab()
        self._init_input_tab()
        self._init_user_tab()

        ttk.Button(self.root, text="登出", command=self.logout).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=5)

    def _init_help_tab(self):
        f = ttk.Frame(self.tab_help, padding=10)
        f.pack(fill=tk.BOTH, expand=True)
        txt = tk.Text(f, wrap=tk.WORD, font=("微软雅黑", 10))
        scr = ttk.Scrollbar(f, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        help_msg = (
            "欢迎使用魔方成绩处理程序！\n\n"
            "【快速入门】\n"
            "1. 在“项目管理”中创建或导入预设项目。\n"
            "2. 在“录入成绩”中选择项目、输入成绩。\n"
            "3. 在“查看成绩”中分析数据、查看报告。\n\n"
            "【常见模式】\n"
            "- 单条录入：常规练习记录。\n"
            "- 批处理：一次性录入多条练习。\n"
            "- 比赛模式(五次取平均)：用于模拟比赛。\n\n"
            "【用户设置】\n"
            "可在“用户”选项卡中修改密码或注销账号。\n"
        )
        txt.insert("1.0", help_msg)
        txt.config(state=tk.DISABLED)

    # ------------------- 项目管理 -------------------
    def _on_manage_canvas_configure(self, event):
        self.proj_canvas.itemconfig(self.proj_window, width=event.width)
        
    def _init_manage_tab(self):
        self.manage_frame = ttk.Frame(self.tab_manage, padding=10)
        self.manage_frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(self.manage_frame)
        top = ttk.Frame(self.manage_frame)
        top.pack(fill=tk.X, pady=5)
        ttk.Button(top, text="新建项目", command=self.add_project).pack(side=tk.LEFT, padx=5)
        if self.event_mgr.presets:
            ttk.Button(top, text="从预设导入", command=self.show_preset_dialog).pack(side=tk.LEFT, padx=5)
        self.proj_canvas = tk.Canvas(self.manage_frame)
        scrollbar = ttk.Scrollbar(self.manage_frame, orient=tk.VERTICAL, command=self.proj_canvas.yview)
        self.proj_inner = ttk.Frame(self.proj_canvas)
        self.proj_inner.bind("<Configure>", lambda e: self.proj_canvas.configure(scrollregion=self.proj_canvas.bbox("all")))
        self.proj_canvas.create_window((0,0), window=self.proj_inner, anchor="nw")
        self.proj_canvas.configure(yscrollcommand=scrollbar.set)
        self.proj_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.render_projects()
        self.proj_canvas = tk.Canvas(self.manage_frame)
        scrollbar = ttk.Scrollbar(self.manage_frame, orient=tk.VERTICAL, command=self.proj_canvas.yview)
        self.proj_inner = ttk.Frame(self.proj_canvas)
        self.proj_inner.bind("<Configure>", lambda e: self.proj_canvas.configure(scrollregion=self.proj_canvas.bbox("all")))
        self.proj_window = self.proj_canvas.create_window((0,0), window=self.proj_inner, anchor="nw")
        self.proj_canvas.bind("<Configure>", self._on_manage_canvas_configure)   # 新增绑定
        self.proj_canvas.configure(yscrollcommand=scrollbar.set)
        self.proj_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def render_projects(self):
        for w in self.proj_inner.winfo_children():
            w.destroy()
        if not self.user_data.projects:
            ttk.Label(self.proj_inner, text="暂无项目，请创建或导入。").pack(pady=20)
            return
        for proj_name, info in self.user_data.projects.items():
            f = ttk.LabelFrame(self.proj_inner, text=proj_name, padding=5)
            f.pack(fill=tk.X, padx=10, pady=5)
            tags = info.get("tags", [])
            lb = tk.Listbox(f, height=min(6, max(1, len(tags))))
            lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            for t in tags:
                lb.insert(tk.END, t)
            btnf = ttk.Frame(f)
            btnf.pack(side=tk.RIGHT, padx=5)
            ttk.Button(btnf, text="新增标签", command=lambda n=proj_name: self.add_tag(n)).pack(side=tk.TOP, pady=2)
            ttk.Button(btnf, text="删除标签", command=lambda n=proj_name: self.delete_tag(n)).pack(side=tk.TOP, pady=2)
            ttk.Button(btnf, text="删除项目", command=lambda n=proj_name: self.delete_project(n)).pack(side=tk.TOP, pady=2)

    def add_project(self):
        name = simpledialog.askstring("新建项目", "项目名称：", parent=self.root)
        if name and (name := name.strip()):
            self.user_data.add_project(name)
            self.render_projects()

    def delete_project(self, name):
        if messagebox.askyesno("确认删除", f"删除项目“{name}”及其所有成绩？"):
            self.user_data.delete_project(name)
            self.render_projects()

    def add_tag(self, proj_name):
        tag = simpledialog.askstring("新增标签", f"为“{proj_name}”添加标签：", parent=self.root)
        if tag and (tag := tag.strip()):
            self.user_data.add_tag(proj_name, tag)
            self.render_projects()

    def delete_tag(self, proj_name):
        proj = self.user_data.projects.get(proj_name)
        if not proj:
            return
        # 获取选中的标签 (简单方法：从项目卡片的 Listbox 获取选中项)
        for child in self.proj_inner.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == proj_name:
                lb = child.winfo_children()[0]
                sel = lb.curselection()
                if not sel:
                    messagebox.showinfo("提示", "请先选择标签")
                    return
                tag = lb.get(sel[0])
                # 预设保护
                if proj.get("preset") and proj.get("preset_name"):
                    preset_class = self.event_mgr.presets.get(proj["preset_name"])
                    if preset_class and tag in preset_class().tags:
                        messagebox.showwarning("无法删除", "预设标签不可删除")
                        return
                if messagebox.askyesno("确认", f"删除标签“{tag}”？"):
                    self.user_data.remove_tag(proj_name, tag)
                    self.render_projects()
                return

    def show_preset_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("预设项目")
        dlg.geometry("400x250")
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=10)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="选择预设模板：").pack(anchor=tk.W)
        for preset_name, cls in self.event_mgr.presets.items():
            inst = cls()
            row = ttk.Frame(f)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{preset_name}  ({', '.join(inst.tags)})").pack(side=tk.LEFT)
            exists = preset_name in self.user_data.projects
            btn = ttk.Button(row, text="添加", command=lambda n=preset_name, tags=inst.tags: self._add_preset(n, tags, dlg))
            btn.pack(side=tk.RIGHT)
            if exists:
                btn.config(state=tk.DISABLED)
        ttk.Button(dlg, text="关闭", command=dlg.destroy).pack(pady=10)

    def _add_preset(self, name, tags, dlg):
        self.user_data.add_project(name, tags=tags, preset=True, preset_name=name)
        dlg.destroy()
        self.render_projects()

    # ------------------- 查看成绩 -------------------
    def _init_view_tab(self):
        self.view_frame = ttk.Frame(self.tab_view, padding=10)
        self.view_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部选择栏
        bar = ttk.Frame(self.view_frame)
        bar.pack(fill=tk.X, pady=5)
        ttk.Label(bar, text="项目：").pack(side=tk.LEFT)
        self.view_proj_var = tk.StringVar()
        proj_names = list(self.user_data.projects.keys())
        self.view_proj_combo = ttk.Combobox(bar, textvariable=self.view_proj_var, values=proj_names, state="readonly", width=15)
        self.view_proj_combo.pack(side=tk.LEFT, padx=5)
        self.view_proj_combo.bind("<<ComboboxSelected>>", lambda e: self.on_view_project_changed())

        # 对于三阶魔方预设，增加单次/平均选择
        self.view_mode_var = tk.StringVar(value="单次")
        self.view_mode_combo = ttk.Combobox(bar, textvariable=self.view_mode_var, state="readonly", width=6)
        self.view_mode_combo.pack(side=tk.LEFT, padx=5)
        self.view_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.load_view_data())

        # 排序切换
        self.sort_order = "时间降序"  # 默认最近→最久
        ttk.Button(bar, text="切换排序", command=self.toggle_sort).pack(side=tk.LEFT, padx=5)

        # 表格区域
        tree_frame = ttk.Frame(self.view_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.view_tree = ttk.Treeview(tree_frame, columns=("序号","成绩","标签","时间","备注","模式"), show="headings", height=12)
        self.view_tree.heading("序号", text="序号")
        self.view_tree.heading("成绩", text="成绩")
        self.view_tree.heading("标签", text="标签")
        self.view_tree.heading("时间", text="录入时间")
        self.view_tree.heading("备注", text="备注")
        self.view_tree.heading("模式", text="模式")
        self.view_tree.column("序号", width=50)
        self.view_tree.column("成绩", width=100)
        self.view_tree.column("标签", width=120)
        self.view_tree.column("时间", width=150)
        self.view_tree.column("备注", width=150)
        self.view_tree.column("模式", width=80)
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.view_tree.yview)
        self.view_tree.configure(yscrollcommand=scroll.set)
        self.view_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 操作按钮
        btnf = ttk.Frame(self.view_frame)
        btnf.pack(fill=tk.X, pady=5)
        ttk.Button(btnf, text="修改成绩", command=self.edit_selected_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btnf, text="删除成绩", command=self.delete_selected_record).pack(side=tk.LEFT, padx=5)

        self.load_view_data()

    def on_view_project_changed(self):
        proj = self.view_proj_var.get()
        if proj in self.user_data.projects:
            # 检查是否为三阶魔方预设
            if proj == "三阶魔方" and self.user_data.projects[proj].get("preset"):
                self.view_mode_combo.config(values=["单次","平均"], state="readonly")
                self.view_mode_var.set("单次")
            else:
                self.view_mode_combo.config(values=["单次"], state="disabled")
                self.view_mode_var.set("单次")
        self.load_view_data()

    def load_view_data(self):
        proj = self.view_proj_var.get()
        if not proj:
            return
        for row in self.view_tree.get_children():
            self.view_tree.delete(row)
        mode = self.view_mode_var.get()
        if mode == "平均":
            # 计算平均
            avg_data = self.user_data.get_competition_averages(proj)
            if self.sort_order.startswith("时间"):
                avg_data.sort(key=lambda x: x["timestamp"], reverse=True)
            else:
                # 按平均成绩升序，DNF排最后
                avg_data.sort(key=lambda x: (isinstance(x["average"], str), x["average"] if isinstance(x["average"], float) else 9999))
            for i, ad in enumerate(avg_data, 1):
                avg_str = f"{ad['average']:.3f}" if isinstance(ad["average"], float) else "#DNF"
                best_str = f"{ad['best_time']:.3f}" if ad['best_time'] else "-"
                worst_str = f"{ad['worst_time']:.3f}" if ad['worst_time'] else "-"
                self.view_tree.insert("", tk.END, values=(i, avg_str, f"最好{best_str}/最差{worst_str}", ad["timestamp"], "", "比赛"))
        else:
            # 单次成绩：显示所有非比赛模式的记录（或所有记录？先所有）
            records = self.user_data.records.get(proj, [])
            if self.sort_order.startswith("时间"):
                records.sort(key=lambda r: r["timestamp"], reverse=True)
            else:
                records.sort(key=lambda r: r["time_seconds"])
            for i, rec in enumerate(records, 1):
                time_str = f"{rec['time_seconds']:.3f}" if not rec["invalid"] else "#DNF"
                tags_str = ", ".join(rec.get("tags", []))
                self.view_tree.insert("", tk.END, values=(i, time_str, tags_str, rec["timestamp"], rec.get("note",""), rec.get("input_mode","")))

    def toggle_sort(self):
        if self.sort_order.startswith("时间"):
            self.sort_order = "成绩升序"  # 最好→最差
        else:
            self.sort_order = "时间降序"
        self.load_view_data()

    def edit_selected_record(self):
        sel = self.view_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请选择一条记录")
            return
        # 获取记录 ID（需从原始数据中查找）
        # 这里简化：仅支持单次记录的编辑，平均不支持
        if self.view_mode_var.get() != "单次":
            messagebox.showinfo("提示", "仅单次成绩可编辑")
            return
        proj = self.view_proj_var.get()
        records = self.user_data.records.get(proj, [])
        idx = int(self.view_tree.item(sel[0], "values")[0]) - 1
        if 0 <= idx < len(records):
            rec = records[idx]
            self.open_edit_window(proj, rec)

    def open_edit_window(self, proj, rec):
        win = tk.Toplevel(self.root)
        win.title("修改成绩")
        win.geometry("400x300")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="成绩(秒)：").grid(row=0, column=0, padx=5, pady=5)
        time_var = tk.StringVar(value=str(rec["time_seconds"]))
        ttk.Entry(win, textvariable=time_var).grid(row=0, column=1, padx=5)

        ttk.Label(win, text="备注：").grid(row=1, column=0, padx=5)
        note_var = tk.StringVar(value=rec.get("note",""))
        ttk.Entry(win, textvariable=note_var).grid(row=1, column=1, padx=5)

        # 标签编辑可省略，先不修改标签

        def save():
            try:
                new_time = float(time_var.get())
                if new_time <= 0 or new_time > 36000:
                    raise ValueError
            except:
                messagebox.showerror("错误", "无效时间")
                return
            self.user_data.edit_record(proj, rec["id"], new_time=round(new_time,3), new_note=note_var.get())
            win.destroy()
            self.load_view_data()

        ttk.Button(win, text="保存", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_selected_record(self):
        sel = self.view_tree.selection()
        if not sel:
            return
        proj = self.view_proj_var.get()
        if not proj:
            return
        records = self.user_data.records.get(proj, [])
        idx = int(self.view_tree.item(sel[0], "values")[0]) - 1
        if idx < 0 or idx >= len(records):
            return
        rec = records[idx]
        rid = rec["id"]
        # 确定是否为批处理或比赛模式（id含有"-"）
        if "-" in rid:
            base_id = rid.split("-")[0]
            batch_ids = [r["id"] for r in records if r["id"].startswith(base_id + "-")]
            msg = f"将删除该批次的所有 {len(batch_ids)} 条成绩，确定吗？"
        else:
            batch_ids = [rid]
            msg = "确定要删除该条成绩吗？"
        if not messagebox.askyesno("确认删除", msg):
            return
        for bid in batch_ids:
            self.user_data.delete_record(proj, bid)
        self.load_view_data()

    # ------------------- 录入成绩 -------------------
    def _init_input_tab(self):
        self.input_frame = ttk.Frame(self.tab_input, padding=10)
        self.input_frame.pack(fill=tk.BOTH, expand=True)

        # 项目选择
        bar = ttk.Frame(self.input_frame)
        bar.pack(fill=tk.X, pady=5)
        ttk.Label(bar, text="项目：").pack(side=tk.LEFT)
        self.input_proj_var = tk.StringVar()
        proj_names = list(self.user_data.projects.keys())
        self.input_proj_combo = ttk.Combobox(bar, textvariable=self.input_proj_var, values=proj_names, state="readonly", width=15)
        self.input_proj_combo.pack(side=tk.LEFT, padx=5)
        self.input_proj_combo.bind("<<ComboboxSelected>>", lambda e: self.on_input_project_changed())

        # 模式选择
        ttk.Label(bar, text="模式：").pack(side=tk.LEFT, padx=(10,0))
        self.input_mode_var = tk.StringVar(value="单条录入")
        self.input_mode_combo = ttk.Combobox(bar, textvariable=self.input_mode_var, state="readonly", width=12)
        self.input_mode_combo.pack(side=tk.LEFT, padx=5)
        self.input_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.update_input_panel())

        # 标签选择
        self.tag_vars = []
        self.tag_frame = ttk.LabelFrame(self.input_frame, text="标签", padding=5)
        self.tag_frame.pack(fill=tk.X, pady=5)

        # 动态输入面板
        self.input_panel = ttk.Frame(self.input_frame)
        self.input_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        # 保存按钮
        ttk.Button(self.input_frame, text="保存成绩", command=self.save_input).pack(pady=10)

        if proj_names:
            self.input_proj_var.set(proj_names[0])
            self.on_input_project_changed()

    def on_input_project_changed(self):
        proj = self.input_proj_var.get()
        self.tag_vars.clear()
        for w in self.tag_frame.winfo_children():
            w.destroy()
        if proj in self.user_data.projects:
            tags = self.user_data.projects[proj].get("tags", [])
            for tag in tags:
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.tag_frame, text=tag, variable=var)
                cb.pack(side=tk.LEFT, padx=5)
                self.tag_vars.append((tag, var))
            # 更新模式列表
            proj_info = self.user_data.projects[proj]
            if proj_info.get("preset") and proj_info.get("preset_name"):
                cls = self.event_mgr.presets.get(proj_info["preset_name"])
                if cls:
                    inst = cls()
                    modes = inst.get_input_modes()
                else:
                    modes = ["单条录入", "批处理"]
            else:
                modes = ["单条录入", "批处理"]
            self.input_mode_combo.config(values=modes)
            self.input_mode_var.set(modes[0])
            self.update_input_panel()

    def update_input_panel(self):
        for w in self.input_panel.winfo_children():
            w.destroy()
        mode = self.input_mode_var.get()
        if mode == "单条录入":
            self._build_single_input()
        elif mode == "批处理":
            self._build_batch_input()
        elif mode == "比赛模式(五次取平均)":
            self._build_comp_input()

    def _build_single_input(self):
        f = ttk.Frame(self.input_panel, padding=5)
        f.pack(fill=tk.X)
        ttk.Label(f, text="总秒数：").pack(side=tk.LEFT)
        self.single_time_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.single_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(f, text="时分秒：").pack(side=tk.LEFT, padx=(10,0))
        self.h_var = tk.StringVar()
        self.m_var = tk.StringVar()
        self.s_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.h_var, width=4).pack(side=tk.LEFT)
        ttk.Label(f, text="时").pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.m_var, width=4).pack(side=tk.LEFT)
        ttk.Label(f, text="分").pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.s_var, width=6).pack(side=tk.LEFT)
        ttk.Label(f, text="秒").pack(side=tk.LEFT)
        # 联动简化：保存时才计算
        # 备注
        ttk.Label(f, text="  备注：").pack(side=tk.LEFT, padx=(10,0))
        self.single_note_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.single_note_var).pack(side=tk.LEFT, padx=5)
        # 无效标记
        self.single_invalid_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="DNF", variable=self.single_invalid_var).pack(side=tk.LEFT, padx=5)

    def _build_batch_input(self):
        # 简化：输入数量
        f = ttk.Frame(self.input_panel)
        f.pack(fill=tk.X, pady=5)
        ttk.Label(f, text="成绩数量：").pack(side=tk.LEFT)
        self.batch_count_var = tk.StringVar(value="5")
        ttk.Entry(f, textvariable=self.batch_count_var, width=4).pack(side=tk.LEFT)
        ttk.Button(f, text="生成输入", command=self.generate_batch_entries).pack(side=tk.LEFT, padx=5)
        self.batch_entries_frame = ttk.Frame(self.input_panel)
        self.batch_entries_frame.pack(fill=tk.X)

    def generate_batch_entries(self):
        for w in self.batch_entries_frame.winfo_children():
            w.destroy()
        try:
            n = int(self.batch_count_var.get())
            if n < 1: n = 1
        except:
            n = 5
        self.batch_time_vars = []
        for i in range(n):
            row = ttk.Frame(self.batch_entries_frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=f"第{i+1}次：").pack(side=tk.LEFT)
            var = tk.StringVar()
            ttk.Entry(row, textvariable=var, width=8).pack(side=tk.LEFT, padx=5)
            self.batch_time_vars.append(var)
        # 共同备注
        ttk.Label(self.batch_entries_frame, text="共同备注：").pack(side=tk.LEFT, padx=(10,0))
        self.batch_note_var = tk.StringVar()
        ttk.Entry(self.batch_entries_frame, textvariable=self.batch_note_var).pack(side=tk.LEFT)

    def _build_comp_input(self):
        f = ttk.Frame(self.input_panel)
        f.pack(fill=tk.X)
        self.comp_time_vars = []
        self.comp_dnf_vars = []
        for i in range(5):
            row = ttk.Frame(f)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=f"第{i+1}次：").pack(side=tk.LEFT)
            var = tk.StringVar()
            ttk.Entry(row, textvariable=var, width=8).pack(side=tk.LEFT, padx=5)
            dnf_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(row, text="DNF", variable=dnf_var).pack(side=tk.LEFT)
            self.comp_time_vars.append(var)
            self.comp_dnf_vars.append(dnf_var)
        ttk.Label(f, text="共同备注：").pack(side=tk.LEFT, padx=(10,0))
        self.comp_note_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.comp_note_var).pack(side=tk.LEFT)

    def save_input(self):
        proj = self.input_proj_var.get()
        if not proj:
            messagebox.showwarning("提示", "请选择项目")
            return
        mode = self.input_mode_var.get()
        tags = [t for t, v in self.tag_vars if v.get()]
        if mode == "单条录入":
            # 获取时间（优先总秒数）
            time_sec = None
            if self.single_time_var.get():
                try:
                    time_sec = float(self.single_time_var.get())
                except:
                    pass
            if time_sec is None:
                # 尝试从时分秒计算
                try:
                    h = int(self.h_var.get()) if self.h_var.get() else 0
                    m = int(self.m_var.get()) if self.m_var.get() else 0
                    s = float(self.s_var.get()) if self.s_var.get() else 0
                    time_sec = h*3600 + m*60 + s
                except:
                    messagebox.showerror("错误", "无效时间")
                    return
            if time_sec <= 0 or time_sec > 36000:
                messagebox.showerror("错误", "时间需在0-36000秒")
                return
            invalid = self.single_invalid_var.get()
            self.user_data.add_record(proj, time_sec, tags, note=self.single_note_var.get(), invalid=invalid, input_mode="单条录入")
            messagebox.showinfo("成功", "成绩已保存")
        elif mode == "批处理":
            times = []
            for var in self.batch_time_vars:
                try:
                    t = float(var.get())
                    if t <= 0 or t > 36000:
                        raise ValueError
                    times.append(t)
                except:
                    messagebox.showerror("错误", "存在无效时间")
                    return
            self.user_data.add_batch_records(proj, times, tags, input_mode="批处理", notes_list=None)  # 可扩展单个备注
            messagebox.showinfo("成功", f"已保存 {len(times)} 条成绩")
        elif mode == "比赛模式(五次取平均)":
            times = []
            for i in range(5):
                if self.comp_dnf_vars[i].get():
                    times.append(None)
                else:
                    try:
                        t = float(self.comp_time_vars[i].get())
                        if t <= 0 or t > 36000:
                            raise ValueError
                        times.append(t)
                    except:
                        messagebox.showerror("错误", f"第{i+1}次时间无效")
                        return
            self.user_data.add_competition_records(proj, times, tags)
            messagebox.showinfo("成功", "比赛成绩已保存")
        else:
            return
        # 清空输入（简单处理）
        self.update_input_panel()

    # ------------------- 用户设置 -------------------
    def _init_user_tab(self):
        f = ttk.Frame(self.tab_user, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text=f"当前用户：{self.username}", font=("微软雅黑", 11)).pack(pady=5)

        btn_frame = ttk.Frame(f)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="修改密码/免密", command=self.change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="注销账号", command=self.delete_account).pack(side=tk.LEFT, padx=5)

    def change_password(self):
        user_mgr = UserManager()
        user_mgr.load_admin()
        user_mgr.load_user_list()
        info = user_mgr.get_user_info(self.username)
        if not info:
            messagebox.showerror("错误", "用户信息丢失")
            return
        win = tk.Toplevel(self.root)
        win.title("修改密码")
        win.geometry("300x200")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="新密码：").grid(row=0, column=0, padx=5, pady=5)
        pw1 = ttk.Entry(win, show="*")
        pw1.grid(row=0, column=1, padx=5)
        ttk.Label(win, text="确认密码：").grid(row=1, column=0, padx=5)
        pw2 = ttk.Entry(win, show="*")
        pw2.grid(row=1, column=1, padx=5)

        require_var = tk.BooleanVar(value=info.get('require_password', False))
        ttk.Checkbutton(win, text="登录时需要密码", variable=require_var).grid(row=2, column=0, columnspan=2, pady=5)

        def save():
            p1 = pw1.get()
            p2 = pw2.get()
            if require_var.get() and p1 != p2:
                messagebox.showwarning("错误", "两次密码不一致")
                return
            info['require_password'] = require_var.get()
            if require_var.get() and p1:
                info['password_hash'] = user_mgr.hash_password(p1)
            elif not require_var.get():
                info['password_hash'] = ""
            user_mgr.save_user_list()
            messagebox.showinfo("成功", "密码设置已更新")
            win.destroy()

        ttk.Button(win, text="保存", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_account(self):
        if messagebox.askyesno("注销账号", "确定注销账号并删除所有数据吗？此操作不可恢复！"):
            user_mgr = UserManager()
            user_mgr.load_admin()
            user_mgr.load_user_list()
            user_mgr.delete_user(self.username)
            data_file = f"Users/{self.username}.json"
            if os.path.exists(data_file):
                os.remove(data_file)
            self.user_data = None
            self.logout()

    def logout(self):
        if self.user_data:
            self.user_data.save()
        self.root.withdraw()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.quit()


# ----------------------------- 主函数 -----------------------------
def main():
    if not os.path.exists("check.bin"):
        init_check_bin()
    else:
        if not verify_check_bin():
            messagebox.showerror("错误", "项目路径校验失败，请检查文件完整性。")
            return

    user_mgr = UserManager()
    user_mgr.load_admin()
    user_mgr.load_user_list()

    event_mgr = EventManager()
    event_mgr.load_presets()

    root = tk.Tk()
    root.withdraw()

    while True:
        username, is_admin = login_dialog(user_mgr)
        if not username:
            break

        if is_admin:
            panel = AdminPanel(root, user_mgr)
            root.mainloop()
            if not tk._default_root:
                break
        else:
            user_data = UserDataManager(username)
            user_data.load()
            view = UserMainView(root, username, user_data, event_mgr)
            root.mainloop()
            if not tk._default_root:
                break

    try:
        root.destroy()
    except:
        pass


if __name__ == "__main__":
    main()
