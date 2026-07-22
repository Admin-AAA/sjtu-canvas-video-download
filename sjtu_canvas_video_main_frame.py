"""应用主壳：单窗口 + 侧边栏导航（登录 / 下载 / 历史）。"""
import tkinter as tk
import tkinter.ttk as ttk

from sjtu_login import login_using_cookies
from sjtu_login_frame import LoginFrame
from sjtu_qr_code_login_frame import QRCodeLoginFrame
from sjtu_history_frame import HistoryFrame
from sjtu_download_view import DownloadView
from sjtu_style import (
    apply_theme, COLORS, FONT_BASE, heading, card, primary_button, secondary_button,
)

NAV_ITEMS = [
    ("login", "登录"),
    ("download", "下载"),
    ("history", "历史"),
]


def _round_rect(c, x, y, w, h, r, fill):
    c.create_arc(x, y, x + 2 * r, y + 2 * r, start=90, extent=90, fill=fill, outline=fill)
    c.create_arc(x + w - 2 * r, y, x + w, y + 2 * r, start=0, extent=90, fill=fill, outline=fill)
    c.create_arc(x + w - 2 * r, y + h - 2 * r, x + w, y + h, start=270, extent=90, fill=fill, outline=fill)
    c.create_arc(x, y + h - 2 * r, x + 2 * r, y + h, start=180, extent=90, fill=fill, outline=fill)
    c.create_rectangle(x + r, y, x + w - r, y + h, fill=fill, outline=fill)
    c.create_rectangle(x, y + r, x + w, y + h - r, fill=fill, outline=fill)


class _NavItem(tk.Frame):
    def __init__(self, master, text, command):
        super().__init__(master, bg=COLORS["sidebar_bg"])
        self._command = command
        self._active = False
        self.accent = tk.Frame(self, bg=COLORS["sidebar_bg"], width=3)
        self.accent.pack(side="left", fill="y")
        self.label = tk.Label(
            self, text=text, bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
            font=FONT_BASE, padx=14, pady=9,
        )
        self.label.pack(side="left", fill="x", expand=True)
        for w in (self, self.label):
            w.bind("<Button-1>", lambda e: self._command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        if not self._active:
            self._paint(COLORS["sidebar_hover"], COLORS["sidebar_hover"], COLORS["sidebar_fg"])

    def _on_leave(self, e):
        if not self._active:
            self._paint(COLORS["sidebar_bg"], COLORS["sidebar_bg"], COLORS["sidebar_fg"])

    def _paint(self, frame_bg, label_bg, label_fg):
        self.config(bg=frame_bg)
        self.label.config(bg=label_bg, fg=label_fg)

    def set_active(self, active):
        self._active = active
        if active:
            self._paint(COLORS["primary_soft"], COLORS["primary_soft"], COLORS["primary"])
            self.accent.config(bg=COLORS["primary"])
        else:
            self._paint(COLORS["sidebar_bg"], COLORS["sidebar_bg"], COLORS["sidebar_fg"])
            self.accent.config(bg=COLORS["sidebar_bg"])


class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        apply_theme(master)
        master.title("SJTU Canvas 视频下载器")
        master.geometry("940x640")
        master.minsize("760", "500")

        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.urls = [
            "https://courses.sjtu.edu.cn/app/oauth/2.0/login?login_type=outer",
            "https://oc.sjtu.edu.cn/login/openid_connect",
        ]
        self.all_courses = []
        self.cookies = None
        self.use_course_id = False
        self.course_id = ""
        self._current_view = None
        self._nav_items = {}

        self._build_sidebar()
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.grid(row=0, column=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = tk.Label(
            self, textvariable=self.status_var, anchor="w",
            bg=COLORS["panel"], fg=COLORS["muted"], font=("PingFang SC", 11),
            padx=14, pady=7, highlightbackground=COLORS["border"], highlightthickness=1,
        )
        self.status_bar.grid(row=1, column=1, sticky=tk.W + tk.E)

        self.navigate("login")

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=210)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky=tk.N + tk.S)
        self.sidebar.grid_propagate(False)

        logo = tk.Canvas(self.sidebar, width=40, height=40, bg=COLORS["sidebar_bg"], highlightthickness=0)
        logo.place(x=22, y=26)
        _round_rect(logo, 2, 2, 36, 36, 9, COLORS["primary"])
        logo.create_text(20, 21, text="C", fill="white", font=("PingFang SC", 18, "bold"))
        tk.Label(self.sidebar, text="Canvas 视频下载", bg=COLORS["sidebar_bg"],
                 fg="white", font=("PingFang SC", 14, "bold")).place(x=72, y=30)
        tk.Label(self.sidebar, text="SJTU 课程视频", bg=COLORS["sidebar_bg"],
                 fg=COLORS["sidebar_fg"], font=("PingFang SC", 11)).place(x=72, y=50)

        nav_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        nav_frame.place(x=12, y=110, width=190)
        for name, text in NAV_ITEMS:
            item = _NavItem(nav_frame, text, lambda n=name: self.navigate(n))
            item.pack(fill="x", pady=2)
            self._nav_items[name] = item

        tk.Label(self.sidebar, text="Canvas 视频下载器", bg=COLORS["sidebar_bg"],
                 fg="#5B6675", font=("PingFang SC", 11)).place(x=22, y=600)

    def navigate(self, name):
        if self._current_view is not None:
            self._current_view.destroy()
        for n, item in self._nav_items.items():
            item.set_active(n == name)
        self._current_view = None

        if name == "login":
            self._current_view = LoginView(self, self.content)
        elif name == "download":
            self._current_view = DownloadView(self, self.content)
        elif name == "history":
            self._current_view = HistoryFrame(self.content)
        self._current_view.pack(fill="both", expand=True)

    def on_login(self, cookies):
        login_using_cookies(self.urls[1], cookies)
        self.cookies = cookies
        self.set_status("登录成功，正在加载课程列表…")
        self.navigate("download")

    def set_status(self, text):
        self.status_var.set(str(text))


class LoginView(tk.Frame):
    def __init__(self, app, master=None):
        tk.Frame.__init__(self, master, bg=COLORS["bg"])
        self.app = app
        self.columnconfigure(0, weight=1)

        heading(self, "登录 jAccount", "登录后自动读取你的 Canvas 课程与视频信息。")

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="x", padx=28)
        nb = ttk.Notebook(body)
        nb.pack(fill="x")

        tab_account = tk.Frame(nb, bg=COLORS["panel"])
        tab_qr = tk.Frame(nb, bg=COLORS["panel"])
        nb.add(tab_account, text="账号密码")
        nb.add(tab_qr, text="扫码登录")

        on_success = lambda: app.navigate("download")
        LoginFrame(app.urls[0], lambda cookies: app.on_login(cookies), tab_account, on_success=on_success)
        QRCodeLoginFrame(app.urls[0], lambda cookies: app.on_login(cookies), tab_qr, on_success=on_success)
