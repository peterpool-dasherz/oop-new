import tkinter.font as tkfont
import tkinter as tk
from tkinter import ttk
import platform
import subprocess
from pathlib import Path

THEME_MODE = "System"

def configure():
    # family = "Segoe UI"
    family = "Helvetica"
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=15, family=family)
    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=12, family=family)
    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=12, family=family)

def set_theme_mode(mode):
    global THEME_MODE
    if mode not in{"Light", "Dark", "System"}:
        raise ValueError('Theme mode must be Light, Dark or follows the system setting')
    THEME_MODE = mode

def get_theme_mode():
    return THEME_MODE
                 

def _is_dark_mode():
    system = platform.system()
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                check=False,
            )
            return "Dark" in result.stdout
        except Exception:
            return False

    elif system == "Windows":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False
    else:
        return False

def _resolve_theme(mode = None):
    if mode is None:
        mode = THEME_MODE
    if mode == "System":
        return "Dark" if _is_dark_mode() else "Light"
    return mode

def get_theme_colors(mode = None):
    actual = _resolve_theme(mode)
    if actual == "Dark":
        return { "mode": actual, "bg": "#1f2430", "panel": "#2b3140", "input_bg": "#31384a", "text_fg": "#e7eaf0", "accent": "#4f7cac", "accent_hover": "#5f8fbe"}
    return { "mode": actual, "bg": "#f4f4f4", "panel": "#ffffff", "input_bg": "#ffffff", "text_fg": "#1f2430", "accent": "#3d6ae8", "accent_hover": "#5b84b1"}

def apply_device_theme(window):
    if _is_dark_mode():
        apply_theme(window, "Dark")
    else:
        apply_theme(window, "Light")

def apply_theme(window, mode):
    if mode == "Light":
        bg = "#f4f4f4"
        input_bg = "#ffffff"
        text_fg = "#1f2430"
        accent = "#3d6ae8"
        accent_hover = "#5b84b1"
    else: 
        bg = "#1f2430"
        input_bg = "#31384a"
        text_fg = "#e7eaf0"
        accent = "#4f7cac"
        accent_hover = "#5f8fbe"
    
    window.configure(bg = bg)
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background= bg)
    style.configure("TLabelframe", background = bg, foreground = text_fg)
    style.configure("TLabelframe.Label", background = bg, foreground = text_fg)
    style.configure("TLabel", background = bg, foreground = text_fg)
    style.configure("TButton", background = accent, foreground = text_fg, padding=6)
    style.map("TButton", background=[("active", accent_hover)])
    style.configure("TEntry", fieldbackground = input_bg, foreground = text_fg)
    style.configure("TCombobox", fieldbackground = input_bg, foreground = text_fg)

    _apply_widget_tree(window, {"bg": bg, "input_bg": input_bg, "text_fg": text_fg, "accent_hover": accent_hover})


def _apply_widget_tree(widget, colors):
    try:
        if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame, tk.LabelFrame)):
            widget.configure(bg = colors["bg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg = colors["bg"], fg = colors["text_fg"])
        elif isinstance(widget, tk.Text):
            widget.configure(bg = colors["input_bg"], fg = colors["text_bg"], insertbackground = colors["text_fg"], selectbackground = colors["accent_hover"])
    except tk.TclError:
        pass

    for child in widget.winfo_children():
        _apply_widget_tree(child, colors)





def save_theme_mode(settings_path, mode):
    path = Path(settings_path)
    with path.open("w", encoding = "utf-8") as file:
        file.write(mode)

def load_theme_mode(settings_path):
    path = Path(settings_path)
    if not path.exists():
        return "System"
    try:
        mode = path.read_text(encoding = "utf-8").strip().title()
        if mode in {"Light", "Dark", "System"}:
            return mode
    except OSError:
        pass
    return "System"


