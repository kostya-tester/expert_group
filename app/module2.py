# -*- coding: utf-8 -*-
"""
Модуль 2. Форма ввода данных о детали по шести исключающим критериям.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER, WARN, WARN_LIGHT,
    FONT_FAMILY
)
from app.widgets import ScrollableFrame, Divider, InfoBox, TagBadge
from app.data import apply_exclusion_criteria, score_methods, get_auxiliary, DEFAULT_WEIGHTS


class Module2(ttk.Frame):
    def __init__(self, parent, base_dir: str, on_result=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._on_result = on_result
        self._build()

    def _build(self):
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 2", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Ввод данных о детали",
                  style="H1.TLabel").pack(anchor="w")

        InfoBox(
            self,
            "Ответьте на шесть вопросов о контролируемой детали. "
            "На основе ответов система исключит неприменимые методы НК "
            "и выдаст рекомендацию с балльной оценкой.",
            kind="info"
        ).pack(fill="x", padx=24, pady=(4, 10))

        scroll = ScrollableFrame(self, bg=BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        inner = scroll.inner

        # ── Переменные ──────────────────────────────────────────────────────
        self._v_prod    = tk.StringVar(value="серийное")
        self._v_filler  = tk.BooleanVar(value=False)
        self._v_radius  = tk.BooleanVar(value=False)

        # Поля ручного ввода (вопросы 3, 5, 6)
        self._e_thick   = tk.StringVar(value="4,0")
        self._e_area    = tk.StringVar(value="2,0")
        self._e_min_def = tk.StringVar(value="3")

        # Весовые коэффициенты
        self._weights = {f"w{i}": tk.IntVar(value=DEFAULT_WEIGHTS[f"w{i}"]) for i in range(1, 6)}

        fields = inner

        # 1. Тип производства
        self._mk_card(fields, "1. Тип производства",
                      "КТ исключается при серийном производстве.")\
            ._radio(self._v_prod, [("Серийное", "серийное"),
                                   ("Опытное / единичное", "опытное")])

        # 2. Наличие заполнителя — определяет и тип конструкции
        self._mk_card(fields,
                      "2. Наличие заполнителя в зоне контроля",
                      "УЗК и РК исключаются при наличии заполнителя. "
                      "Ответ также определяет тип конструкции (монолитная / трёхслойная).")\
            ._radio_bool(self._v_filler,
                         [("Нет заполнителя — монолитная конструкция", False),
                          ("Есть заполнитель (сотовый, пенопластовый и т.п.) — трёхслойная конструкция", True)])

        # 3. Толщина — ручной ввод
        self._mk_card(fields,
                      "3. Толщина в зоне контроля (мм)",
                      "Импеданс и ширография исключаются при толщине более 3 мм. "
                      "Десятые доли вводятся через запятую (например: 2,5).")\
            ._entry(self._e_thick, "мм")

        # 4. Радиусные зоны
        self._mk_card(fields,
                      "4. Контроль радиусных и криволинейных зон",
                      "Контактный УЗК и импеданс исключаются при контроле радиусных зон.")\
            ._radio_bool(self._v_radius,
                         [("Не требуется (плоские / слабоизогнутые участки)", False),
                          ("Требуется (радиусные переходы, криволинейные поверхности)", True)])

        # 5. Площадь — ручной ввод
        self._mk_card(fields,
                      "5. Площадь контролируемой поверхности (м²)",
                      "Ширография, термография и РК исключаются при площади менее 1 м². "
                      "Десятые доли вводятся через запятую (например: 1,5).")\
            ._entry(self._e_area, "м²")

        # 6. Минимальный дефект — ручной ввод
        self._mk_card(fields,
                      "6. Минимальный выявляемый дефект по НД (мм)",
                      "Импеданс, ширография и термография исключаются при требовании < 5 мм. "
                      "Десятые доли вводятся через запятую (например: 3,0).")\
            ._entry(self._e_min_def, "мм")

        # Весовые коэффициенты
        w_card = self._mk_card(fields,
                               "Весовые коэффициенты критериев оценки",
                               "Задайте приоритеты для балльной оценки методов (1 — минимум, 5 — максимум).")
        w_names = ["Скорость контроля", "Чувствительность",
                   "Стоимость оборудования", "Эксплуатационные расходы", "Безопасность"]
        for i, name in enumerate(w_names, start=1):
            w_card._weight_row(name, self._weights[f"w{i}"])

        # Кнопка
        btn_frame = tk.Frame(fields, bg=BG_MAIN)
        btn_frame.pack(fill="x", padx=8, pady=(8, 16))
        tk.Button(btn_frame,
                  text="Определить методы НК  →",
                  bg=ACCENT, fg="#FFFFFF",
                  font=(FONT_FAMILY, 12, "bold"),
                  relief="flat", bd=0,
                  padx=20, pady=10,
                  cursor="hand2",
                  activebackground="#1A3F5C",
                  activeforeground="#FFFFFF",
                  command=self._submit).pack(side="right")

    # ── Вспомогательный строитель ────────────────────────────────────────
    def _mk_card(self, parent, title, hint=""):
        return _CardBuilder(parent, title, hint)

    def _parse_float(self, svar: tk.StringVar, field_name: str):
        """Парсит строку с запятой или точкой как разделителем."""
        raw = svar.get().strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода",
                f"Поле «{field_name}»: введите число.\n"
                f"Десятые доли через запятую, например: 2,5"
            )
            return None

    def _submit(self):
        thickness = self._parse_float(self._e_thick, "Толщина")
        if thickness is None:
            return
        area = self._parse_float(self._e_area, "Площадь")
        if area is None:
            return
        min_def = self._parse_float(self._e_min_def, "Минимальный дефект")
        if min_def is None:
            return

        # Тип конструкции выводится автоматически из наличия заполнителя
        construction = "трёхслойная" if self._v_filler.get() else "монолитная"

        params = {
            "production":   self._v_prod.get(),
            "has_filler":   self._v_filler.get(),
            "thickness":    thickness,
            "has_radius":   self._v_radius.get(),
            "area":         area,
            "min_defect":   min_def,
            "construction": construction,
        }
        weights = {k: v.get() for k, v in self._weights.items()}
        available, excl_log = apply_exclusion_criteria(params)
        scored = score_methods(available, weights)

        aux_method, aux_reason = None, "Не определён"
        if scored:
            aux_method, aux_reason = get_auxiliary(
                scored[0][0], construction, params["production"]
            )

        if self._on_result:
            self._on_result(params, available, scored, excl_log,
                            aux_method, aux_reason, weights)


class _CardBuilder:
    def __init__(self, parent, title: str, hint: str = ""):
        self._f = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid",
                           highlightthickness=1, highlightbackground=BORDER)
        self._f.pack(fill="x", padx=8, pady=6)
        tk.Label(self._f, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 anchor="w", padx=14).pack(fill="x", pady=(8, 0))
        if hint:
            tk.Label(self._f, text=hint,
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10, "italic"),
                     anchor="w", padx=14,
                     wraplength=720).pack(fill="x", pady=(2, 0))
        self._inner = tk.Frame(self._f, bg=BG_CARD)
        self._inner.pack(fill="x", padx=14, pady=(4, 10))

    def _radio(self, var, options):
        for text, val in options:
            tk.Radiobutton(self._inner, text=text, variable=var, value=val,
                           bg=BG_CARD, fg=TEXT_MAIN, font=(FONT_FAMILY, 11),
                           activebackground=ACCENT_LIGHT,
                           selectcolor=ACCENT_LIGHT,
                           cursor="hand2").pack(anchor="w", pady=2)
        return self

    def _radio_bool(self, var, options):
        for text, val in options:
            tk.Radiobutton(self._inner, text=text, variable=var, value=val,
                           bg=BG_CARD, fg=TEXT_MAIN, font=(FONT_FAMILY, 11),
                           activebackground=ACCENT_LIGHT,
                           selectcolor=ACCENT_LIGHT,
                           cursor="hand2").pack(anchor="w", pady=2)
        return self

    def _entry(self, svar: tk.StringVar, unit: str):
        row = tk.Frame(self._inner, bg=BG_CARD)
        row.pack(anchor="w")
        tk.Entry(row, textvariable=svar,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 13),
                 bd=1, relief="solid",
                 width=10,
                 justify="center").pack(side="left")
        tk.Label(row, text=" " + unit,
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left")
        return self

    def _weight_row(self, name: str, var: tk.IntVar):
        row = tk.Frame(self._inner, bg=BG_CARD)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=name, bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 11), width=28, anchor="w").pack(side="left")
        val_lbl = tk.Label(row, text=str(var.get()),
                           bg=BG_CARD, fg=ACCENT,
                           font=(FONT_FAMILY, 11, "bold"), width=3)
        val_lbl.pack(side="right")
        scale = tk.Scale(row, variable=var, from_=1, to=5,
                         orient="horizontal", resolution=1,
                         bg=BG_CARD, fg=TEXT_MAIN, troughcolor=BG_PANEL,
                         activebackground=ACCENT, highlightthickness=0,
                         sliderrelief="flat", bd=0, showvalue=False,
                         font=(FONT_FAMILY, 9), width=14)
        scale.pack(side="left", fill="x", expand=True, padx=(8, 4))
        scale.configure(command=lambda v: val_lbl.config(text=str(int(float(v)))))
        return self
