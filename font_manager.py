import tkinter.font as tkfont
from tkinter import ttk

def configure():
    # family = "Segoe UI"
    family = "Helvetica"
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=15, family=family)
    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=12, family=family)
    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=12, family=family)

def apply_dark_theme(window):
    bg = "#1f2430"
    panel = "#2b3140"
    input_bg = "#31384a"
    text_fg = "#e7eaf0"
    accent = "#4f7cac"
    accent_hover = "#5f8fbe"
    window.configure(bg = bg)



    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background = bg)
    style.configure("Tlabelframe", background = bg, foreground = text_fg)
    style.configure("TLabelframe.label", background = bg, foreground = text_fg)
    style.configure("TLabel", background = bg, foreground = text_fg)
    style.configure("TButton", background = accent, foreground = "white", padding = 6)
    style.map("TButton", background = [("active", accent_hover)])
    style.configure("TEntry", fieldbackground = input_bg, foreground = text_fg)
    style.configure("TCombobox", fieldbackground = input_bg, foreground = text_fg)



