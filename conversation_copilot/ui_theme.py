"""Playful, high-legibility Tk theme shared by every product surface."""
from __future__ import annotations

import sys
import tkinter as tk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageTk


THEMES = {
    "light": {
        "page": "#FFF7EC", "surface": "#FFFFFF", "sunken": "#FBFCFF",
        "muted": "#F1F5FF", "ink": "#16214A", "ink_muted": "#4C5E8C",
        "line": "#DCE4F2", "outline": "#16214A", "shadow": "#E3D3BC",
        "accent": "#2B5BE0", "accent_soft": "#EAF1FF", "on_accent": "#FFFFFF",
        "success": "#0E9464", "success_soft": "#E4F8EE", "success_ink": "#0A5E3E",
        "warning": "#F5B62B", "warning_soft": "#FFF0CC",
        "danger": "#E8462F", "danger_soft": "#FFECEA", "danger_ink": "#B3382B",
        "meter_on": "#17C08A", "meter_off": "#D9E3F5",
        "tone": "#FFF0CC", "social": "#F0E9FF", "replies": "#E7F0FF",
        "memory": "#E9F9F1", "follow_up": "#FFE9E7",
    },
    "dark": {
        "page": "#0E1119", "surface": "#191E2E", "sunken": "#1B2133",
        "muted": "#1F2740", "ink": "#E9EDF8", "ink_muted": "#A9B5D6",
        "line": "#2F3852", "outline": "#3C4970", "shadow": "#05070E",
        "accent": "#3B6BF0", "accent_soft": "#1C2A4E", "on_accent": "#FFFFFF",
        "success": "#0B7A52", "success_soft": "#123326", "success_ink": "#86E3BA",
        "warning": "#F0B429", "warning_soft": "#3A2E12",
        "danger": "#C2331F", "danger_soft": "#3A1E1A", "danger_ink": "#FFA394",
        "meter_on": "#1FCF96", "meter_off": "#2E3650",
        "tone": "#3A2E12", "social": "#2A2447", "replies": "#1C2A4E",
        "memory": "#123326", "follow_up": "#3A1E1A",
    },
}

DISPLAY_FONT = "Trebuchet MS"
BODY_FONT = "Segoe UI Semibold"


class RoundedButton(tk.Button):
    """Accessible Tk button with a theme-colored rounded background."""

    def __init__(self, master=None, **kwargs):
        kwargs.setdefault("compound", "center")
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("padx", 10)
        kwargs.setdefault("pady", 6)
        super().__init__(master, **kwargs)
        self._cc_fill = self.cget("background")
        self._cc_outline = self._cc_fill
        self._cc_parent_bg = self._cc_fill
        self._cc_disabled_fill = self._cc_fill
        self._cc_focus_outline = self._cc_outline
        self._cc_image = None
        self._cc_image_key = None
        self._cc_palette_ready = False
        self._cc_focused = False
        self.bind("<Configure>", self._redraw, add="+")
        self.bind("<FocusIn>", self._set_focus, add="+")
        self.bind("<FocusOut>", self._set_focus, add="+")

    def configure(self, cnf=None, **kwargs):
        result = tk.Button.configure(self, cnf, **kwargs)
        if getattr(self, "_cc_palette_ready", False) and ({"text", "font", "state"} & set(kwargs)):
            self._cc_image_key = None
            self.after_idle(self._redraw)
        return result

    config = configure

    def set_palette(
        self, fill: str, foreground: str, outline: str, parent_bg: str,
        *, disabled_fill: str, focus_outline: str,
    ) -> None:
        self._cc_fill = fill
        self._cc_outline = outline
        self._cc_parent_bg = parent_bg
        self._cc_disabled_fill = disabled_fill
        self._cc_focus_outline = focus_outline
        self._cc_palette_ready = True
        self._cc_image_key = None
        tk.Button.configure(
            self,
            background=parent_bg,
            foreground=foreground,
            activebackground=parent_bg,
            activeforeground=foreground,
            disabledforeground=outline,
        )
        self.after_idle(self._redraw)

    def _set_focus(self, event) -> None:
        self._cc_focused = event.type == tk.EventType.FocusIn
        self._cc_image_key = None
        self._redraw()

    def _redraw(self, _event=None) -> None:
        try:
            if not self._cc_palette_ready or not self.winfo_exists():
                return
            width, height = self.winfo_width(), self.winfo_height()
            font = tkfont.Font(font=self.cget("font"))
            width = max(width, font.measure(self.cget("text")) + 24)
            height = max(height, font.metrics("linespace") + 14)
            disabled = self.cget("state") == "disabled"
        except tk.TclError:
            return
        fill = self._cc_disabled_fill if disabled else self._cc_fill
        outline = self._cc_focus_outline if self._cc_focused else self._cc_outline
        key = (width, height, fill, outline, self._cc_parent_bg, self._cc_focused, disabled)
        if width < 4 or height < 4 or key == self._cc_image_key:
            return
        image = Image.new("RGB", (width, height), self._cc_parent_bg)
        ImageDraw.Draw(image).rounded_rectangle(
            (1, 1, width - 2, height - 2),
            radius=min(12, height // 2),
            fill=fill,
            outline=outline,
            width=3 if self._cc_focused else 2,
        )
        self._cc_image = ImageTk.PhotoImage(image, master=self)
        self._cc_image_key = key
        tk.Button.configure(self, image=self._cc_image, compound="center", padx=0, pady=0)


def system_theme() -> str:
    if sys.platform != "win32":
        return "light"
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            return "light" if winreg.QueryValueEx(key, "AppsUseLightTheme")[0] else "dark"
    except OSError:
        return "light"


def configure_ttk(style, colors: dict[str, str], *, font_size: int = 10) -> None:
    style.theme_use("clam")
    style.configure("TFrame", background=colors["page"])
    style.configure("TLabel", background=colors["page"], foreground=colors["ink"], font=(BODY_FONT, font_size))
    style.configure(
        "TButton", background=colors["surface"], foreground=colors["ink"],
        bordercolor=colors["outline"], lightcolor=colors["surface"], darkcolor=colors["surface"],
        font=(BODY_FONT, font_size, "bold"), padding=(10, 7), relief="flat",
    )
    style.map("TButton", background=[("active", colors["accent_soft"])])
    style.configure(
        "Primary.TButton", background=colors["accent"], foreground=colors["on_accent"],
        bordercolor=colors["outline"], font=(DISPLAY_FONT, font_size + 2, "bold"), padding=(13, 8),
    )
    style.map("Primary.TButton", background=[("active", colors["accent"])])
    style.configure("Quiet.TButton", background=colors["muted"], foreground=colors["ink"], padding=(9, 6))
    style.configure(
        "TCombobox", fieldbackground=colors["muted"], background=colors["muted"],
        foreground=colors["ink"], arrowcolor=colors["ink"], bordercolor=colors["line"],
        lightcolor=colors["line"], darkcolor=colors["line"], padding=6,
    )
    style.map("TCombobox", fieldbackground=[("readonly", colors["muted"])], foreground=[("readonly", colors["ink"])])
    style.configure("Vertical.TScrollbar", background=colors["muted"], troughcolor=colors["surface"], arrowcolor=colors["ink"])


def apply_theme(widget, colors: dict[str, str], *, font_size: int = 10) -> None:
    """Apply tokens recursively; explicit ``_cc_role`` values retain semantic color."""
    import tkinter as tk
    from tkinter import ttk

    role = getattr(widget, "_cc_role", "")
    parent_bg = colors["page"]
    try:
        parent = widget.nametowidget(widget.winfo_parent()) if widget.winfo_parent() else None
        if parent is not None and "background" in parent.configure():
            parent_bg = parent.cget("background")
    except (KeyError, tk.TclError):
        pass

    try:
        if widget.winfo_toplevel() == widget:
            widget.configure(background=colors["page"])
        elif isinstance(widget, tk.LabelFrame):
            background = colors.get(role, colors["surface"]) if role in {"tone", "social", "replies", "memory", "follow_up"} else colors.get(f"{role}_soft", colors["surface"])
            widget.configure(
                background=background, foreground=colors["ink"],
                font=(DISPLAY_FONT, font_size + 1, "bold"), bd=2, relief="solid",
                highlightthickness=0,
            )
        elif isinstance(widget, (tk.Frame, tk.Canvas)):
            if role in {"tone", "social", "replies", "memory", "follow_up"}:
                background = colors[role]
            else:
                background = colors["surface"] if getattr(widget, "_cc_surface", False) else parent_bg
            widget.configure(background=background, highlightbackground=colors["line"])
        elif isinstance(widget, tk.Label):
            background = parent_bg
            foreground = colors["ink"]
            if role in {"success", "warning", "danger", "accent"}:
                background = colors[f"{role}_soft"]
                foreground = colors.get(f"{role}_ink", colors["ink"])
            widget.configure(background=background, foreground=foreground, font=(BODY_FONT, font_size))
        elif isinstance(widget, tk.Button):
            background, foreground = colors["surface"], colors["ink"]
            if role == "primary":
                background, foreground = colors["accent"], colors["on_accent"]
            elif role == "success":
                background, foreground = colors["success"], "#FFFFFF"
            elif role == "danger":
                background, foreground = colors["danger"], "#FFFFFF"
            elif role == "warning":
                background, foreground = colors["warning_soft"], colors["ink"]
            elif role in {"tone", "social", "replies", "memory", "follow_up"}:
                background = colors[role]
            if isinstance(widget, RoundedButton):
                widget.configure(font=(BODY_FONT, font_size, "bold"), cursor="hand2")
                widget.set_palette(
                    background, foreground, colors["outline"], parent_bg,
                    disabled_fill=colors["muted"], focus_outline=colors["accent"],
                )
            else:
                widget.configure(
                    background=background, foreground=foreground, activebackground=background,
                    activeforeground=foreground, font=(BODY_FONT, font_size, "bold"),
                    relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                    highlightthickness=2, highlightbackground=colors["outline"],
                    highlightcolor=colors["accent"],
                )
        elif isinstance(widget, (tk.Entry, tk.Text)):
            widget.configure(
                background=colors["muted"], foreground=colors["ink"],
                insertbackground=colors["ink"], selectbackground=colors["accent"],
                selectforeground=colors["on_accent"], relief="flat", bd=0,
                highlightthickness=2, highlightbackground=colors["line"],
                highlightcolor=colors["accent"], font=(BODY_FONT, font_size),
            )
        elif isinstance(widget, tk.Listbox):
            widget.configure(
                background=colors["muted"], foreground=colors["ink"],
                selectbackground=colors["accent"], selectforeground=colors["on_accent"],
                relief="flat", bd=0, highlightthickness=2,
                highlightbackground=colors["line"], highlightcolor=colors["accent"],
                font=(BODY_FONT, font_size),
            )
        elif isinstance(widget, tk.Scale):
            widget.configure(
                background=parent_bg, foreground=colors["ink"], activebackground=colors["accent"],
                troughcolor=colors["line"], highlightthickness=0, font=(BODY_FONT, font_size),
            )
        elif isinstance(widget, (tk.Checkbutton, tk.Radiobutton)):
            widget.configure(
                background=parent_bg, foreground=colors["ink"], activebackground=parent_bg,
                activeforeground=colors["ink"], selectcolor=colors["accent_soft"],
                font=(BODY_FONT, font_size), highlightthickness=1,
                highlightcolor=colors["accent"],
            )
        elif isinstance(widget, ttk.Widget):
            pass
    except tk.TclError:
        pass

    for child in widget.winfo_children():
        apply_theme(child, colors, font_size=font_size)


def role(widget, name: str):
    widget._cc_role = name
    return widget


def surface(widget):
    widget._cc_surface = True
    return widget
