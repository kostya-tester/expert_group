# -*- coding: utf-8 -*-
"""
Модуль 3. Рекомендуемые методы НК с расчётом взвешенной суммы.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER,
    WARN, WARN_LIGHT, OK, OK_LIGHT, INFO, INFO_LIGHT,
    FONT_FAMILY
)
from app.widgets import ScrollableFrame, Divider, InfoBox, TagBadge
from app.data import NK_METHODS, METHOD_SCORES, get_defects_for_methods


class Module3(ttk.Frame):
    def __init__(self, parent, base_dir: str, on_go_module4=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._on_go_module4 = on_go_module4
        self._result_data = None
        self._build_empty()

    # ── Публичные методы ─────────────────────────────────────────────────
    def show_results(self, params, available, scored, excl_log,
                     aux_method, aux_reason, weights):
        self._result_data = dict(
            params=params, available=available, scored=scored,
            excl_log=excl_log, aux_method=aux_method,
            aux_reason=aux_reason, weights=weights
        )
        for w in self.winfo_children():
            w.destroy()
        self._build_results()

    def get_recommended_methods(self):
        """Возвращает (основной, вспомогательный) для передачи в модуль 4."""
        if not self._result_data:
            return [], None
        d = self._result_data
        scored = d["scored"]
        main_m = scored[0][0] if scored else None
        aux_m  = d["aux_method"]
        methods = [m for m in [main_m, aux_m] if m]
        return methods, main_m

    # ── Пустое состояние ─────────────────────────────────────────────────
    def _build_empty(self):
        for w in self.winfo_children():
            w.destroy()
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 3", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Рекомендуемые методы НК", style="H1.TLabel").pack(anchor="w")
        InfoBox(self, "Сначала заполните форму в Модуле 2 и нажмите «Определить методы НК».",
                kind="plain").pack(fill="x", padx=24, pady=(4, 12))
        tk.Label(self, text="Результаты расчёта появятся здесь.",
                 bg=BG_MAIN, fg=TEXT_MUTED,
                 font=(FONT_FAMILY, 12, "italic")).pack(expand=True)

    # ── Результаты ───────────────────────────────────────────────────────
    def _build_results(self):
        d      = self._result_data
        params = d["params"]
        scored = d["scored"]
        excl   = d["excl_log"]
        aux_m  = d["aux_method"]
        aux_r  = d["aux_reason"]
        w      = d["weights"]

        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 3", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Рекомендуемые методы НК", style="H1.TLabel").pack(anchor="w")

        scroll = ScrollableFrame(self, bg=BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        inner = scroll.inner

        self._params_block(inner, params)
        self._excl_block(inner, excl)

        if not d["available"]:
            InfoBox(inner,
                    "⚠  Все методы исключены по заданным критериям.\n"
                    "Пересмотрите требования или уточните задачу.",
                    kind="warn").pack(fill="x", padx=8, pady=8)
            return

        self._formula_block(inner, w)
        self._scores_block(inner, scored, w)

        if scored:
            main_m = scored[0][0]
            self._recommendation_block(inner, main_m, aux_m, aux_r)
            # Кнопка перехода в модуль 4
            self._goto_btn(inner, main_m, aux_m)

    # ── Параметры ────────────────────────────────────────────────────────
    def _params_block(self, parent, params):
        card = self._card(parent, "Введённые параметры детали")
        rows = [
            ("Тип производства",        params["production"].capitalize()),
            ("Тип конструкции",         params["construction"].capitalize()),
            ("Заполнитель",             "Да" if params["has_filler"] else "Нет"),
            ("Толщина в зоне контроля", f"{params['thickness']:.1f} мм"),
            ("Контроль радиусных зон",  "Требуется" if params["has_radius"] else "Не требуется"),
            ("Площадь контроля",        f"{params['area']:.1f} м²"),
            ("Минимальный дефект по НД",f"{params['min_defect']:.1f} мм"),
        ]
        for lbl, val in rows:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=lbl + ":", bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 11), width=30, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=BG_CARD, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left")

    # ── Исключения ───────────────────────────────────────────────────────
    def _excl_block(self, parent, excl_log):
        card = self._card(parent, "Применённые критерии исключения")
        any_excl = False
        for method, reasons in excl_log.items():
            if reasons:
                any_excl = True
                row = tk.Frame(card, bg=BG_CARD)
                row.pack(fill="x", padx=14, pady=2)
                tk.Label(row, text=method,
                         bg=WARN_LIGHT, fg=WARN,
                         font=(FONT_FAMILY, 11, "bold"),
                         padx=8).pack(side="left")
                tk.Label(row, text=" — " + "; ".join(reasons),
                         bg=BG_CARD, fg=TEXT_SEC,
                         font=(FONT_FAMILY, 10),
                         wraplength=500, anchor="w").pack(side="left", padx=6)
        if not any_excl:
            tk.Label(card, text="Ни один метод не был исключён.",
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 11, "italic"),
                     padx=14, anchor="w").pack(fill="x")

    # ── Формула ──────────────────────────────────────────────────────────
    def _formula_block(self, parent, weights):
        card = self._card(parent, "Расчёт по формуле взвешенной суммы")

        w_vals = [weights[f"w{i}"] for i in range(1, 6)]
        w_sum  = sum(w_vals)
        cnames = ["Скорость (c₁)", "Чувствительность (c₂)",
                  "Стоимость об. (c₃)", "Экспл. расходы (c₄)", "Безопасность (c₅)"]

        # Формула
        formula_txt = (
            "P = (w₁·c₁ + w₂·c₂ + w₃·c₃ + w₄·c₄ + w₅·c₅) / Σwᵢ"
        )
        tk.Label(card, text=formula_txt,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 padx=14, anchor="w").pack(fill="x")

        # Заданные веса
        w_row = tk.Frame(card, bg=BG_CARD)
        w_row.pack(fill="x", padx=14, pady=(4, 0))
        tk.Label(w_row, text="Веса:", bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 10)).pack(side="left")
        for i, (cn, wv) in enumerate(zip(cnames, w_vals), 1):
            tk.Label(w_row,
                     text=f"  w{i}={wv}",
                     bg=BG_CARD, fg=ACCENT,
                     font=(FONT_FAMILY, 10, "bold")).pack(side="left")
        tk.Label(w_row, text=f"  |  Σw = {w_sum}",
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 10)).pack(side="left")

        # Матрица баллов (шапка)
        tbl = tk.Frame(card, bg=BG_PANEL)
        tbl.pack(fill="x", padx=14, pady=(8, 4))

        cols = ["Метод"] + [f"c{i}" for i in range(1, 6)] + ["P"]
        widths = [22] + [6]*5 + [6]
        for col, ww in zip(cols, widths):
            tk.Label(tbl, text=col, bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10, "bold"),
                     width=ww, anchor="w",
                     padx=4, pady=3).pack(side="left")

        for method, score in sorted(
                METHOD_SCORES.items(), key=lambda x: -x[1].get("c1", 0)):
            s = METHOD_SCORES[method]
            p = sum(s[f"c{i}"] * w_vals[i-1] for i in range(1, 6)) / w_sum
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=1)
            vals = [NK_METHODS[method]["full_name"]] + \
                   [str(s[f"c{i}"]) for i in range(1, 6)] + \
                   [f"{p:.2f}"]
            for val, ww in zip(vals, widths):
                tk.Label(row, text=val, bg=BG_CARD, fg=TEXT_MAIN,
                         font=(FONT_FAMILY, 10),
                         width=ww, anchor="w", padx=4, pady=2).pack(side="left")

    # ── Балльная оценка доступных методов ────────────────────────────────
    def _scores_block(self, parent, scored, weights):
        card = self._card(parent, "Рейтинг доступных методов")

        hdr_row = tk.Frame(card, bg=BG_PANEL)
        hdr_row.pack(fill="x", padx=14, pady=(0, 4))
        for col, ww in [("Метод НК", 30), ("Балл P", 14), ("Рейтинг", 10)]:
            tk.Label(hdr_row, text=col, bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10, "bold"),
                     width=ww, anchor="w", padx=4, pady=4).pack(side="left")

        for rank, (method, score) in enumerate(scored, 1):
            is_best = (rank == 1)
            rbg = ACCENT_LIGHT if is_best else BG_CARD
            row = tk.Frame(card, bg=rbg,
                           highlightthickness=1 if is_best else 0,
                           highlightbackground=ACCENT)
            row.pack(fill="x", padx=14, pady=2)

            tk.Label(row, text=NK_METHODS[method]["full_name"],
                     bg=rbg, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 11, "bold" if is_best else "normal"),
                     width=30, anchor="w", padx=6, pady=6).pack(side="left")

            # Прогресс-бар
            bar = tk.Frame(row, bg=rbg, width=150, height=22)
            bar.pack(side="left", padx=4)
            bar.pack_propagate(False)
            fill_w = max(4, int(130 * score / 4.0))
            tk.Frame(bar, bg=ACCENT if is_best else "#A8C8E8",
                     width=fill_w, height=14).place(x=0, rely=0.5, anchor="w")
            tk.Label(bar, text=f"{score:.2f}",
                     bg=rbg, fg=ACCENT if is_best else TEXT_SEC,
                     font=(FONT_FAMILY, 10, "bold" if is_best else "normal")
                     ).place(relx=1.0, rely=0.5, anchor="e")

            rank_txt = "★ Лучший" if is_best else f"№{rank}"
            tk.Label(row, text=rank_txt,
                     bg=rbg, fg=ACCENT if is_best else TEXT_MUTED,
                     font=(FONT_FAMILY, 10, "bold" if is_best else "normal"),
                     width=10, anchor="w").pack(side="left", padx=4)

    # ── Рекомендация ─────────────────────────────────────────────────────
    def _recommendation_block(self, parent, main_m, aux_m, aux_reason):
        card = self._card(parent, "Рекомендация")

        # Основной метод
        mf = tk.Frame(card, bg=OK_LIGHT)
        mf.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(mf, text="Основной метод НК:",
                 bg=OK_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11), padx=12, pady=6).pack(side="left")
        tk.Label(mf, text=NK_METHODS[main_m]["full_name"],
                 bg=OK_LIGHT, fg=OK,
                 font=(FONT_FAMILY, 13, "bold"), padx=8, pady=6).pack(side="left")

        # Описание основного
        info_m = NK_METHODS[main_m]
        tk.Label(card, text=info_m["description"],
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11),
                 wraplength=660, justify="left", anchor="w",
                 padx=14).pack(fill="x", pady=(0, 4))

        # Дефекты основного
        dets = info_m.get("detects", [])
        if dets:
            dr = tk.Frame(card, bg=BG_CARD)
            dr.pack(fill="x", padx=14, pady=(0, 8))
            tk.Label(dr, text="Выявляет: ", bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 10)).pack(side="left")
            for dt in dets:
                TagBadge(dr, dt).pack(side="left", padx=(0, 4), pady=2)

        Divider(card).pack(fill="x", padx=14, pady=6)

        # Вспомогательный метод
        af = tk.Frame(card, bg=INFO_LIGHT)
        af.pack(fill="x", padx=14, pady=(0, 4))
        tk.Label(af, text="Вспомогательный метод НК:",
                 bg=INFO_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11), padx=12, pady=6).pack(side="left")
        if aux_m:
            tk.Label(af, text=NK_METHODS[aux_m]["full_name"],
                     bg=INFO_LIGHT, fg=INFO,
                     font=(FONT_FAMILY, 13, "bold"), padx=8, pady=6).pack(side="left")
            # Описание вспомогательного
            info_a = NK_METHODS[aux_m]
            tk.Label(card, text=info_a["description"],
                     bg=BG_CARD, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 11),
                     wraplength=660, justify="left", anchor="w",
                     padx=14).pack(fill="x", pady=(0, 4))
            dets_a = info_a.get("detects", [])
            if dets_a:
                dr2 = tk.Frame(card, bg=BG_CARD)
                dr2.pack(fill="x", padx=14, pady=(0, 4))
                tk.Label(dr2, text="Выявляет: ", bg=BG_CARD, fg=TEXT_SEC,
                         font=(FONT_FAMILY, 10)).pack(side="left")
                for dt in dets_a:
                    TagBadge(dr2, dt).pack(side="left", padx=(0, 4), pady=2)
        else:
            tk.Label(af, text="Не требуется",
                     bg=INFO_LIGHT, fg=INFO,
                     font=(FONT_FAMILY, 12, "italic"), padx=8, pady=6).pack(side="left")

        tk.Label(card, text=aux_reason,
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11, "italic"),
                 wraplength=660, justify="left", anchor="w",
                 padx=14).pack(fill="x", pady=(0, 10))

    # ── Кнопка → Модуль 4 ────────────────────────────────────────────────
    def _goto_btn(self, parent, main_m, aux_m):
        methods_str = NK_METHODS[main_m]["full_name"]
        if aux_m:
            methods_str += " + " + NK_METHODS[aux_m]["full_name"]

        bar = tk.Frame(parent, bg=ACCENT_LIGHT,
                       highlightthickness=1, highlightbackground=ACCENT)
        bar.pack(fill="x", padx=8, pady=(6, 8))

        tk.Label(bar,
                 text=f"Показать дефекты, выявляемые методами: {methods_str}",
                 bg=ACCENT_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11),
                 padx=14, pady=8).pack(side="left")

        tk.Button(bar,
                  text="Показать возможные дефекты  →",
                  bg=ACCENT, fg="#FFFFFF",
                  font=(FONT_FAMILY, 11, "bold"),
                  relief="flat", bd=0,
                  padx=16, pady=8,
                  cursor="hand2",
                  activebackground=ACCENT_DARK,
                  activeforeground="#FFFFFF",
                  command=self._on_go_module4 if self._on_go_module4 else lambda: None
                  ).pack(side="right", padx=14, pady=8)

    # ── Вспомогательный ──────────────────────────────────────────────────
    def _card(self, parent, title):
        card = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid",
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", padx=8, pady=6)
        tk.Label(card, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 anchor="w", padx=14, pady=8).pack(fill="x")
        Divider(card).pack(fill="x", padx=14, pady=(0, 6))
        return card
