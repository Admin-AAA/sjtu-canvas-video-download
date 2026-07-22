"""下载视图：输入课程ID → 加载讲次 → 下载。"""
import re
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.messagebox

from sjtu_canvas_video_download import download_courses
from sjtu_real_canvas_video_v2 import get_real_canvas_videos_v2 as get_real_canvas_videos
from sjtu_style import (
    COLORS, FONT_BASE, FONT_SMALL, heading, card, field_label,
    primary_button, secondary_button,
)


def remove_invalid_chars(s):
    return re.sub(r"[<>:\"/\\|?*\s]", "_", s)


def get_course_filename_ext(course_link):
    right_index = course_link.find('?')
    left_index = course_link.rfind('.', 0, right_index)
    return course_link[left_index:right_index]


class DownloadView(tk.Frame):
    def __init__(self, app, master=None):
        tk.Frame.__init__(self, master, bg=COLORS["bg"])
        self.app = app
        self.all_courses = app.all_courses
        self.columnconfigure(0, weight=1)

        heading(self, "下载视频", "输入课程ID，加载后一键下载全部讲次。")

        if app.cookies is None and not self.all_courses:
            self._build_login_hint()
            return

        self.partial_var = tk.IntVar()
        self.course_id_var = tk.StringVar()

        self._build_course_id_card()
        self._build_option_card()
        self._build_action_card()

        n = len(self.all_courses[0]) if self.all_courses else 0
        self.set_status("已加载 %d 讲" % n if n else "请输入课程ID")

    def _build_login_hint(self):
        body = card(self)
        tk.Label(
            body, text="请先登录 jAccount 以获取课程与视频信息。",
            bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_SMALL,
        ).pack(anchor="w")
        primary_button(body, text="去登录", command=lambda: self.app.navigate("login")).pack(anchor="w", pady=(12, 0))

    def _build_course_id_card(self):
        body = card(self)
        field_label(body, "课程ID").pack(anchor="w")
        row = tk.Frame(body, bg=COLORS["panel"])
        row.pack(fill="x", pady=(4, 8))
        self.course_id_entry = ttk.Entry(row, textvariable=self.course_id_var)
        self.course_id_entry.pack(side="left", fill="x", expand=True)
        self.course_id_entry.bind("<FocusOut>", lambda e: self._refresh_courses())
        self.refresh_button = secondary_button(row, text="加载课程", command=self._refresh_courses)
        self.refresh_button.pack(side="left", padx=(8, 0))
        tk.Label(
            body, text="https://oc.sjtu.edu.cn/courses/90553 90553是课程id",
            bg=COLORS["panel"], fg=COLORS["faint"], font=FONT_SMALL,
        ).pack(anchor="w")

    def _build_option_card(self):
        body = card(self)
        field_label(body, "保存到").pack(anchor="w")
        row = tk.Frame(body, bg=COLORS["panel"])
        row.pack(fill="x", pady=(4, 12))
        self.video_dirname_var = tk.StringVar()
        self.video_dirname_entry = ttk.Entry(row, textvariable=self.video_dirname_var)
        self.video_dirname_entry.pack(side="left", fill="x", expand=True)
        secondary_button(row, text="浏览", command=self._set_video_dirname).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(body, variable=self.partial_var, text="只下载录像（不下载录屏）").pack(anchor="w")

    def _build_action_card(self):
        body = card(self)
        row = tk.Frame(body, bg=COLORS["panel"])
        row.pack(fill="x")
        secondary_button(row, text="预览文件清单", command=self.preview).pack(side="left")
        self.download_button = primary_button(row, text="开始下载", command=self.initiate_download)
        self.download_button.pack(side="right")

    def _refresh_courses(self):
        if self.app.cookies is None:
            self.set_status("请先登录 jAccount")
            return
        cid = self.course_id_var.get().strip()
        if not cid:
            self.set_status("请输入课程ID")
            return
        self.set_status("正在加载课程视频列表…")
        self.refresh_button.config(state="disabled")
        self.download_button.config(state="disabled")

        def work():
            try:
                courses = get_real_canvas_videos(cid, self.app.cookies)
                self.app.all_courses = courses
                self.app.master.after(0, self._on_courses_loaded)
            except Exception as e:
                self.app.master.after(0, lambda: self._on_courses_error(e))

        threading.Thread(target=work, daemon=True).start()

    def _on_courses_loaded(self):
        self.all_courses = self.app.all_courses
        n = len(self.all_courses[0]) if self.all_courses else 0
        self.refresh_button.config(state="normal")
        self.download_button.config(state="normal")
        self.set_status("已加载 %d 讲" % n)

    def _on_courses_error(self, e):
        self.refresh_button.config(state="normal")
        self.download_button.config(state="normal")
        self.set_status("加载失败：%s" % e)
        tkinter.messagebox.showerror("加载失败", "请检查课程ID、网络或登录状态后重试。\n\n%s" % e)

    def get_course_links_filenames(self):
        if not self.all_courses or not self.all_courses[0]:
            return [], []
        partial = self.partial_var.get()
        links, names = [], []
        for course in self.all_courses[0]:
            s_name = remove_invalid_chars(course["subjName"])
            t_name = remove_invalid_chars(course["userName"])
            c_name = remove_invalid_chars(course["courName"])
            raw = "%s_%s_%s" % (s_name, t_name, c_name)
            dirname = "%s_%s" % (s_name, t_name)
            play_list = course["videoPlayResponseVoList"] or []
            is_normal = bool(play_list) and "cdviViewNum" in play_list[0]
            if is_normal:
                videos = sorted(play_list, key=lambda t: t.get("cdviViewNum", 0))
                for i, video in enumerate(videos):
                    if partial and video.get("cdviViewNum", 0) != 0:
                        continue
                    link = video["rtmpUrlHdv"]
                    ext = get_course_filename_ext(link)
                    fname = "%s/%s%s" % (dirname, raw, ext) if partial else "%s/%s_%s%s" % (dirname, raw, i, ext)
                    links.append(link)
                    names.append(fname)
            else:
                video = play_list[0] if play_list else {}
                link = video.get("rtmpUrlHdv")
                if not link:
                    continue
                ext = get_course_filename_ext(link)
                fname = "%s/%s%s" % (dirname, raw, ext)
                links.append(link)
                names.append(fname)
        return links, names

    def set_status(self, text):
        self.app.set_status(text)

    def _set_video_dirname(self):
        d = tkinter.filedialog.askdirectory()
        if d:
            self.video_dirname_var.set(d)

    def _validate(self):
        if not self.all_courses or not self.all_courses[0]:
            tkinter.messagebox.showerror("错误", "请先输入课程ID并加载")
            return False
        if not self.video_dirname_var.get():
            tkinter.messagebox.showerror("错误", "请指定保存路径")
            return False
        return True

    def initiate_download(self):
        if not self._validate():
            return
        video_dirname = self.video_dirname_var.get()
        self.download_button.config(state="disabled")
        self.set_status("正在获取视频地址并开始下载…")

        def work():
            try:
                links, names = self.get_course_links_filenames()
                if not links:
                    self.app.master.after(0, lambda: tkinter.messagebox.showerror("错误", "没有可下载的视频，请确认已加载课程。"))
                    return
                download_courses(links, names, video_dirname, silent=True)
                self.app.master.after(0, lambda: self.set_status("已提交下载：%d 个视频，请在终端查看进度" % len(links)))
            except Exception as e:
                self.app.master.after(0, lambda: tkinter.messagebox.showerror("获取视频信息失败", "%s\n请检查网络或登录状态后重试。" % e))
            finally:
                self.app.master.after(0, lambda: self.download_button.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

    def preview(self):
        if not self.all_courses or not self.all_courses[0]:
            tkinter.messagebox.showerror("错误", "请先输入课程ID并加载")
            return
        self.set_status("正在生成文件清单…")

        def work():
            try:
                _, names = self.get_course_links_filenames()
                self.app.master.after(0, lambda: self._show_preview(names))
            except Exception as e:
                self.app.master.after(0, lambda: tkinter.messagebox.showerror("获取视频信息失败", "%s\n请检查网络或登录状态后重试。" % e))

        threading.Thread(target=work, daemon=True).start()

    def _show_preview(self, names):
        if not names:
            tkinter.messagebox.showinfo("预览", "没有可下载的视频。")
            return
        win = tk.Toplevel(self.app.master)
        win.title("文件清单（共 %d 个）" % len(names))
        win.geometry("520x420")
        win.transient(self.app.master)
        win.grab_set()
        txt = tk.Text(win, bg=COLORS["panel"], fg=COLORS["text"], font=FONT_SMALL, padx=12, pady=12, wrap="none")
        txt.insert("1.0", "\n".join(names))
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=12, pady=12)
        self.set_status("已加载 %d 讲" % len(self.all_courses[0]) if self.all_courses else 0)
