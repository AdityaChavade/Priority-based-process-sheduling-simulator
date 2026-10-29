"""
Modern Modal Dialogs
────────────────────
Styled custom confirmation and alert modals.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_CARD, BG_PANEL, BG_INPUT, BORDER_DEFAULT, BORDER_FOCUS,
    CYAN, DANGER, SUCCESS, WARNING, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)


class ConfirmDialog(tk.Toplevel):
    """
    Modern modal confirmation dialog with danger/warning/info theme.
    """

    def __init__(self, parent, title: str, message: str,
                 detail: str = "", confirm_text: str = "Confirm",
                 cancel_text: str = "Cancel", is_danger: bool = False):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.configure(bg=BG_BASE)
        self.resizable(False, False)
        
        self.result = False
        fonts = get_fonts()

        # Modal Container
        container = tk.Frame(
            self,
            bg=BG_CARD,
            highlightbackground=DANGER if is_danger else BORDER_FOCUS,
            highlightthickness=1,
            padx=24,
            pady=20
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header with icon
        header = tk.Frame(container, bg=BG_CARD)
        header.pack(fill="x", pady=(0, 10))

        icon_char = "⚠" if is_danger else "ℹ"
        icon_color = DANGER if is_danger else CYAN
        lbl_icon = tk.Label(
            header,
            text=icon_char,
            bg=BG_CARD,
            fg=icon_color,
            font=fonts["heading"]
        )
        lbl_icon.pack(side="left", padx=(0, 10))

        lbl_title = tk.Label(
            header,
            text=title,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=fonts["heading"]
        )
        lbl_title.pack(side="left")

        # Message
        lbl_msg = tk.Label(
            container,
            text=message,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=fonts["body_bold"],
            wraplength=380,
            justify="left"
        )
        lbl_msg.pack(anchor="w", pady=(0, 6))

        # Detail text
        if detail:
            lbl_detail = tk.Label(
                container,
                text=detail,
                bg=BG_CARD,
                fg=TEXT_SECONDARY,
                font=fonts["caption"],
                wraplength=380,
                justify="left"
            )
            lbl_detail.pack(anchor="w", pady=(0, 16))

        # Buttons row
        btn_row = tk.Frame(container, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        btn_cancel = ttk.Button(
            btn_row,
            text=cancel_text,
            style="Ghost.TButton",
            command=self._on_cancel
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_confirm = ttk.Button(
            btn_row,
            text=confirm_text,
            style="Danger.TButton" if is_danger else "Accent.TButton",
            command=self._on_confirm
        )
        btn_confirm.pack(side="right")

        # Key bindings
        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")

        self.wait_window(self)

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()
