# SJTU Canvas 视频下载器 · 易用性全面优化

针对四个维度逐一排查并完成优化。项目为 **Tkinter 桌面 GUI**，故将"页面/导航/交互"原则落到桌面端：单窗口 + 侧边栏导航、统一主题、后台线程。

## 1. 页面美观度
- 新增 `sjtu_style.py` 统一设计语言：浅灰背景 + 白色卡片 + 蓝色主行动色 + 深色侧边栏，规范字体（PingFang SC）、间距、描边。
- 提供 `heading / card / accent_button / default_button` 等复用组件，所有界面风格一致。
- 主按钮（蓝底白字 Accent 样式）与次按钮区分清晰，建立视觉层次。

## 2. 交互流畅度
- **课程列表加载改为后台线程**：登录后不再冻结界面，底部状态栏实时显示"正在加载课程列表…"。
- **下载与取视频地址改为后台线程**：原来 `download_courses` 在 macOS 上是 `subprocess.run` 阻塞调用（aria2 跑几分钟 GUI 直接卡死），现已移出主线程；`download_courses` 新增 `silent` 参数，后台调用不再弹窗，进度统一由状态栏提示。
- 按钮在加载/下载期间自动置灰，避免重复触发。

## 3. 页面数量管理（导航结构）
- 原结构：**主窗口 + 最多 7 个浮动子窗口**（登录、扫码、单下、批量、下载器、历史、预览）互相堆叠、无层级。
- 新结构：**单窗口 + 侧边栏**，仅 3 个视图——`登录 / 下载 / 历史`，层级清晰、路径短。
  - 登录页用 `ttk.Notebook` 在「账号密码 / 扫码登录」间切换，不再开两个窗口。
  - 下载把"选科目 → 选讲 → 填路径 → 下载"合并到**同一界面**，省去两次弹窗跳转。
  - 预览改为相对主窗口的模态对话框（`transient` + `grab_set`）。
- `sjtu_canvas_video_picker_frame.py` 与 `sjtu_canvas_video_downloader_frame.py` 已被合并取代（暂保留，未删除）。

## 4. 整体易用性
- 侧边栏导航直观，当前视图高亮。
- 下载流程步骤从"多窗口跳转"缩短为"单屏操作"；支持单个/批量切换、预览、按课程ID高级加载、导入/导出下载地址。
- 统一交互规范：主次按钮、卡片分区、状态栏反馈、友好报错（网络失败时弹提示而非崩溃）。
- 保留并整合了原有全部功能（登录、扫码、导入/导出、历史续传、课程ID），无功能丢失。

## 验证
- 全部文件 `py_compile` 通过；8 个模块导入冒烟全 OK。
- 链接构建 / 索引解析纯逻辑 headless 测试通过。
- **启动崩溃修复 + 验收（headless 实跑）**：
  - 修复 ① `AttributeError: 'App' object has no attribute '_nav_buttons'`（`App.__init__` 在侧边栏构建前漏初始化状态字典）。
  - 验收测试又揪出并修复 ② `AttributeError: 'DownloadView' object has no attribute 'lower_combobox'`（`_build_course_card` 的 prefill 在 lower/upper 下拉框创建前就调用，登录后有课程必崩）。
  - 验收方法：stub 掉联网的登录框，用 `.venv` 真实构建 `App(root)` 并依次 `navigate(login/download/history)`，覆盖"未登录提示"与"已登录有课程"两条路径，强制布局。6 步全 ok → `ACCEPTANCE_OK`，确认可启动、三视图切换无报错。

## 关键文件
- 新增：`sjtu_style.py`、`sjtu_download_view.py`
- 重写：`sjtu_canvas_video_main_frame.py`、`main.py`
- 改动：`sjtu_login_frame.py`、`sjtu_qr_code_login_frame.py`、`sjtu_canvas_video_download.py`、`sjtu_history_frame.py`
