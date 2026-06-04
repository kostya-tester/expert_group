# -*- coding: utf-8 -*-
"""
Модуль 3. Рекомендуемые методы и дефекты, которые они выявляют.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER,
    WARN, WARN_LIGHT, OK, OK_LIGHT, INFO, INFO_LIGHT,
    FONT_FAMILY
)
from app.widgets import ScrollableFrame, Divider, InfoBox, TagBadge
from app.data import NK_METHODS, get_defects_for_methods


class Module3(ttk.Frame):
    def __init__(self, parent, base_dir: str, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._result_data = None
        self._build_empty()

    def _build_empty(self):
        for w in self.winfo_children():
            w.destroy()

        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 3", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Рекомендуемые методы НК",
                  style="H1.TLabel").pack(anchor="w")

        InfoBox(
            self,
            "Сначала заполните форму ввода данных в Модуле 2 и нажмите «Рассчитать».",
            kind="plain"
        ).pack(fill="x", padx=24, pady=(4, 12))

        tk.Label(self, text="Результаты расчёта появятся здесь после заполнения формы.",
                 bg=BG_MAIN, fg=TEXT_MUTED,
                 font=(FONT_FAMILY, 12, "italic")).pack(expand=True)

    def show_results(self, params: dict, available: list, scored: list,
                     excl_log: dict, aux_method, aux_reason: str, weights: dict):
        self._result_data = {
            "params": params, "available": available, "scored": scored,
            "excl_log": excl_log, "aux_method": aux_method,
            "aux_reason": aux_reason, "weights": weights,
        }
        for w in self.winfo_children():
            w.destroy()
        self._build_results()

    def _build_results(self):
        d = self._result_data
        params = d["params"]
        available = d["available"]
        scored = d["scored"]
        excl_log = d["excl_log"]
        aux_method = d["aux_method"]
        aux_reason = d["aux_reason"]

        # Заголовок
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 3", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Рекомендуемые методы НК",
                  style="H1.TLabel").pack(anchor="w")

        scroll = ScrollableFrame(self, bg=BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        inner = scroll.inner

        # ── Введённые параметры ──────────────────────────────────
        self._params_block(inner, params)

        # ── Исключения ───────────────────────────────────────────
        self._excl_block(inner, excl_log)

        # ── Доступные методы ─────────────────────────────────────
        if not available:
            InfoBox(inner,
                    "⚠  Все методы исключены по заданным критериям.\n"
                    "Пересмотрите требования или уточните задачу.",
                    kind="warn").pack(fill="x", padx=8, pady=8)
            return

        # ── Результаты балльной оценки ───────────────────────────
        self._scores_block(inner, scored)

        # ── Рекомендация ─────────────────────────────────────────
        if scored:
            main_m = scored[0][0]
            self._recommendation_block(inner, main_m, aux_method, aux_reason)

        # ── Дефекты, выявляемые рекомендованной парой ───────────
        pair = ([scored[0][0]] if scored else [])
        if aux_method:
            pair.append(aux_method)
        if pair:
            self._detects_block(inner, pair)

    # ─── Параметры ────────────────────────────────────────────────────────
    def _params_block(self, parent, params):
        card = self._mk_card(parent, "Введённые параметры детали")
        rows = [
            ("Тип производства", params["production"].capitalize()),
            ("Заполнитель в зоне контроля", "Да" if params["has_filler"] else "Нет"),
            ("Толщина в зоне контроля", f"{params['thickness']:.1f} мм"),
            ("Контроль радиусных зон", "Требуется" if params["has_radius"] else "Не требуется"),
            ("Площадь контроля", f"{params['area']:.1f} м²"),
            ("Минимальный дефект по НД", f"{params['min_defect']:.0f} мм"),
            ("Тип конструкции", params["construction"].capitalize()),
        ]
        for lbl, val in rows:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=lbl + ":", bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 11), width=34, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=BG_CARD, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left")

    # ─── Исключения ───────────────────────────────────────────────────────
    def _excl_block(self, parent, excl_log):
        card = self._mk_card(parent, "Применённые критерии исключения")
        excluded_any = False
        for method, reasons in excl_log.items():
            if reasons:
                excluded_any = True
                row = tk.Frame(card, bg=BG_CARD)
                row.pack(fill="x", padx=14, pady=2)
                tk.Label(row, text=method,
                         bg=WARN_LIGHT, fg=WARN,
                         font=(FONT_FAMILY, 11, "bold"),
                         padx=8, pady=2).pack(side="left")
                tk.Label(row, text=" — " + "; ".join(reasons),
                         bg=BG_CARD, fg=TEXT_SEC,
                         font=(FONT_FAMILY, 10),
                         wraplength=500, anchor="w").pack(side="left", padx=6)

        if not excluded_any:
            tk.Label(card, text="Ни один метод не был исключён.",
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 11, "italic"),
                     padx=14, pady=4, anchor="w").pack(fill="x")

    # ─── Баллы ────────────────────────────────────────────────────────────
    def _scores_block(self, parent, scored):
        card = self._mk_card(parent, "Балльная оценка доступных методов")

        # Шапка таблицы
        hdr_row = tk.Frame(card, bg=BG_PANEL)
        hdr_row.pack(fill="x", padx=14, pady=(0, 4))
        for col, w in [("Метод НК", 28), ("Итоговый балл", 16), ("Рейтинг", 10)]:
            tk.Label(hdr_row, text=col, bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10, "bold"),
                     width=w, anchor="w", padx=4, pady=4).pack(side="left")

        max_score = scored[0][1] if scored else 1.0

        for rank, (method, score) in enumerate(scored, start=1):
            is_best = (rank == 1)
            row_bg = OK_LIGHT if is_best else BG_CARD

            row = tk.Frame(card, bg=row_bg,
                           highlightthickness=1 if is_best else 0,
                           highlightbackground=ACCENT if is_best else BORDER)
            row.pack(fill="x", padx=14, pady=2)

            # Метод
            tk.Label(row, text=NK_METHODS[method]["full_name"],
                     bg=row_bg, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 11, "bold" if is_best else "normal"),
                     width=28, anchor="w", padx=6, pady=6).pack(side="left")

            # Прогресс-бар
            bar_frame = tk.Frame(row, bg=row_bg, width=160, height=24)
            bar_frame.pack(side="left", padx=4)
            bar_frame.pack_propagate(False)
            fill_w = int(140 * score / 4.0)
            tk.Frame(bar_frame, bg=ACCENT if is_best else ACCENT_LIGHT,
                     width=fill_w, height=16).place(x=0, rely=0.5, anchor="w")
            tk.Label(bar_frame, text=f"{score:.2f}",
                     bg=row_bg, fg=ACCENT if is_best else TEXT_SEC,
                     font=(FONT_FAMILY, 11, "bold" if is_best else "normal")).place(
                relx=1.0, rely=0.5, anchor="e")

            # Ранг
            rank_txt = "★ Лучший" if is_best else f"№{rank}"
            tk.Label(row, text=rank_txt,
                     bg=row_bg, fg=OK if is_best else TEXT_MUTED,
                     font=(FONT_FAMILY, 10, "bold" if is_best else "normal"),
                     width=10, anchor="w").pack(side="left", padx=4)

    # ─── Рекомендация ─────────────────────────────────────────────────────
    def _recommendation_block(self, parent, main_m, aux_method, aux_reason):
        card = self._mk_card(parent, "Рекомендация")

        # Основной метод
        main_f = tk.Frame(card, bg=OK_LIGHT, bd=0)
        main_f.pack(fill="x", padx=14, pady=(0, 8))
        tk.Label(main_f, text="Основной метод НК:",
                 bg=OK_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11), padx=12, pady=4).pack(side="left")
        tk.Label(main_f, text=NK_METHODS[main_m]["full_name"],
                 bg=OK_LIGHT, fg=OK,
                 font=(FONT_FAMILY, 13, "bold"),
                 padx=8, pady=4).pack(side="left")

        # Описание основного метода
        info = NK_METHODS[main_m]
        tk.Label(card, text=info["description"],
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11),
                 wraplength=660, justify="left", anchor="w",
                 padx=14, pady=(0, 4)).pack(fill="x")

        # Дефекты основного метода
        dets = info.get("detects", [])
        if dets:
            det_row = tk.Frame(card, bg=BG_CARD)
            det_row.pack(fill="x", padx=14, pady=(0, 8))
            tk.Label(det_row, text="Выявляет: ",
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10)).pack(side="left")
            for d in dets:
                TagBadge(det_row, d).pack(side="left", padx=(0, 4), pady=2)

        Divider(card).pack(fill="x", padx=14, pady=6)

        # Вспомогательный метод
        aux_f = tk.Frame(card, bg=INFO_LIGHT, bd=0)
        aux_f.pack(fill="x", padx=14, pady=(0, 8))
        tk.Label(aux_f, text="Вспомогательный метод НК:",
                 bg=INFO_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11), padx=12, pady=4).pack(side="left")
        if aux_method:
            tk.Label(aux_f, text=NK_METHODS[aux_method]["full_name"],
                     bg=INFO_LIGHT, fg=INFO,
                     font=(FONT_FAMILY, 13, "bold"), padx=8, pady=4).pack(side="left")
        else:
            tk.Label(aux_f, text="Не требуется",
                     bg=INFO_LIGHT, fg=INFO,
                     font=(FONT_FAMILY, 12, "italic"), padx=8, pady=4).pack(side="left")

        tk.Label(card, text=aux_reason,
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11, "italic"),
                 wraplength=660, justify="left", anchor="w",
                 padx=14, pady=(0, 10)).pack(fill="x")

    # ─── Выявляемые дефекты ───────────────────────────────────────────────
    def _detects_block(self, parent, methods: list):
        defects = get_defects_for_methods(methods)
        if not defects:
            return
        card = self._mk_card(parent, f"Дефекты, выявляемые методами: {', '.join(methods)}")
        for d in defects:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=3)
            tk.Label(row, text="•", bg=BG_CARD, fg=ACCENT,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", anchor="n")
            info_col = tk.Frame(row, bg=BG_CARD)
            info_col.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(info_col, text=d["name"],
                     bg=BG_CARD, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 11, "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(info_col, text=d.get("short", ""),
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10),
                     anchor="w", wraplength=550).pack(fill="x")

    # ─── Вспомогательный строитель ───────────────────────────────────────
    def _mk_card(self, parent, title: str) -> tk.Frame:
        card = tk.Frame(parent, bg=BG_CARD,
                        bd=1, relief="solid",
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", padx=8, pady=6)
        tk.Label(card, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 anchor="w", padx=14, pady=8).pack(fill="x")
        Divider(card).pack(fill="x", padx=14, pady=(0, 6))
        return card
