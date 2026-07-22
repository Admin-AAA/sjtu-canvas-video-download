"""统一视觉主题与可复用组件。"""
import tkinter as tk
import tkinter.ttk as ttk

COLORS = {
    "bg": "#F4F6FA",
    "panel": "#FFFFFF",
    "panel_alt": "#F0F3F9",
    "text": "#1A2030",
    "muted": "#707A8A",
    "faint": "#9AA3B2",
    "border": "#E4E8F0",
    "primary": "#3B6FF5",
    "primary_hover": "#2E5BE0",
    "primary_disabled": "#B9C6F7",
    "primary_soft": "#EAF0FE",
    "sidebar_bg": "#131A26",
    "sidebar_fg": "#AEB9CC",
    "sidebar_hover": "#1E2735",
    "success": "#16A34A",
    "warning": "#D97706",
    "danger": "#DC2626",
}

FONT_BASE = ("PingFang SC", 13)
FONT_TITLE = ("PingFang SC", 20, "bold")
FONT_HEAD = ("PingFang SC", 16, "bold")
FONT_SMALL = ("PingFang SC", 11)
FONT_BTN = ("PingFang SC", 13)
FONT_LABEL = ("PingFang SC", 12)


def apply_theme(root):
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", font=FONT_BASE, background=COLORS["bg"], foreground=COLORS["text"])

    style.configure(
        "TButton", padding=(14, 7), relief="flat", borderwidth=0,
        background=COLORS["panel"], foreground=COLORS["text"],
    )
    style.map(
        "TButton",
        background=[("active", COLORS["panel_alt"]), ("disabled", "#E9EDF3")],
        foreground=[("disabled", "#9AA3AF")],
    )

    style.configure(
        "Accent.TButton", padding=(16, 8), relief="flat", borderwidth=0,
        background=COLORS["primary"], foreground="white", font=FONT_BTN,
    )
    style.map(
        "Accent.TButton",
        background=[("active", COLORS["primary_hover"]), ("disabled", COLORS["primary_disabled"])],
    )

    style.configure(
        "TCombobox", padding=7, fieldbackground="white",
        background=COLORS["panel"], bordercolor=COLORS["border"], relief="solid",
    )
    style.configure("TCombobox", arrowsize=14)
    style.configure(
        "TEntry", padding=7, fieldbackground="white",
        bordercolor=COLORS["border"], relief="solid",
    )
    style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["text"], indicatordiameter=15)
    style.map("TCheckbutton", background=[("active", COLORS["panel_alt"])])
    style.configure("TRadiobutton", background=COLORS["panel"], foreground=COLORS["text"], indicatordiameter=15)
    style.map("TRadiobutton", background=[("active", COLORS["panel_alt"])])

    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(18, 9), background=COLORS["panel_alt"],
                    foreground=COLORS["muted"], borderwidth=0)
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["panel"])],
        foreground=[("selected", COLORS["text"])],
    )

    root.option_add("*TCombobox*Listbox.background", "white")
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["primary"])
    root.option_add("*TCombobox*Listbox.selectForeground", "white")


def heading(parent, text, subtitle=None):
    f = tk.Frame(parent, bg=COLORS["bg"])
    tk.Label(f, text=text, font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
    if subtitle:
        tk.Label(f, text=subtitle, font=FONT_SMALL, bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(4, 0))
    f.pack(anchor="w", fill="x", padx=28, pady=(22, 14))
    return f


def field_label(master, text):
    return tk.Label(master, text=text, bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_LABEL, anchor="w")


def card(parent, **kw):
    padx = kw.pop("padx", 28)
    pady = kw.pop("pady", 18)
    c = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1, **kw)
    c.pack(fill="x", padx=28, pady=(0, 14))
    inner = tk.Frame(c, bg=COLORS["panel"])
    inner.pack(fill="x", padx=padx, pady=pady)
    return inner


def primary_button(master, **kw):
    return ttk.Button(master, style="Accent.TButton", **kw)


def secondary_button(master, **kw):
    return ttk.Button(master, style="TButton", **kw)
