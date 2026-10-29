"""
DEADLOCKNEXUS Theme & Design System
────────────────────────────────────
Centralized style, color tokens, typography, and TTK widget styling.
Aesthetic: Academic Operating Systems Analysis & Visualization Platform.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont


# ── Color Palette ─────────────────────────────────────────────────────────────
# Primary Backgrounds (Subtle dark slate rather than neon cyberpunk)
BG_BASE       = "#0A0E14"   # Primary application backdrop
BG_SIDEBAR    = "#0F141D"   # Navigation sidebar
BG_PANEL      = "#131924"   # Workbench container
BG_CARD       = "#171F2C"   # Elevated section container
BG_CARD_ALT   = "#1C2636"   # Hover/active elevation
BG_INPUT      = "#1C2432"   # Input fields and tables
BG_INPUT_HOVER= "#243042"

# Borders (Subtle, restrained)
BORDER_SUBTLE = "#1B2330"
BORDER_DEFAULT= "#232E3F"
BORDER_FOCUS  = "#38BDF8"
BORDER_HOVER  = "#334155"

# Primary Technical Accents
CYAN          = "#38BDF8"   # Sky blue / technical cyan
CYAN_DIM      = "#0284C7"
CYAN_BG       = "#0C2333"
PURPLE        = "#A78BFA"   # Muted purple
PURPLE_BG     = "#201736"

# Semantic Status Colors (Restrained and readable)
SUCCESS       = "#34D399"   # System safe / green
SUCCESS_BG    = "#0B261D"
SUCCESS_BORDER= "#164E3A"

WARNING       = "#FBBF24"   # Waiting / caution amber
WARNING_BG    = "#2B210B"
WARNING_BORDER= "#543F14"

DANGER        = "#F87171"   # Deadlock / danger red
DANGER_BG     = "#2E1316"
DANGER_BORDER = "#5C2128"

INFO          = "#38BDF8"
INFO_BG       = "#0C2333"

# Text Hierarchy
TEXT_PRIMARY  = "#F1F5F9"   # Crisp readable off-white
TEXT_SECONDARY= "#94A3B8"   # Slate secondary
TEXT_MUTED    = "#64748B"   # Low-contrast technical labels
TEXT_DARK     = "#0A0E14"


# ── Font Definitions ──────────────────────────────────────────────────────────
def get_fonts():
    """Returns standardized dictionary of application fonts with safe fallbacks."""
    available = set(tkfont.families()) if tk._default_root else set()
    
    if "Inter" in available:
        ui_family = "Inter"
    elif "Segoe UI" in available:
        ui_family = "Segoe UI"
    elif "Helvetica Neue" in available:
        ui_family = "Helvetica Neue"
    else:
        ui_family = "Arial"

    if "JetBrains Mono" in available:
        mono_family = "JetBrains Mono"
    elif "Consolas" in available:
        mono_family = "Consolas"
    elif "Fira Code" in available:
        mono_family = "Fira Code"
    elif "Courier New" in available:
        mono_family = "Courier New"
    else:
        mono_family = "Courier"

    return {
        "title": (ui_family, 14, "bold"),
        "subtitle": (ui_family, 10),
        "heading": (ui_family, 12, "bold"),
        "subheading": (ui_family, 10, "bold"),
        "body": (ui_family, 9),
        "body_bold": (ui_family, 9, "bold"),
        "caption": (ui_family, 8),
        "caption_bold": (ui_family, 8, "bold"),
        
        "mono_lg": (mono_family, 15, "bold"),
        "mono": (mono_family, 9),
        "mono_bold": (mono_family, 9, "bold"),
        "mono_sm": (mono_family, 8),
        "mono_sm_bold": (mono_family, 8, "bold"),
        "mono_badge": (mono_family, 7, "bold"),
    }


# ── TTK Style Configuration ───────────────────────────────────────────────────
def configure_app_styles(root: tk.Tk):
    """Configures TTK theme styles for the application."""
    style = ttk.Style(root)
    style.theme_use("clam")
    
    fonts = get_fonts()

    # Frames and Labels
    style.configure("TFrame", background=BG_PANEL)
    style.configure("Dark.TFrame", background=BG_BASE)
    style.configure("Card.TFrame", background=BG_CARD)
    style.configure("Sidebar.TFrame", background=BG_SIDEBAR)
    
    style.configure("TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=fonts["body"])
    style.configure("Muted.TLabel", background=BG_PANEL, foreground=TEXT_MUTED, font=fonts["caption"])
    style.configure("Heading.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=fonts["heading"])
    style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY, font=fonts["body"])
    style.configure("CardMuted.TLabel", background=BG_CARD, foreground=TEXT_MUTED, font=fonts["caption"])
    
    # Entry
    style.configure("TEntry",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    bordercolor=BORDER_DEFAULT,
                    lightcolor=BORDER_DEFAULT,
                    darkcolor=BORDER_DEFAULT,
                    insertcolor=CYAN,
                    padding=5)
    
    # Spinbox
    style.configure("TSpinbox",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    bordercolor=BORDER_DEFAULT,
                    lightcolor=BORDER_DEFAULT,
                    darkcolor=BORDER_DEFAULT,
                    arrowcolor=TEXT_SECONDARY,
                    insertcolor=CYAN,
                    padding=4)

    # Combobox
    style.configure("TCombobox",
                    fieldbackground=BG_INPUT,
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    bordercolor=BORDER_DEFAULT,
                    darkcolor=BORDER_DEFAULT,
                    lightcolor=BORDER_DEFAULT,
                    arrowcolor=CYAN,
                    padding=4)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG_INPUT), ("focus", BG_INPUT_HOVER)],
              foreground=[("readonly", TEXT_PRIMARY)])

    # Standard Neutral Button
    style.configure("TButton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    bordercolor=BORDER_DEFAULT,
                    darkcolor=BORDER_DEFAULT,
                    lightcolor=BORDER_DEFAULT,
                    relief="flat",
                    font=fonts["body"],
                    padding=(10, 5))
    style.map("TButton",
              background=[("pressed", BG_BASE), ("active", BG_CARD_ALT)],
              bordercolor=[("active", BORDER_HOVER)],
              foreground=[("active", TEXT_PRIMARY)])

    # Primary Action Button
    style.configure("Accent.TButton",
                    background=CYAN,
                    foreground=TEXT_DARK,
                    bordercolor=CYAN,
                    relief="flat",
                    font=fonts["body_bold"],
                    padding=(12, 6))
    style.map("Accent.TButton",
              background=[("pressed", CYAN_DIM), ("active", "#7DD3FC")],
              foreground=[("pressed", TEXT_DARK), ("active", TEXT_DARK)])

    # Danger Red Button
    style.configure("Danger.TButton",
                    background=DANGER,
                    foreground=TEXT_PRIMARY,
                    bordercolor=DANGER,
                    relief="flat",
                    font=fonts["body_bold"],
                    padding=(10, 5))
    style.map("Danger.TButton",
              background=[("pressed", "#DC2626"), ("active", "#EF4444")],
              foreground=[("pressed", TEXT_PRIMARY), ("active", TEXT_PRIMARY)])

    # Success Green Button
    style.configure("Success.TButton",
                    background=SUCCESS,
                    foreground=TEXT_DARK,
                    bordercolor=SUCCESS,
                    relief="flat",
                    font=fonts["body_bold"],
                    padding=(10, 5))
    style.map("Success.TButton",
              background=[("pressed", "#059669"), ("active", "#10B981")],
              foreground=[("pressed", TEXT_DARK), ("active", TEXT_DARK)])

    # Warning Button
    style.configure("Warning.TButton",
                    background=WARNING,
                    foreground=TEXT_DARK,
                    bordercolor=WARNING,
                    relief="flat",
                    font=fonts["body_bold"],
                    padding=(10, 5))
    style.map("Warning.TButton",
              background=[("pressed", "#D97706"), ("active", "#F59E0B")],
              foreground=[("pressed", TEXT_DARK), ("active", TEXT_DARK)])

    # Subtle / Ghost Button
    style.configure("Ghost.TButton",
                    background=BG_PANEL,
                    foreground=TEXT_SECONDARY,
                    bordercolor=BORDER_SUBTLE,
                    relief="flat",
                    font=fonts["body"],
                    padding=(8, 4))
    style.map("Ghost.TButton",
              background=[("active", BG_CARD)],
              foreground=[("active", TEXT_PRIMARY)],
              bordercolor=[("active", BORDER_DEFAULT)])

    # Checkbutton & Radiobutton
    style.configure("TCheckbutton",
                    background=BG_PANEL,
                    foreground=TEXT_PRIMARY,
                    font=fonts["body"],
                    indicatorcolor=BG_INPUT,
                    indicatorrelief="flat")
    style.map("TCheckbutton",
              indicatorcolor=[("selected", CYAN), ("active", BG_CARD_ALT)],
              foreground=[("active", TEXT_PRIMARY)])

    style.configure("TRadiobutton",
                    background=BG_PANEL,
                    foreground=TEXT_PRIMARY,
                    font=fonts["body"],
                    indicatorcolor=BG_INPUT)
    style.map("TRadiobutton",
              indicatorcolor=[("selected", CYAN), ("active", BG_CARD_ALT)],
              foreground=[("active", TEXT_PRIMARY)])

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=BG_CARD,
                    troughcolor=BG_BASE,
                    bordercolor=BG_BASE,
                    arrowcolor=TEXT_MUTED,
                    relief="flat")
    style.map("Vertical.TScrollbar",
              background=[("active", BG_CARD_ALT), ("pressed", CYAN_DIM)])

    # Scale / Slider
    style.configure("Horizontal.TScale",
                    background=BG_PANEL,
                    troughcolor=BG_INPUT,
                    bordercolor=BORDER_DEFAULT,
                    lightcolor=CYAN,
                    darkcolor=CYAN)

    # Treeview / Tables
    style.configure("Treeview",
                    background=BG_CARD,
                    fieldbackground=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    bordercolor=BORDER_DEFAULT,
                    font=fonts["body"],
                    rowheight=26)
    style.map("Treeview",
              background=[("selected", BG_INPUT_HOVER)],
              foreground=[("selected", CYAN)])
    
    style.configure("Treeview.Heading",
                    background=BG_PANEL,
                    foreground=TEXT_SECONDARY,
                    bordercolor=BORDER_DEFAULT,
                    font=fonts["caption_bold"],
                    padding=(6, 4))
    style.map("Treeview.Heading",
              background=[("active", BG_CARD)],
              foreground=[("active", TEXT_PRIMARY)])

    return fonts
