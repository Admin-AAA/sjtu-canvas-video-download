import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import datetime
from sjtu_canvas_video_download import download_courses
from sjtu_history import history, save_history
from sjtu_style import COLORS, FONT_SMALL, heading, card, primary_button, secondary_button


def _format_time(ts):
    if ts > 1e15:
        ts = ts / 1_000_000_000
    elif ts > 1e12:
        ts = ts / 1_000
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


class HistoryFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg=COLORS["bg"])
        self.columnconfigure(0, weight=1)

        heading(self, "下载历史", "查看或续传以往的任务。")

        body = card(self)

        list_frame = tk.Frame(body, bg=COLORS["panel"])
        list_frame.pack(fill="both", expand=True)
        self.task_listbox = tk.Listbox(
            list_frame, bg=COLORS["panel"], fg=COLORS["text"], font=FONT_SMALL,
            relief="flat", borderwidth=0, highlightthickness=0,
            selectbackground=COLORS["primary"], selectforeground="white",
            activestyle="none",
        )
        self.task_listbox.pack(side="left", fill="both", expand=True, pady=(4, 0))
        scroll = ttk.Scrollbar(list_frame, command=self.task_listbox.yview)
        scroll.pack(side="right", fill="y")
        self.task_listbox.config(yscrollcommand=scroll.set)

        self._rebuild_list()

        btn_row = tk.Frame(body, bg=COLORS["panel"])
        btn_row.pack(fill="x", pady=(12, 0))
        secondary_button(btn_row, text="清空历史记录", command=self.clear_history).pack(side="left")
        primary_button(btn_row, text="重新下载选中项", command=self.initiate_download).pack(side="right")

    def _rebuild_list(self):
        self.task_listbox.delete(0, tk.END)
        self.task_names = []
        for i, task in enumerate(history):
            name = task["course_filenames"][0] if task["course_filenames"] else "未命名任务"
            self.task_names.append("%d. %s · %s" % (i, _format_time(task["time"]), name))
            self.task_listbox.insert(tk.END, self.task_names[-1])
        if self.task_names:
            self.task_listbox.selection_set(0)

    def get_task_index(self):
        sel = self.task_listbox.curselection()
        return sel[0] if sel else -1

    def initiate_download(self):
        task_index = self.get_task_index()
        if task_index == -1:
            tkinter.messagebox.showerror("错误", "请选择一个历史任务")
            return
        task = history[task_index]
        download_courses(task["course_links"], task["course_filenames"], task["video_dirname"], True)

    def clear_history(self):
        if tkinter.messagebox.askyesno("警告", "是否清空历史记录?"):
            history.clear()
            save_history()
            self._rebuild_list()
