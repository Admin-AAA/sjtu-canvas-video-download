import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import sys
import os
import json
from PIL import ImageTk
from sjtu_login import *
from sjtu_style import (
    COLORS, FONT_BASE, FONT_SMALL, card, field_label, primary_button, secondary_button,
)

self_dirname = os.path.dirname(sys.argv[0])
config_filename = os.path.join(self_dirname, "config.json")


class LoginFrame(tk.Frame):
    def __init__(self, url, callback, master=None, on_success=None):
        super().__init__(master, bg=COLORS["bg"])
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        self.url = url
        self.callback = callback

        if os.path.isfile(config_filename):
            with open(config_filename, encoding="utf-8") as f:
                config = json.load(f)
            self.config_username = config.get("username", "")
            self.config_password = config.get("password", "")
        else:
            self.config_username = ""
            self.config_password = ""

        body = card(self)

        field_label(body, "jAccount 用户名").pack(anchor="w")
        self.username_var = tk.StringVar(value=self.config_username)
        self.username_entry = ttk.Entry(body, textvariable=self.username_var, font=FONT_BASE)
        self.username_entry.pack(fill="x", pady=(4, 12))

        field_label(body, "jAccount 密码").pack(anchor="w")
        self.password_var = tk.StringVar(value=self.config_password)
        self.password_entry = ttk.Entry(body, show="*", textvariable=self.password_var, font=FONT_BASE)
        self.password_entry.pack(fill="x", pady=(4, 12))

        field_label(body, "验证码").pack(anchor="w")
        cap_row = tk.Frame(body, bg=COLORS["panel"])
        cap_row.pack(fill="x", pady=(4, 12))
        self.captcha_label = tk.Label(cap_row, bg=COLORS["panel"], relief="solid",
                                      bd=1, cursor="hand2")
        self.captcha_label.pack(side="left")
        self.captcha_label.bind("<ButtonRelease-1>", lambda e: self.refresh_captcha())
        self.captcha_var = tk.StringVar()
        self.captcha_entry = ttk.Entry(cap_row, textvariable=self.captcha_var, font=FONT_BASE)
        self.captcha_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        rem_row = tk.Frame(body, bg=COLORS["panel"])
        rem_row.pack(fill="x", pady=(0, 14))
        self.username_checkbutton_var = tk.IntVar(value=bool(self.config_username))
        self.username_checkbutton = ttk.Checkbutton(
            rem_row, text="记住用户名", variable=self.username_checkbutton_var,
            command=self.username_checkbutton_changed,
        )
        self.username_checkbutton.pack(side="left")
        self.password_checkbutton_var = tk.IntVar(value=bool(self.config_password))
        self.password_checkbutton = ttk.Checkbutton(
            rem_row, text="记住密码", variable=self.password_checkbutton_var,
            command=self.password_checkbutton_changed,
        )
        self.password_checkbutton.pack(side="left", padx=(16, 0))

        btn_row = tk.Frame(body, bg=COLORS["panel"])
        btn_row.pack(fill="x")
        secondary_button(btn_row, text="刷新验证码", command=self.refresh_all).pack(side="left")
        primary_button(btn_row, text="登录", command=self.try_login).pack(side="right")

        self.refresh_all()

    def refresh_captcha(self):
        self.captcha_img = ImageTk.PhotoImage(get_captcha_img(self.uuid, self.cookies, self.url2))
        self.captcha_label.configure(image=self.captcha_img)

    def refresh_all(self):
        try:
            self.params, self.uuid, self.cookies, self.url2 = get_params_uuid_cookies(self.url)
        except Exception as e:
            tkinter.messagebox.showerror("连接失败", "无法连接登录服务器，请检查网络后点击「刷新验证码」重试。\n\n%s" % e)
            return
        self.refresh_captcha()

    def try_login(self):
        username = self.username_var.get()
        if not username:
            tkinter.messagebox.showerror("登录失败", "请输入用户名")
            return
        password = self.password_var.get()
        if not password:
            tkinter.messagebox.showerror("登录失败", "请输入密码")
            return
        captcha = self.captcha_var.get()
        if not captcha:
            tkinter.messagebox.showerror("登录失败", "请输入验证码")
            return
        result = login(username, password, self.uuid, captcha, self.params, self.cookies)
        if result is None:
            tkinter.messagebox.showerror("登录失败", "请正确填写用户名、密码和验证码")
            self.refresh_all()
        else:
            tkinter.messagebox.showinfo("登录成功", "登录成功")
            self.callback(result)
            if self.on_success:
                self.on_success()
            else:
                self.master.destroy()
            save_user = "" if not self.username_checkbutton_var.get() else username
            save_pass = "" if not self.password_checkbutton_var.get() else password
            if self.config_username != save_user or self.config_password != save_pass:
                with open(config_filename, "w", encoding="utf-8") as f:
                    json.dump({"username": save_user, "password": save_pass}, f, ensure_ascii=False)

    def username_checkbutton_changed(self):
        if not self.username_checkbutton_var.get():
            self.password_checkbutton_var.set(False)

    def password_checkbutton_changed(self):
        if self.password_checkbutton_var.get():
            self.username_checkbutton_var.set(True)
