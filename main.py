# -*- coding: utf-8 -*-
"""
Главный файл приложения.
Экспертная система выбора метода НК для углепластиковых деталей.
"""
import sys
import os
import tkinter as tk
from tkinter import ttk


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


BASE_DIR = resource_path(".")

from app.styles import (
    BG_MAIN, BG_PANEL, BG_HEADER, ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    TEXT_MAIN, TEXT_SEC, BORDER, FONT_FAMILY,
    configure_ttk_styles
)
from app.module1 import Module1
from app.module2 import Module2
from app.module3 import Module3
from app.module4 import Module4


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Экспертная система выбора метода НК — углепластик (МАИ, 2026)")
        self.geometry("1200x780")
        self.minsize(900, 600)
        self.configure(bg=BG_MAIN)

        icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self._style = ttk.Style(self)
        configure_ttk_styles(self._style)
        self._build_layout()

    def _build_layout(self):
        # ── Шапка ────────────────────────────────────────────────────────
        top_bar = tk.Frame(self, bg=BG_HEADER, height=48)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        tk.Label(top_bar,
                 text="  Экспертная система выбора метода НК  •  углепластик  •  вакуумная инфузия",
                 bg=BG_HEADER, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 11), anchor="w").pack(side="left", padx=16, pady=10)
        tk.Label(top_bar, text="МАИ, 2026",
                 bg=BG_HEADER, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 10, "italic")).pack(side="right", padx=16)

        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x", side="top")

        # ── Основная область ─────────────────────────────────────────────
        main_pane = tk.Frame(self, bg=BG_MAIN)
        main_pane.pack(fill="both", expand=True)

        nav = tk.Frame(main_pane, bg=BG_PANEL, width=230)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        content = tk.Frame(main_pane, bg=BG_MAIN)
        content.pack(side="left", fill="both", expand=True)

        # ── Создание страниц ─────────────────────────────────────────────
        self._m4 = Module4(content, BASE_DIR)
        self._m3 = Module3(content, BASE_DIR,
                           on_go_module4=self._go_module4)
        self._m2 = Module2(content, BASE_DIR,
                           on_result=self._on_module2_result)
        self._m1 = Module1(content, BASE_DIR,
                           on_go_module2=lambda: self._show_page("m2"))

        self._pages = {"m1": self._m1, "m2": self._m2,
                       "m3": self._m3, "m4": self._m4}
        self._current_page = None

        # ── Навигация ────────────────────────────────────────────────────
        tk.Label(nav, text="НАВИГАЦИЯ",
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 9, "bold"),
                 pady=14).pack(fill="x", padx=12)

        nav_items = [
            ("m1", "1", "Справочник дефектов ВИК",  "Фотографии и описания"),
            ("m2", "2", "Данные о детали",            "Шесть исключающих критериев"),
            ("m3", "3", "Рекомендации",               "Методы и расчёт"),
            ("m4", "4", "Справочник дефектов",        "Интерактивный каталог"),
        ]

        self._nav_btns = {}
        for key, num, title, subtitle in nav_items:
            bf = tk.Frame(nav, bg=BG_PANEL, cursor="hand2")
            bf.pack(fill="x", pady=1)
            nl = tk.Label(bf, text=num, bg=ACCENT, fg="#FFFFFF",
                          font=(FONT_FAMILY, 10, "bold"), width=3, height=2)
            nl.pack(side="left", padx=(8, 0))
            tf = tk.Frame(bf, bg=BG_PANEL)
            tf.pack(side="left", fill="both", expand=True, padx=8, pady=6)
            tl = tk.Label(tf, text=title, bg=BG_PANEL, fg=TEXT_MAIN,
                          font=(FONT_FAMILY, 11, "bold"), anchor="w")
            tl.pack(fill="x")
            sl = tk.Label(tf, text=subtitle, bg=BG_PANEL, fg=TEXT_SEC,
                          font=(FONT_FAMILY, 9), anchor="w")
            sl.pack(fill="x")
            self._nav_btns[key] = (bf, nl, tf, tl, sl)
            for w in [bf, nl, tf, tl, sl]:
                w.bind("<Button-1>", lambda e, k=key: self._show_page(k))
                w.bind("<Enter>",    lambda e, k=key: self._nav_hover(k, True))
                w.bind("<Leave>",    lambda e, k=key: self._nav_hover(k, False))

        tk.Frame(nav, bg=BORDER, height=1).pack(fill="x", padx=12, pady=8)
        tk.Label(nav,
                 text="Алгоритм по гл. 4 диссертации\nМАИ 2026.\n\nГОСТ Р 54795-2011\nНД по НК ПКМ.",
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 9),
                 justify="left", wraplength=200,
                 padx=12, pady=4, anchor="w").pack(fill="x")

        self._show_page("m1")

    # ── Навигация ─────────────────────────────────────────────────────────
    def _show_page(self, key: str):
        if self._current_page:
            self._pages[self._current_page].pack_forget()
        self._pages[key].pack(fill="both", expand=True)
        self._current_page = key
        self._update_nav(key)

    def _update_nav(self, active):
        for key, (bf, nl, tf, tl, sl) in self._nav_btns.items():
            on = (key == active)
            bg = ACCENT_LIGHT if on else BG_PANEL
            for w in [bf, tf, tl, sl]:
                w.configure(bg=bg)
            nl.configure(bg=ACCENT_DARK if on else ACCENT)
            tl.configure(fg=ACCENT if on else TEXT_MAIN)
            sl.configure(fg=ACCENT if on else TEXT_SEC)

    def _nav_hover(self, key, entering):
        if key == self._current_page:
            return
        bg = "#D8E4EE" if entering else BG_PANEL
        bf, nl, tf, tl, sl = self._nav_btns[key]
        for w in [bf, tf, tl, sl]:
            w.configure(bg=bg)

    # ── Колбэки ───────────────────────────────────────────────────────────
    def _on_module2_result(self, params, available, scored, excl_log,
                            aux_method, aux_reason, weights):
        self._m3.show_results(params, available, scored, excl_log,
                               aux_method, aux_reason, weights)
        self._show_page("m3")

    def _go_module4(self):
        methods, _ = self._m3.get_recommended_methods()
        self._m4.set_methods_filter(methods)
        self._show_page("m4")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
