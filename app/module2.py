# -*- coding: utf-8 -*-
"""
Модуль 2. Форма ввода данных о детали по шести исключающим критериям.
"""
import tkinter as tk
from tkinter import ttk

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
        self._on_result = on_result  # callback(params, available, scored, aux_info)
        self._build()

    def _build(self):
        # Заголовок
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 2", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Ввод данных о детали",
                  style="H1.TLabel").pack(anchor="w")

        info = InfoBox(
            self,
            "Ответьте на шесть вопросов о контролируемой детали. "
            "На основе ответов система исключит неприменимые методы НК "
            "и выдаст рекомендацию с балльной оценкой.",
            kind="info"
        )
        info.pack(fill="x", padx=24, pady=(4, 10))

        scroll = ScrollableFrame(self, bg=BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        inner = scroll.inner

        # ─── Переменные ───────────────────────────────────────────
        self._v_prod       = tk.StringVar(value="серийное")
        self._v_filler     = tk.BooleanVar(value=False)
        self._v_thick      = tk.DoubleVar(value=4.0)
        self._v_radius     = tk.BooleanVar(value=False)
        self._v_area       = tk.DoubleVar(value=2.0)
        self._v_min_def    = tk.DoubleVar(value=3.0)
        self._v_construct  = tk.StringVar(value="монолитная")

        # ─── Весовые коэффициенты ─────────────────────────────────
        self._weights = {f"w{i}": tk.IntVar(value=DEFAULT_WEIGHTS[f"w{i}"]) for i in range(1, 6)}

        fields = inner

        # 1. Тип производства
        self._card(fields, "1. Тип производства",
                   "КТ исключается при серийном производстве.") \
            ._add_radio(self._v_prod, [("Серийное", "серийное"),
                                       ("Опытное / единичное", "опытное")])

        # 2. Заполнитель
        self._card(fields, "2. Наличие заполнителя в зоне контроля",
                   "УЗК и РК исключаются при наличии сотового или пенопластового заполнителя.") \
            ._add_radio_bool(self._v_filler,
                             [("Нет заполнителя (монолитная конструкция)", False),
                              ("Есть заполнитель (сотовый, пенопластовый и т.п.)", True)])

        # 3. Толщина
        self._card(fields, "3. Толщина в зоне контроля (мм)",
                   "Импеданс и ширография исключаются при толщине более 3 мм.") \
            ._add_slider(self._v_thick, 0.5, 20.0, "мм", fmt="{:.1f}")

        # 4. Радиусные зоны
        self._card(fields, "4. Контроль радиусных и криволинейных зон",
                   "УЗК (контактный) и импеданс исключаются при необходимости контроля радиусных зон.") \
            ._add_radio_bool(self._v_radius,
                             [("Не требуется (плоские / слабоизогнутые участки)", False),
                              ("Требуется (радиусные переходы, криволинейные поверхности)", True)])

        # 5. Площадь
        self._card(fields, "5. Площадь контролируемой поверхности (м²)",
                   "Ширография, термография и РК исключаются при площади менее 1 м².") \
            ._add_slider(self._v_area, 0.1, 20.0, "м²", fmt="{:.1f}")

        # 6. Минимальный дефект
        self._card(fields, "6. Минимальный выявляемый дефект по НД (мм)",
                   "Импеданс, ширография и термография исключаются при требовании < 5 мм.") \
            ._add_slider(self._v_min_def, 1.0, 20.0, "мм", fmt="{:.0f}")

        # Тип конструкции (для подбора вспомогательного метода)
        self._card(fields, "Тип конструкции детали",
                   "Используется для выбора вспомогательного метода НК.") \
            ._add_radio(self._v_construct,
                        [("Монолитная", "монолитная"),
                         ("Трёхслойная (с заполнителем)", "трёхслойная")])

        # Весовые коэффициенты
        w_card = self._card(fields, "Весовые коэффициенты критериев оценки",
                            "Задайте приоритеты производства для балльной оценки (1–5).")
        w_names = ["Скорость", "Чувствительность", "Стоимость оборудования",
                   "Эксплуатационные расходы", "Безопасность"]
        for i, name in enumerate(w_names, start=1):
            w_card._add_weight_row(name, self._weights[f"w{i}"])

        # Кнопка
        btn_frame = tk.Frame(fields, bg=BG_MAIN)
        btn_frame.pack(fill="x", padx=8, pady=(8, 16))
        ttk.Button(btn_frame, text="Рассчитать и перейти к рекомендациям →",
                   style="Accent.TButton",
                   command=self._submit).pack(side="right")

    # ─── Вспомогательный строитель карточки ──────────────────────────────
    def _card(self, parent, title: str, hint: str = "") -> "_CardBuilder":
        return _CardBuilder(parent, title, hint, self._base_dir)

    def _submit(self):
        params = {
            "production":  self._v_prod.get(),
            "has_filler":  self._v_filler.get(),
            "thickness":   self._v_thick.get(),
            "has_radius":  self._v_radius.get(),
            "area":        self._v_area.get(),
            "min_defect":  self._v_min_def.get(),
            "construction":self._v_construct.get(),
        }
        weights = {k: v.get() for k, v in self._weights.items()}
        available, excl_log = apply_exclusion_criteria(params)
        scored = score_methods(available, weights)

        aux_method = None
        aux_reason = "Не определён"
        if scored:
            main_method = scored[0][0]
            aux_method, aux_reason = get_auxiliary(
                main_method, params["construction"], params["production"]
            )

        if self._on_result:
            self._on_result(params, available, scored, excl_log,
                            aux_method, aux_reason, weights)


class _CardBuilder:
    """Мини-строитель для секций формы."""

    def __init__(self, parent, title: str, hint: str, base_dir: str):
        self._frame = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid",
                               highlightthickness=1, highlightbackground=BORDER)
        self._frame.pack(fill="x", padx=8, pady=6)

        tk.Label(self._frame, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 anchor="w", padx=14).pack(fill="x", pady=(8, 0))
        if hint:
            tk.Label(self._frame, text=hint,
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10, "italic"),
                     anchor="w", padx=14,
                     wraplength=700).pack(fill="x")

        self._inner = tk.Frame(self._frame, bg=BG_CARD)
        self._inner.pack(fill="x", padx=14, pady=(0, 10))
        self._var = None

    def _add_radio(self, var, options):
        for text, val in options:
            tk.Radiobutton(
                self._inner, text=text, variable=var, value=val,
                bg=BG_CARD, fg=TEXT_MAIN,
                font=(FONT_FAMILY, 11),
                activebackground=ACCENT_LIGHT,
                selectcolor=ACCENT_LIGHT,
                cursor="hand2"
            ).pack(anchor="w", pady=2)
        return self

    def _add_radio_bool(self, var, options):
        for text, val in options:
            tk.Radiobutton(
                self._inner, text=text, variable=var, value=val,
                bg=BG_CARD, fg=TEXT_MAIN,
                font=(FONT_FAMILY, 11),
                activebackground=ACCENT_LIGHT,
                selectcolor=ACCENT_LIGHT,
                cursor="hand2"
            ).pack(anchor="w", pady=2)
        return self

    def _add_slider(self, var, from_, to_, unit, fmt="{:.1f}"):
        row = tk.Frame(self._inner, bg=BG_CARD)
        row.pack(fill="x")

        val_lbl = tk.Label(row, text=fmt.format(var.get()) + " " + unit,
                           bg=BG_CARD, fg=ACCENT,
                           font=(FONT_FAMILY, 12, "bold"),
                           width=8, anchor="w")
        val_lbl.pack(side="right")

        scale = tk.Scale(
            row, variable=var, from_=from_, to=to_,
            orient="horizontal", resolution=0.5 if "мм" in unit else 0.1,
            bg=BG_CARD, fg=TEXT_MAIN, troughcolor=BG_PANEL,
            activebackground=ACCENT, highlightthickness=0,
            sliderrelief="flat", bd=0, showvalue=False,
            font=(FONT_FAMILY, 10)
        )
        scale.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def on_change(v):
            val_lbl.config(text=fmt.format(float(v)) + " " + unit)

        scale.configure(command=on_change)

        # Подписи границ
        lbl_row = tk.Frame(self._inner, bg=BG_CARD)
        lbl_row.pack(fill="x")
        tk.Label(lbl_row, text=fmt.format(from_), bg=BG_CARD, fg=TEXT_MUTED,
                 font=(FONT_FAMILY, 9)).pack(side="left")
        tk.Label(lbl_row, text=fmt.format(to_), bg=BG_CARD, fg=TEXT_MUTED,
                 font=(FONT_FAMILY, 9)).pack(side="right")
        return self

    def _add_weight_row(self, name: str, var: tk.IntVar):
        row = tk.Frame(self._inner, bg=BG_CARD)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=name, bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 11), width=28, anchor="w").pack(side="left")

        val_lbl = tk.Label(row, text=str(var.get()),
                           bg=BG_CARD, fg=ACCENT,
                           font=(FONT_FAMILY, 11, "bold"), width=3)
        val_lbl.pack(side="right")

        scale = tk.Scale(
            row, variable=var, from_=1, to=5,
            orient="horizontal", resolution=1,
            bg=BG_CARD, fg=TEXT_MAIN, troughcolor=BG_PANEL,
            activebackground=ACCENT, highlightthickness=0,
            sliderrelief="flat", bd=0, showvalue=False,
            font=(FONT_FAMILY, 9), width=14
        )
        scale.pack(side="left", fill="x", expand=True, padx=(8, 4))
        scale.configure(command=lambda v: val_lbl.config(text=str(int(float(v)))))
        return self
