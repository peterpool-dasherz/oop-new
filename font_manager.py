import tkinter.font as tkfont  # access Tkinter's named fonts
import tkinter as tk  # access Tkinter widget classes for theme updates
from tkinter import ttk  # access ttk styling for frames, labels, and buttons
import platform  # detect the current operating system
import subprocess  # run a system command to detect macOS dark mode
from pathlib import Path  # handle settings file paths safely

THEME_MODE = "System"  # store the currently selected theme mode


def configure():  # configure the default Tkinter fonts used by the app
    # family = "Segoe UI"  # optional alternative font family
    family = "Helvetica"  # use Helvetica as the main interface font
    default_font = tkfont.nametofont("TkDefaultFont")  # get the default Tk font
    default_font.configure(size=15, family=family)  # make normal UI text larger
    text_font = tkfont.nametofont("TkTextFont")  # get the font used by text widgets
    text_font.configure(size=12, family=family)  # set text widget font size and family
    fixed_font = tkfont.nametofont("TkFixedFont")  # get the monospaced Tk font
    fixed_font.configure(size=12, family=family)  # set the fixed font size and family

def set_theme_mode(mode):
    global THEME_MODE  # update the module-level theme setting
    if mode not in {"Light", "Dark", "System"}:  # reject invalid theme names
        raise ValueError("Theme mode must be Light, Dark or follows the system setting")  # tell the caller the value is invalid
    THEME_MODE = mode  # save the selected theme mode


def get_theme_mode():  # return the current saved theme mode
    return THEME_MODE  # provide the global theme value


def _is_dark_mode():  # detect whether the operating system is using dark mode
    system = platform.system()  # read the current operating system name
    if system == "Darwin":  # macOS uses the defaults command for appearance settings
        try:
            result = subprocess.run(  # run the macOS appearance check command
                ["defaults", "read", "-g", "AppleInterfaceStyle"],  # query the global interface style
                capture_output=True,  # capture command output for inspection
                text=True,  # return output as text instead of bytes
                check=False,  # do not raise an exception if the command fails
            )
            return "Dark" in result.stdout  # return True when dark mode is detected
        except Exception:
            return False  # fall back to light mode if the check fails

    elif system == "Windows":  # Windows stores theme preferences in the registry
        try:
            import winreg  # import the Windows registry module only when needed

            key = winreg.OpenKey(  # open the registry key that stores theme settings
                winreg.HKEY_CURRENT_USER,  # use the current user's registry branch
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",  # path to the Windows theme setting
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")  # read whether apps should use light mode
            return value == 0  # 0 means dark mode, 1 means light mode
        except Exception:
            return False  # fall back to light mode if the registry lookup fails
    else:
        return False  # other platforms default to light mode


def _resolve_theme(mode = None):  # convert "System" into an actual theme choice
    if mode is None:  # if no mode was passed in
        mode = THEME_MODE  # use the current global theme mode
    if mode == "System":  # if the user selected system theme
        return "Dark" if _is_dark_mode() else "Light"  # resolve it to dark or light
    return mode  # otherwise return the explicit theme


def get_theme_colors(mode = None):  # return the color palette for the resolved theme
    actual = _resolve_theme(mode)  # resolve the theme mode first
    if actual == "Dark":  # return dark-mode colors when needed
        return {"mode": actual, "bg": "#1f2430", "panel": "#2b3140", "input_bg": "#31384a", "text_fg": "#e7eaf0", "accent": "#4f7cac", "accent_hover": "#5f8fbe"}  # dark palette
    return {"mode": actual, "bg": "#f4f4f4", "panel": "#ffffff", "input_bg": "#ffffff", "text_fg": "#1f2430", "accent": "#3d6ae8", "accent_hover": "#5b84b1"}  # light palette


def apply_device_theme(window):  # apply the system theme to a window
    if _is_dark_mode():  # check whether the operating system is in dark mode
        apply_theme(window, "Dark")  # apply the dark palette
    else:
        apply_theme(window, "Light")  # apply the light palette


def apply_theme(window, mode):  # apply a light or dark theme to the window
    if mode == "Light":  # use the light color set
        bg = "#f4f4f4"  # background color for the main window
        input_bg = "#ffffff"  # background color for input widgets
        text_fg = "#1f2430"  # text color for labels and text widgets
        accent = "#3d6ae8"  # main button color
        accent_hover = "#5b84b1"  # button hover color
    else: 
        bg = "#1f2430"  # dark background color
        input_bg = "#31384a"  # dark input background color
        text_fg = "#e7eaf0"  # light text color
        accent = "#4f7cac"  # dark-mode button color
        accent_hover = "#5f8fbe"  # dark-mode hover color
    
    window.configure(bg = bg)  # apply the main window background color
    style = ttk.Style()  # create the ttk style object
    style.theme_use("clam")  # use the clam theme so colors can be customized

    style.configure("TFrame", background = bg)  # style normal frames
    style.configure("TLabelframe", background = bg, foreground = text_fg)  # style labelled frames
    style.configure("TLabelframe.Label", background = bg, foreground = text_fg)  # style labelled frame titles
    style.configure("TLabel", background = bg, foreground = text_fg)  # style text labels
    style.configure("TButton", background = accent, foreground = text_fg, padding = 6)  # style buttons
    style.map("TButton", background = [("active", accent_hover)])  # change button color when hovered
    style.configure("TEntry", fieldbackground = input_bg, foreground = text_fg)  # style entry widgets
    style.configure("TCombobox", fieldbackground = input_bg, foreground = text_fg)  # style combobox widgets

    _apply_widget_tree(window, {"bg": bg, "input_bg": input_bg, "text_fg": text_fg, "accent_hover": accent_hover})  # apply matching colors to Tk widgets


def _apply_widget_tree(widget, colors):  # recursively style all child widgets
    try:
        if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame, tk.LabelFrame)):  # style container widgets
            widget.configure(bg = colors["bg"])  # apply the background color
        elif isinstance(widget, tk.Label):  # style labels
            widget.configure(bg = colors["bg"], fg = colors["text_fg"])  # apply matching label colors
        elif isinstance(widget, tk.Text):  # style text widgets
            widget.configure(bg = colors["input_bg"], fg = colors["text_fg"], insertbackground = colors["text_fg"], selectbackground = colors["accent_hover"])  # apply text colors and selection highlight
    except tk.TclError:
        pass  # ignore widgets that do not support these options

    # visit every child widget so the whole interface is updated
    for child in widget.winfo_children():
        _apply_widget_tree(child, colors)  # apply the same colors recursively


def save_theme_mode(settings_path, mode):
    path = Path(settings_path)  # convert the settings path into a Path object
    with path.open("w", encoding = "utf-8") as file:  # open the settings file for writing
        file.write(mode)  # save the chosen theme mode


def load_theme_mode(settings_path):  # read the saved theme mode from disk
    path = Path(settings_path)  # convert the settings path into a Path object
    if not path.exists():  # if the file has not been created yet
        return "System"  # default to the system theme
    try:
        mode = path.read_text(encoding = "utf-8").strip().title()  # read and normalize the saved mode
        if mode in {"Light", "Dark", "System"}:  # only accept valid mode names
            return mode  # return the stored theme
    except OSError:
        pass  # ignore file read errors and fall back to default
    return "System"  # use the default if the file is missing or invalid
