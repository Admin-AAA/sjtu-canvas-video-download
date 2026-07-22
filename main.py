import monkey_patch
import tkinter as tk
from sjtu_canvas_video_main_frame import App
import logging

# 关闭 urllib3 连接池 DEBUG 刷屏，仅保留 WARNING 以上，便于查看真实日志
logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

root = tk.Tk()
App(root)
root.mainloop()
