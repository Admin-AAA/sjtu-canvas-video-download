import tkinter as tk
import tkinter.messagebox
from PIL import ImageTk
from sjtu_login import get_params_uuid_cookies
from sjtu_qr_code_login import *
from sjtu_style import COLORS, FONT_SMALL, card, secondary_button


class QRCodeLoginFrame(tk.Frame):
    def __init__(self, url, callback, master=None, on_success=None):
        super().__init__(master, bg=COLORS["bg"])
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        self.url = url
        self.callback = callback
        self.wss = None
        self.t = None

        body = card(self)
        tk.Label(body, text="使用 jAccount App 扫码登录", bg=COLORS["panel"],
                 fg=COLORS["muted"], font=FONT_SMALL).pack(anchor="w", pady=(0, 12))

        self.qr_code_label = tk.Label(body, bg=COLORS["panel"], relief="solid", bd=1, cursor="hand2")
        self.qr_code_label.pack(anchor="center", pady=(0, 12))
        self.qr_code_label.bind("<ButtonRelease-1>", lambda e: self.start_refresh_qr_code())

        btn_row = tk.Frame(body, bg=COLORS["panel"])
        btn_row.pack(fill="x", pady=(0, 8))
        secondary_button(btn_row, text="刷新二维码", command=self.refresh_all).pack(side="left")
        tk.Label(body, text="点击二维码可刷新", bg=COLORS["panel"],
                 fg=COLORS["faint"], font=FONT_SMALL).pack(anchor="center", pady=(6, 0))

        self.bind("<<login>>", lambda e: self.login())
        self.refresh_all()

    def start_refresh_qr_code(self):
        send_update_qr_code(self.wss)

    def refresh_qr_code_callback(self, ts, sig):
        self.ts = ts
        self.sig = sig
        self.refresh_qr_code()

    def refresh_qr_code(self):
        self.qr_code_img = ImageTk.PhotoImage(get_qr_code_img(self.uuid, self.ts, self.sig, self.cookies))
        self.qr_code_label.configure(image=self.qr_code_img)

    def login_callback(self):
        self.event_generate("<<login>>", when="tail")

    def login(self):
        tkinter.messagebox.showinfo("登录成功", "登录成功")
        result = qr_code_login(self.uuid, self.cookies)
        self.callback(result)
        if self.on_success:
            self.on_success()
        else:
            self.master.destroy()

    def refresh_all(self):
        try:
            self.params, self.uuid, self.cookies, self.url2 = get_params_uuid_cookies(self.url)
        except Exception as e:
            tkinter.messagebox.showerror("连接失败", "无法连接登录服务器，请检查网络后点击「刷新二维码」重试。\n\n%s" % e)
            return
        if self.wss is not None:
            self.wss.close()
            self.t.join()
        try:
            self.wss, self.t = get_wss(self.uuid, self.cookies, self.refresh_qr_code_callback, self.login_callback)
        except Exception as e:
            tkinter.messagebox.showerror("连接失败", "无法建立登录连接，请检查网络后点击「刷新二维码」重试。\n\n%s" % e)
            return
        self.start_refresh_qr_code()

    def destroy(self):
        if self.wss is not None:
            self.wss.close()
            self.t.join()
        return super().destroy()
