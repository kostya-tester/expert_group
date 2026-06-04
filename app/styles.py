# -*- coding: utf-8 -*-
"""
Цветовая схема и стили приложения.
Пастельная палитра, голубой акцент, шрифт Times New Roman.
"""
import tkinter as tk
import tkinter.font as tkfont

# ─── Цвета ─────────────────────────────────────────────────────────────────
BG_MAIN       = "#F4F6F8"   # светло-серый (фон окна)
BG_PANEL      = "#E8ECF0"   # чуть темнее для боковых панелей
BG_CARD       = "#FFFFFF"   # белые карточки
BG_HEADER     = "#D6DDE6"   # заголовок навигации

ACCENT        = "#2A6496"   # тёмно-голубой акцент (кнопки, рамки)
ACCENT_LIGHT  = "#C8DCF0"   # светло-голубой (hover, отметка)
ACCENT_DARK   = "#1A3F5C"   # тёмнее для нажатых кнопок

WARN          = "#C0392B"   # красный для критических дефектов
WARN_LIGHT    = "#F5D5D2"

INFO          = "#2A6496"   # совпадает с акцентом
INFO_LIGHT    = "#D0E8F5"

OK            = "#1A6B3A"   # тёмно-зелёный для «лучший метод»
OK_LIGHT      = "#C8E6D4"

TEXT_MAIN     = "#1A1A1A"
TEXT_SEC      = "#555555"
TEXT_MUTED    = "#888888"

SEP_COLOR     = "#C0C8D0"
BORDER        = "#B0BAC4"

# ─── Типография ────────────────────────────────────────────────────────────
FONT_FAMILY   = "Times New Roman"

def make_fonts():
    return {
        "h1":      tkfont.Font(family=FONT_FAMILY, size=18, weight="bold"),
        "h2":      tkfont.Font(family=FONT_FAMILY, size=14, weight="bold"),
        "h3":      tkfont.Font(family=FONT_FAMILY, size=12, weight="bold"),
        "body":    tkfont.Font(family=FONT_FAMILY, size=11),
        "body_b":  tkfont.Font(family=FONT_FAMILY, size=11, weight="bold"),
        "small":   tkfont.Font(family=FONT_FAMILY, size=10),
        "caption": tkfont.Font(family=FONT_FAMILY, size=9, slant="italic"),
        "nav":     tkfont.Font(family=FONT_FAMILY, size=12, weight="bold"),
        "badge":   tkfont.Font(family=FONT_FAMILY, size=9, weight="bold"),
    }


def configure_ttk_styles(style):
    style.theme_use("clam")

    style.configure("TFrame",        background=BG_MAIN)
    style.configure("Card.TFrame",   background=BG_CARD,   relief="flat")
    style.configure("Panel.TFrame",  background=BG_PANEL)
    style.configure("Header.TFrame", background=BG_HEADER)

    style.configure("TLabel",        background=BG_MAIN,  foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 11))
    style.configure("Card.TLabel",   background=BG_CARD,  foreground=TEXT_MAIN)
    style.configure("H1.TLabel",     background=BG_MAIN,  foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 18, "bold"))
    style.configure("H2.TLabel",     background=BG_MAIN,  foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 14, "bold"))
    style.configure("H3.TLabel",     background=BG_CARD,  foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 12, "bold"))
    style.configure("Muted.TLabel",  background=BG_MAIN,  foreground=TEXT_MUTED,
                    font=(FONT_FAMILY, 10, "italic"))
    style.configure("Warn.TLabel",   background=WARN_LIGHT, foreground=WARN,
                    font=(FONT_FAMILY, 11, "bold"))
    style.configure("Ok.TLabel",     background=OK_LIGHT,  foreground=OK,
                    font=(FONT_FAMILY, 11, "bold"))

    style.configure("Accent.TButton",
                    background=ACCENT, foreground="#FFFFFF",
                    font=(FONT_FAMILY, 11, "bold"),
                    padding=(14, 6), relief="flat", borderwidth=0)
    style.map("Accent.TButton",
              background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
              foreground=[("active", "#FFFFFF")])

    style.configure("Nav.TButton",
                    background=BG_PANEL, foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 12, "bold"),
                    padding=(10, 10), relief="flat", borderwidth=0,
                    anchor="w")
    style.map("Nav.TButton",
              background=[("active", ACCENT_LIGHT), ("selected", ACCENT_LIGHT)],
              foreground=[("active", ACCENT), ("selected", ACCENT)])

    style.configure("Active.Nav.TButton",
                    background=ACCENT_LIGHT, foreground=ACCENT,
                    font=(FONT_FAMILY, 12, "bold"),
                    padding=(10, 10), relief="flat", borderwidth=0,
                    anchor="w")

    style.configure("TScrollbar",
                    background=BG_PANEL, troughcolor=BG_MAIN,
                    arrowcolor=TEXT_SEC)
    style.configure("TCheckbutton",
                    background=BG_MAIN, foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 11))
    style.configure("TRadiobutton",
                    background=BG_MAIN, foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 11))
    style.configure("TEntry",
                    fieldbackground=BG_CARD, foreground=TEXT_MAIN,
                    font=(FONT_FAMILY, 11))
    style.configure("Horizontal.TScale",
                    background=BG_MAIN, troughcolor=BG_PANEL,
                    slidercolor=ACCENT)
