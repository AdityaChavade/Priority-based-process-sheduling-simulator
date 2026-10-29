"""
Reusable Modern UI Cards & Widgets
───────────────────────────────────
Clean, restrained layout containers, stat blocks, and status indicators.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_SUBTLE, BORDER_FOCUS,
    CYAN, CYAN_BG, PURPLE, PURPLE_BG, SUCCESS, SUCCESS_BG,
    WARNING, WARNING_BG, DANGER, DANGER_BG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)


class SectionCard(tk.Frame):
    """
    Structured section container with title, optional subtitle,
    and action controls. Clean technical layout without visual clutter.
    """

    def __init__(self, parent, title: str = "", subtitle: str = "", badge_text: str = "",
                 badge_color: str = CYAN, action_btn_text: str = "", on_action=None, **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_DEFAULT,
            highlightthickness=1,
            padx=kwargs.pop("padx", 12),
            pady=kwargs.pop("pady", 10),
            **kwargs
        )
        self.fonts = get_fonts()

        if title or action_btn_text or badge_text:
            header_frame = tk.Frame(self, bg=BG_CARD)
            header_frame.pack(fill="x", pady=(0, 6))

            title_container = tk.Frame(header_frame, bg=BG_CARD)
            title_container.pack(side="left", fill="y")

            # Clean Title Case (avoiding all-caps shouting)
            lbl_title = tk.Label(
                title_container,
                text=title,
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                font=self.fonts["subheading"]
            )
            lbl_title.pack(anchor="w")

            if subtitle:
                lbl_sub = tk.Label(
                    title_container,
                    text=subtitle,
                    bg=BG_CARD,
                    fg=TEXT_MUTED,
                    font=self.fonts["caption"]
                )
                lbl_sub.pack(anchor="w")

            if action_btn_text and on_action:
                btn_action = ttk.Button(
                    header_frame,
                    text=action_btn_text,
                    style="Ghost.TButton",
                    command=on_action
                )
                btn_action.pack(side="right", padx=(6, 0))

            if badge_text:
                self.badge = StatusBadge(
                    header_frame,
                    text=badge_text,
                    color=badge_color
                )
                self.badge.pack(side="right")
            else:
                self.badge = None


class StatCard(tk.Frame):
    """
    Compact technical metric card displaying a clean title, primary value,
    and factual descriptor.
    """

    def __init__(self, parent, title: str, initial_value: str = "0",
                 icon: str = "", accent_color: str = CYAN, subtext: str = "", **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_DEFAULT,
            highlightthickness=1,
            padx=12,
            pady=8,
            **kwargs
        )
        self.fonts = get_fonts()
        self.accent_color = accent_color

        top_row = tk.Frame(self, bg=BG_CARD)
        top_row.pack(fill="x")

        lbl_title = tk.Label(
            top_row,
            text=title,
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption_bold"]
        )
        lbl_title.pack(side="left")

        if icon:
            lbl_icon = tk.Label(
                top_row,
                text=icon,
                bg=BG_CARD,
                fg=TEXT_MUTED,
                font=self.fonts["caption"]
            )
            lbl_icon.pack(side="right")

        self.lbl_value = tk.Label(
            self,
            text=initial_value,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono_lg"]
        )
        self.lbl_value.pack(anchor="w", pady=(2, 2))

        self.lbl_subtext = tk.Label(
            self,
            text=subtext,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=self.fonts["caption"]
        )
        self.lbl_subtext.pack(anchor="w")

    def update_value(self, value: str, subtext: str = None, accent_color: str = None):
        self.lbl_value.configure(text=str(value))
        if subtext is not None:
            self.lbl_subtext.configure(text=subtext)
        if accent_color is not None:
            self.lbl_value.configure(fg=accent_color)


class StatusBadge(tk.Frame):
    """Functional status label for system states."""

    def __init__(self, parent, text: str = "SAFE", color: str = SUCCESS, **kwargs):
        bg_tint = {
            SUCCESS: SUCCESS_BG,
            WARNING: WARNING_BG,
            DANGER: DANGER_BG,
            CYAN: CYAN_BG,
            PURPLE: PURPLE_BG,
        }.get(color, BG_INPUT)

        super().__init__(
            parent,
            bg=bg_tint,
            highlightbackground=color,
            highlightthickness=1,
            padx=7,
            pady=1,
            **kwargs
        )
        self.fonts = get_fonts()
        self.color = color

        self.lbl = tk.Label(
            self,
            text=text,
            bg=bg_tint,
            fg=color,
            font=self.fonts["mono_badge"]
        )
        self.lbl.pack()

    def set_status(self, text: str, color: str):
        self.color = color
        bg_tint = {
            SUCCESS: SUCCESS_BG,
            WARNING: WARNING_BG,
            DANGER: DANGER_BG,
            CYAN: CYAN_BG,
            PURPLE: PURPLE_BG,
        }.get(color, BG_INPUT)
        
        self.configure(bg=bg_tint, highlightbackground=color)
        self.lbl.configure(text=text, bg=bg_tint, fg=color)


class UtilizationBar(tk.Canvas):
    """Proportional indicator for resource allocation capacity."""

    def __init__(self, parent, width: int = 120, height: int = 8, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=BG_BASE,
            highlightthickness=1,
            highlightbackground=BORDER_DEFAULT,
            **kwargs
        )
        self.bar_width = width
        self.bar_height = height

    def set_fraction(self, fraction: float, color: str = CYAN):
        self.delete("all")
        frac = max(0.0, min(1.0, fraction))
        w = int(self.winfo_width() or self.bar_width)
        h = int(self.winfo_height() or self.bar_height)
        
        fill_w = int(w * frac)
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, h, fill=color, outline="")
