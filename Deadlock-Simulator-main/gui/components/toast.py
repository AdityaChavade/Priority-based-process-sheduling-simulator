"""
Toast Notification System
─────────────────────────
Modern floating toast notifications that animate into view and auto-dismiss.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_CARD, BG_INPUT, BORDER_DEFAULT, TEXT_PRIMARY, TEXT_SECONDARY,
    SUCCESS, WARNING, DANGER, CYAN, INFO, get_fonts
)


class ToastNotification:
    """Manages displaying clean, modern floating toast notifications on the app."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._active_toasts = []

    def show(self, message: str, level: str = "info", duration_ms: int = 3500):
        """
        Show a toast notification.
        level: 'info' | 'success' | 'warn' | 'error' | 'danger'
        """
        fonts = get_fonts()
        
        # Color mapping
        level_map = {
            "success": (SUCCESS, "✓"),
            "warn": (WARNING, "⚠"),
            "warning": (WARNING, "⚠"),
            "error": (DANGER, "✕"),
            "danger": (DANGER, "✕"),
            "info": (CYAN, "ℹ"),
        }
        accent_color, symbol = level_map.get(level.lower(), (CYAN, "ℹ"))

        # Toast window / frame overlay
        toast = tk.Frame(
            self.root,
            bg=BG_CARD,
            highlightbackground=accent_color,
            highlightthickness=1,
            padx=12,
            pady=8
        )

        # Icon / Symbol
        lbl_icon = tk.Label(
            toast,
            text=symbol,
            bg=BG_CARD,
            fg=accent_color,
            font=fonts["body_bold"]
        )
        lbl_icon.pack(side="left", padx=(0, 8))

        # Message Text
        lbl_text = tk.Label(
            toast,
            text=message,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=fonts["body"],
            wraplength=340,
            justify="left"
        )
        lbl_text.pack(side="left", fill="x", expand=True)

        # Close button
        btn_close = tk.Label(
            toast,
            text="✕",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=fonts["caption"],
            cursor="hand2"
        )
        btn_close.pack(side="right", padx=(8, 0))

        def close_toast():
            if toast in self._active_toasts:
                self._active_toasts.remove(toast)
            toast.destroy()
            self._reposition()

        btn_close.bind("<Button-1>", lambda e: close_toast())
        toast.bind("<Button-1>", lambda e: close_toast())
        lbl_text.bind("<Button-1>", lambda e: close_toast())

        self._active_toasts.append(toast)
        self._reposition()

        # Schedule auto close
        self.root.after(duration_ms, close_toast)

    def _reposition(self):
        """Positions active toasts at the top-right corner of the application."""
        y_offset = 64
        right_margin = 24
        
        for toast in self._active_toasts:
            toast.update_idletasks()
            w = toast.winfo_reqwidth()
            h = toast.winfo_reqheight()
            
            app_w = self.root.winfo_width()
            x = max(20, app_w - w - right_margin)
            
            toast.place(x=x, y=y_offset, width=w, height=h)
            toast.lift()
            y_offset += h + 8
