# -*- coding: utf-8 -*-
"""
Главный файл приложения.
Экспертная система выбора метода НК для углепластиковых деталей
авиационного назначения.
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# ─── Путь к ресурсам (корректный при запуске из EXE через PyInstaller) ─────
def resource_path(rel: str) -> str:
    """Возвращает абсолютный путь к ресурсу (работает и в EXE)."""
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

        # Иконка (если есть)
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
        # ── Верхняя полоска-шапка ───────────────────────────────────────
        top_bar = tk.Frame(self, bg=BG_HEADER, height=48)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="  Экспертная система выбора метода НК  •  углепластик  •  вакуумная инфузия",
            bg=BG_HEADER, fg=TEXT_MAIN,
            font=(FONT_FAMILY, 11),
            anchor="w"
        ).pack(side="left", padx=16, pady=10)

        tk.Label(
            top_bar,
            text="МАИ, 2026",
            bg=BG_HEADER, fg=TEXT_SEC,
            font=(FONT_FAMILY, 10, "italic")
        ).pack(side="right", padx=16)

        # Разделитель
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x", side="top")

        # ── Боковая навигация + контентная область ──────────────────────
        main_pane = tk.Frame(self, bg=BG_MAIN)
        main_pane.pack(fill="both", expand=True, side="top")

        nav = tk.Frame(main_pane, bg=BG_PANEL, width=230)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        content = tk.Frame(main_pane, bg=BG_MAIN)
        content.pack(side="left", fill="both", expand=True)

        # ── Создание страниц ─────────────────────────────────────────────
        self._m3 = Module3(content, BASE_DIR)
        self._m4 = Module4(content, BASE_DIR)
        self._m1 = Module1(content, BASE_DIR)
        self._m2 = Module2(content, BASE_DIR,
                           on_result=self._on_module2_result)

        self._pages = {
            "m1": self._m1,
            "m2": self._m2,
            "m3": self._m3,
            "m4": self._m4,
        }
        self._current_page = None

        # ── Навигационные кнопки ─────────────────────────────────────────
        tk.Label(nav, text="НАВИГАЦИЯ",
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 9, "bold"),
                 pady=14).pack(fill="x", padx=12)

        nav_items = [
            ("m1", "1", "Справочник дефектов ВИК",    "Фотографии и описания"),
            ("m2", "2", "Данные о детали",              "Шесть исключающих критериев"),
            ("m3", "3", "Рекомендации",                 "Методы и дефекты"),
            ("m4", "4", "Справочник дефектов",          "Интерактивный каталог"),
        ]

        self._nav_btns = {}
        for key, num, title, subtitle in nav_items:
            btn_frame = tk.Frame(nav, bg=BG_PANEL, cursor="hand2")
            btn_frame.pack(fill="x", pady=1)

            num_lbl = tk.Label(btn_frame,
                               text=num,
                               bg=ACCENT, fg="#FFFFFF",
                               font=(FONT_FAMILY, 10, "bold"),
                               width=3, height=2)
            num_lbl.pack(side="left", padx=(8, 0))

            txt_frame = tk.Frame(btn_frame, bg=BG_PANEL)
            txt_frame.pack(side="left", fill="both", expand=True, padx=8, pady=6)

            title_lbl = tk.Label(txt_frame, text=title,
                                 bg=BG_PANEL, fg=TEXT_MAIN,
                                 font=(FONT_FAMILY, 11, "bold"),
                                 anchor="w")
            title_lbl.pack(fill="x")
            sub_lbl = tk.Label(txt_frame, text=subtitle,
                               bg=BG_PANEL, fg=TEXT_SEC,
                               font=(FONT_FAMILY, 9),
                               anchor="w")
            sub_lbl.pack(fill="x")

            self._nav_btns[key] = (btn_frame, num_lbl, txt_frame, title_lbl, sub_lbl)

            for widget in [btn_frame, num_lbl, txt_frame, title_lbl, sub_lbl]:
                widget.bind("<Button-1>", lambda e, k=key: self._show_page(k))
                widget.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
                widget.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))

        # Вертикальный разделитель
        tk.Frame(nav, bg=BORDER, height=1).pack(fill="x", padx=12, pady=8)

        # Справка
        help_text = (
            "Алгоритм разработан согласно\n"
            "гл. 4 диссертации МАИ 2026.\n\n"
            "Источник: ГОСТ Р 54795-2011\n"
            "и НД по НК ПКМ."
        )
        tk.Label(nav, text=help_text,
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 9),
                 justify="left", wraplength=200,
                 padx=12, pady=4, anchor="w").pack(fill="x")

        # Показать первую страницу
        self._show_page("m1")

    def _show_page(self, key: str):
        if self._current_page:
            self._pages[self._current_page].pack_forget()
        self._pages[key].pack(fill="both", expand=True)
        self._current_page = key
        self._update_nav(key)

    def _update_nav(self, active_key: str):
        for key, (btn_frame, num_lbl, txt_frame, title_lbl, sub_lbl) in self._nav_btns.items():
            is_active = (key == active_key)
            bg = ACCENT_LIGHT if is_active else BG_PANEL
            fg = ACCENT if is_active else TEXT_MAIN
            fg_sub = ACCENT if is_active else TEXT_SEC
            num_bg = ACCENT_DARK if is_active else ACCENT

            btn_frame.configure(bg=bg)
            num_lbl.configure(bg=num_bg)
            txt_frame.configure(bg=bg)
            title_lbl.configure(bg=bg, fg=fg)
            sub_lbl.configure(bg=bg, fg=fg_sub)

    def _nav_hover(self, key: str, entering: bool):
        if key == self._current_page:
            return
        btn_frame, num_lbl, txt_frame, title_lbl, sub_lbl = self._nav_btns[key]
        bg = "#DDD8CD" if entering else BG_PANEL
        for w in [btn_frame, txt_frame, title_lbl, sub_lbl]:
            w.configure(bg=bg)

    def _on_module2_result(self, params, available, scored, excl_log,
                            aux_method, aux_reason, weights):
        self._m3.show_results(params, available, scored, excl_log,
                               aux_method, aux_reason, weights)
        self._show_page("m3")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
